# Feasibility Study: Web UI for Lot Number Updates & Bundle Management

## Executive Summary

A web UI is **feasible and recommended**. The core generation pipeline (zint + Typst) must run server-side, but the data editing surface is simple enough that a lightweight web app can expose it to non-technical users with minimal risk.

The recommended approach is a **Python web app (Flask or FastAPI)** that wraps the existing generation scripts, provides spreadsheet-like editing for each subsystem's data files, and serves the generated PDFs for download.

---

## Current System: What Users Need to Edit

### Connector-Prep (most complex)

Users interact with three CSVs:

| File | Purpose | Shape | Edit Frequency |
|------|---------|-------|----------------|
| `bench_lots.csv` | Lot numbers per bench per part | 5 benches x 9 parts = 45 rows | **Frequent** — lot changes are the primary use case |
| `pou_map.csv` | Bundle-to-part quantity matrix | 311 bundles x 9 part columns | **Occasional** — new assemblies added |
| `part_numbers.csv` | Friendly name to MIL-SPEC mapping | 9 rows | **Rare** — only when new part types introduced |

Key complexity: lot numbers are **bench-specific** — the same part can have different lot numbers on different benches.

### Laser

| File | Purpose | Shape | Edit Frequency |
|------|---------|-------|----------------|
| `part_lots.csv` | Part name → (part number, lot number) | 9 rows | **Frequent** — lot updates |
| `pou_map.csv` | Bundle-to-part quantity matrix | 34 bundles x 9 part columns | **Occasional** — new bundles |

Simpler than connector-prep: no bench dimension, single lot per part.

### Routing

| File | Purpose | Shape | Edit Frequency |
|------|---------|-------|----------------|
| `Router-pou.csv` | Denormalized: one row per (bundle, part) combo | 46 rows, 5 columns | **Both** — lot updates and new bundles |

Simplest data model but most manual to edit (lot numbers repeated across rows for the same part).

---

## Proposed Architecture

```
┌─────────────────────────────────────────────────┐
│                   Browser UI                     │
│  ┌───────────┐ ┌───────────┐ ┌───────────────┐  │
│  │ Conn-Prep │ │   Laser   │ │   Routing     │  │
│  │  Tab/Page │ │  Tab/Page │ │   Tab/Page    │  │
│  └─────┬─────┘ └─────┬─────┘ └──────┬────────┘  │
└────────┼──────────────┼──────────────┼───────────┘
         │              │              │
         ▼              ▼              ▼
┌─────────────────────────────────────────────────┐
│              Python Web Server                   │
│         (Flask or FastAPI, single app)           │
│                                                  │
│  • Reads/writes CSVs as the data store           │
│  • Validates input before writing                │
│  • Calls existing generate.py / bash scripts     │
│  • Serves generated PDFs for download            │
└──────────────────┬──────────────────────────────┘
                   │
         ┌─────────┴─────────┐
         │  System Tools     │
         │  • zint (barcode) │
         │  • typst (PDF)    │
         └───────────────────┘
```

### Why Python + Flask/FastAPI

- **Already in the stack** — connector-prep uses Python; no new runtime dependency
- **Thin wrapper** — the existing `generate.py` and bash scripts can be called directly via `subprocess`
- **Simple deployment** — single process, no database, CSVs remain the source of truth
- **Low learning curve** — Flask is ~100 lines for this kind of CRUD app

### Why NOT a client-side / static site approach

- `zint` and `typst` are CLI tools that must run on the server
- Barcode data contains precise control character encoding (`\t`, `\r`) that must be preserved exactly — this logic should not be reimplemented in JavaScript
- PDF generation is inherently server-side

---

## UI Design Per Subsystem

### 1. Connector-Prep: Lot Number Updates

**Interface**: A grid/table showing parts as rows and benches as columns, with lot numbers as editable cells.

```
                 Bench 1              Bench 2              Bench 3           ...
Black       [BASN115289 098536] [BASN115289 097810] [BASN115289 097810]
Red         [DXN116839 315470 ] [DXN116839 315470 ] [DXN116839 212302 ]
Blue        [DXN116386 226836 ] [DXN116386 226836 ] [DXN116386 226836 ]
...

                                    [ Save & Generate PDFs ]
```

