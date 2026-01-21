# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Generates Code 128 barcode PDFs for Connector Prep workbenches. Joins three data sources (part numbers, lot numbers, assembly quantities) to produce barcodes that auto-fill multi-field forms when scanned.

## Commands

```bash
# Generate PDFs for a single bench
python generate.py --bench 1

# Generate PDFs for all benches (1-4)
python generate.py --bench all

# List configured benches
python generate.py --list-benches
```

## Dependencies

- Python 3.6+
- `zint` (barcode generator, uses `-b 20` for Code 128)
- `typst` (document compiler)

## Data Files

| File | Purpose |
|------|---------|
| `part_numbers.csv` | Maps friendly names (Black, Red, Blue) to part numbers (MS27488-22-2) |
| `bench_lots.csv` | Lot numbers per bench per part (Bench, Name, LotNumber) |
| `conn_prep_pou.csv` | Assembly matrix - rows are bundles, columns are part quantities |

Every part name in `conn_prep_pou.csv` columns must have entries in both `part_numbers.csv` and `bench_lots.csv` for each bench.

## Output

- PDFs: `output/conn_prep_bench{N}.pdf`
- Barcodes: `barcodes/bench{N}/{bundle}_{index}.png`

## Barcode Data Format

Each barcode encodes: `{PartNumber}{post_part}{LotNumber}{post_lot}{Quantity}{post_qty}`

Control characters are configurable per-bench via `BENCH_CONTROLS` dict in `generate.py` (lines 30-35).

## Architecture

`generate.py` runs a single-pass pipeline:
1. Load all three CSVs into memory
2. For each assembly row, yield barcode records for non-empty quantity cells
3. Generate PNG barcodes with zint (`generate_barcodes()`)
4. Group by assembly prefix, generate Typst source (`generate_typst_source()`)
5. Compile to PDF with typst
