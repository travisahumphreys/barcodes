# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Multi-workstation barcode generation system for manufacturing/assembly operations. Three independent subsystems generate barcodes with scanner-specific control character encoding.

## Commands

### Connector Prep (Python + Typst)
```bash
cd connector-prep/
python generate.py --bench 1        # Generate for single bench (1-4)
python generate.py --bench all      # Generate for all benches
python generate.py --list-benches   # List configured benches
```

### Laser Workstation (Bash + Typst)
```bash
cd laser/
bash barcode_gen_pdf.sh             # Generates laser_barcodes.pdf
```

### Routing Workstation (Bash + Typst)
```bash
cd routing/
bash barcode_gen_router.sh          # Generates router_barcodes.pdf + update form
```

## System Dependencies

Required tools (no package.json/requirements.txt - all system-level):
- `zint` - Barcode generator (CODE128, type 20)
- `typst` - Document compiler for PDF layout
- `python3` - For connector-prep subsystem only

## Architecture

**Three independent subsystems**, each with different implementation approaches:

| Subsystem | Tech Stack | Data File | Output |
|-----------|------------|-----------|--------|
| connector-prep | Python + Typst | Multiple CSVs | Per-bench PDFs |
| laser | Bash + Typst | Laser-pou.csv | Single PDF |
| routing | Bash + Typst | Router-pou.csv | PDF + update form |

### Connector-Prep Architecture (Most Complex)

Logic delegation pattern: Python handles only barcode PNG generation; all data processing and layout logic lives in Typst.

- `generate.py` - Loads CSVs, generates PNGs via zint, invokes Typst with bench parameter
- `conn_prep.typ` - Processes CSV data, builds lookup tables, layouts barcode cards in grid
- `part_numbers.csv` - Maps friendly names to MIL-SPEC part numbers
- `bench_lots.csv` - Lot numbers per bench per part
- `conn_prep_pou.csv` - Bill of materials with bundles and quantities

### Laser/Routing Architecture

Bash scripts dynamically generate Typst source, then compile to PDF. Scripts auto-commit archives with timestamps to git.

## Barcode Data Format

Barcodes encode scanner control sequences:
```
{PartNumber}\t{LotNumber}\t{Quantity}\t\t\t\t{EndMarkers}
```

Control characters are bench-specific (connector-prep) and must remain in Python - they cannot be generated in Typst.

## Key Constraints

- CSV files are the source of truth for all part data
- Connector-prep supports 4 benches with different lot numbers and control sequences
- Generated PDFs are gitignored; archives are committed with timestamps
- No automated testing - verify PDF output manually