- Grid layout mirrors `bench_lots.csv` structure directly
- Each cell is a text input pre-filled with the current lot number
- "Save & Generate" writes the CSV and runs generation for affected benches
- Color-code cells that changed since last generation

### 2. Connector-Prep: Bundle Management

**Interface**: Spreadsheet-like view of `pou_map.csv` — bundle ID in the first column, part quantities in subsequent columns.

```
Bundle    | Black | Red | Blue | Yellow | Clear | Contact | BMS | BlackBMS | Label
----------|-------|-----|------|--------|-------|---------|-----|----------|------
3755-300  | 203   | 78  | 23   | 6      |       |         | 1   |          |
3755-304  | 209   | 47  | 8    |        |       |         | 6   |          |
[+ Add Bundle]

                                    [ Save & Generate PDFs ]
```

- Existing bundles editable inline
- "Add Bundle" row at bottom with blank fields
- Empty cells = part not used (matches CSV semantics)
- Validate: bundle ID format (XXXX-YYY), quantities are positive integers or blank

### 3. Laser: Lot Number Updates

**Interface**: Simple key-value list (9 parts).

```
Part Name    Part Number         Lot Number
TEDLAR       BACT19C-T1S2       [VC25118126 147632    ]
1_16         M23053/5-102-4     [DXN104725 153035     ]
3_32         M23053/5-103-4     [DXN116269 185742     ]
...

                          [ Save & Generate PDF ]
```

- Read-only part name/number columns (from `part_lots.csv`)
- Editable lot number column only
- Single "Save & Generate" button regenerates the full laser PDF

### 4. Laser: Bundle Management

**Interface**: Same spreadsheet pattern as connector-prep but simpler (no bench dimension).

```
BUNDLE | TEDLAR | 1_16 | 3_32 | 1_8 | 3_16 | 1_4 | 3_8 | 1_2 | BUNDLE-ID
-------|--------|------|------|-----|------|-----|-----|-----|----------
2031   | 1      |      |      |     | 1    |     |     | 1   |
2401   | 1      |      |      |     |      |     |     | 1   | 1
[+ Add Bundle]
```

### 5. Routing: Combined View

**Interface**: Two-panel layout since routing uses a denormalized CSV.

**Panel A — Lot Number Updates** (deduplicated part list):
```
Part Name              Part Number           Lot Number
#10 Red Lug            bact12AC3             [BASN115265 097825    ]
#10 Blue Lug           bact12AC8             [BASN115270 097810    ]
Red Contact            s280w555-920          [DXN116156 149085     ]
...
                                     [ Update Lots ]
```

Updating a lot number here propagates to ALL rows in `Router-pou.csv` that share that part number.

**Panel B — Bundle Contents** (grouped by bundle):
```
Bundle: 6230
  Part Name          | Qty
  #10 Red Lug        | 5
  #10 Blue Lug       | 3
  ...
  [+ Add Part to Bundle]

Bundle: 5104
  ...

[+ Add New Bundle]
                                     [ Save & Generate PDFs ]
```

---

## Technical Implementation Plan

### Phase 1: Core Web App (Minimum Viable)
**Scope**: Lot number editing + PDF generation for all 3 subsystems.

```
web/
├── app.py              # Flask app, routes, CSV read/write
├── templates/
│   ├── base.html       # Shared layout, navigation
│   ├── connector.html  # Bench x Part lot grid
│   ├── laser.html      # Simple lot list
│   └── routing.html    # Two-panel lot + bundle view
├── static/
│   └── style.css       # Minimal styling
└── requirements.txt    # flask (sole dependency)
```

**Estimated scope**: ~500-800 lines of Python, ~300 lines of HTML/CSS.

**Key implementation details**:
- CSV files remain in their current locations — the web app reads/writes them in place
- Generation calls the existing scripts via `subprocess`:
  - `python connector-prep/generate.py --bench {N}`
  - `python laser/generate.py`
  - `bash routing/barcode_gen_router.sh`
- Generated PDFs served via Flask's `send_file()`
- No database — CSVs are the single source of truth
- No authentication in Phase 1 (assumes local network / trusted environment)

