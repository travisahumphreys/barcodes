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

### Laser Workstation (Python + Typst)
```bash
cd laser/
python generate.py                  # Generates output/laser.pdf
python generate.py --clean          # Clean barcodes directory first
```

### Routing Workstation (Python + Typst)
```bash
cd routing/
python generate.py                  # Generates output/router_barcodes.pdf + update form
python generate.py --clean          # Clean barcodes directory first
```

## System Dependencies

Required tools (no package.json/requirements.txt - all system-level):
- `zint` - Barcode generator (CODE128, type 20)
- `typst` - Document compiler for PDF layout
- `python3` - For all three subsystems

## Architecture

**Three independent subsystems**, all following the same logic delegation pattern:

| Subsystem | Tech Stack | Data File | Output |
|-----------|------------|-----------|--------|
| connector-prep | Python + Typst | Multiple CSVs | Per-bench PDFs |
| laser | Python + Typst | part_lots.csv + pou_map.csv | Single PDF |
| routing | Python + Typst | pou_map.csv | PDF + update form |

### Connector-Prep Architecture (Most Complex)

Logic delegation pattern: Python handles only barcode PNG generation; all data processing and layout logic lives in Typst.

- `generate.py` - Loads CSVs, generates PNGs via zint, invokes Typst with bench parameter
- `conn_prep.typ` - Processes CSV data, builds lookup tables, layouts barcode cards in grid
- `part_numbers.csv` - Maps friendly names to MIL-SPEC part numbers
- `bench_lots.csv` - Lot numbers per bench per part
- `conn_prep_pou.csv` - Bill of materials with bundles and quantities

### Laser/Routing Architecture

Same logic delegation pattern: `generate.py` produces barcode PNGs via zint and invokes Typst; a static `.typ` file (`laser.typ` / `routing.typ`) reads the CSVs and handles all layout. Routing additionally derives `update_form.csv` and compiles `update_form.typ`.

## Barcode Data Format

Barcodes encode scanner control sequences:
```
{PartNumber}\t{LotNumber}\t{Quantity}\t\t\t\t{EndMarkers}
```

Control characters are bench-specific (connector-prep) and must remain in Python - they cannot be generated in Typst.

## Key Constraints

- CSV files are the source of truth for all part data
- Connector-prep supports 4 benches with different lot numbers and control sequences
- Generated PDFs are gitignored
- No automated testing - verify PDF output manually