### Phase 2: Bundle Management
**Scope**: Add/edit/remove bundles in pou_map CSVs.

- Add spreadsheet-style editing for `pou_map.csv` (connector-prep, laser)
- Add row-based editing for `Router-pou.csv` (routing)
- Input validation (bundle ID format, integer quantities, required fields)

### Phase 3: Safety & Polish
**Scope**: Protect against data loss and improve UX.

- **Backup on save**: Auto-copy CSV to `backups/{timestamp}/` before overwriting
- **Undo**: Keep last N versions of each CSV, allow rollback
- **Validation warnings**: Flag potential issues (lot number format, duplicate bundles)
- **Generation status**: Show spinner during PDF generation, display errors inline
- **PDF preview**: Embed generated PDF in an iframe for immediate review before download
- **Optional auth**: Basic password protection if exposed beyond local network

---

## Risk Assessment

### Low Risk
| Concern | Mitigation |
|---------|------------|
| User enters invalid lot number format | Warn but allow — lot formats vary, hard to validate strictly |
| PDF generation fails | Show error from zint/typst output, CSV is unchanged |
| Concurrent edits | Unlikely with small user base; file locking in Phase 3 if needed |

### Medium Risk
| Concern | Mitigation |
|---------|------------|
| User accidentally clears a lot number | Pre-save backup + undo capability (Phase 3) |
| Control character encoding breaks | **Never expose control chars in UI** — they stay in Python/bash scripts, users only edit lot numbers and quantities |
| CSV corruption from malformed input | Validate/sanitize on write: strip leading/trailing whitespace, reject commas in fields, escape quotes |

### Non-Risks
| Concern | Why it's not a problem |
|---------|----------------------|
| Barcode encoding correctness | Control characters are hardcoded in scripts, not user-editable |
| Typst template changes | Templates are developer-managed, not exposed in UI |
| System dependency management | zint and typst are already installed on the generation machine |

---

## Deployment Options

### Option A: Run Locally (Simplest)
```bash
cd barcodes/web
pip install flask
python app.py
# → http://localhost:5000
```
- Zero infrastructure
- User opens browser on the same machine that generates barcodes
- Best for: single workstation, one operator

### Option B: Local Network Server
- Same app, bind to `0.0.0.0:5000`
- Accessible from any machine on the shop floor network
- Add basic auth (Phase 3)
- Best for: multiple operators, shared printer

### Option C: Containerized (Docker)
```dockerfile
FROM python:3.11-slim
RUN apt-get update && apt-get install -y zint typst
COPY . /app
WORKDIR /app
RUN pip install flask
CMD ["python", "web/app.py"]
```
- Reproducible environment
- Easy to move between machines
- Best for: IT-managed deployment

---

## Alternatives Considered

### Spreadsheet (Google Sheets / Excel) + manual script run
- **Pro**: Users already know spreadsheets
- **Con**: Still requires someone to run the scripts manually, error-prone file transfer, no validation
- **Verdict**: Solves half the problem — lot editing but not generation

### Electron / desktop app
- **Pro**: Native feel, offline capable
- **Con**: Heavier to build and distribute, still needs zint/typst installed
- **Verdict**: Overkill — a browser tab is simpler

### Typst-native web compilation (typst.ts)
- **Pro**: Could compile PDFs in-browser
- **Con**: Still need zint for barcode PNGs (no browser equivalent with identical output), control character encoding is tricky client-side
- **Verdict**: Partial solution, adds complexity without eliminating server dependency

---

## Recommendation

**Build Phase 1 (lot number editing + PDF generation) as a Flask app.** This covers the most frequent user task (lot updates) with the least effort. The existing scripts are called unchanged — the web app is purely a UI layer over CSV editing.

Estimated effort:
- Phase 1 (lot editing + generation): Small — single file Flask app with HTML templates
- Phase 2 (bundle management): Small-medium — spreadsheet-style editing adds complexity
- Phase 3 (safety/polish): Medium — backup system, validation, auth

The key insight is that **the hard parts (barcode encoding, control characters, PDF layout) are already solved** in the existing scripts. The web UI only needs to handle the easy part: letting users type lot numbers into labeled fields and click "Generate."
