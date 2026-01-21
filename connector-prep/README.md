# Connector Prep Barcode Generator

Generates barcode PDFs for Connector Prep workbenches.

## Requirements

- Python 3.6+
- zint (barcode generator)
- typst (document compiler)

## Files

| File | Purpose | Update Frequency |
|------|---------|------------------|
| `part_numbers.csv` | Maps friendly names to part numbers | Rarely |
| `bench_lots.csv` | Lot numbers per bench per part | Frequently |
| `conn_prep_pou.csv` | Assembly matrix (quantities) | When assemblies change |
| `generate.py` | Main script | Never (unless adding features) |

## Usage

```bash
# Generate PDFs for a single bench
python generate.py --bench 1

# Generate PDFs for all benches
python generate.py --bench all

# List configured benches
python generate.py --list-benches
```

## Updating Lot Numbers

Edit `bench_lots.csv`. Each row specifies a bench, part name, and lot number:

```
Bench,Name,LotNumber
1,Black,DXN123456
1,Red,DXN234567
2,Black,DXN345678
...
```

Every part name used in `conn_prep_pou.csv` must have a corresponding entry
for each bench in `bench_lots.csv`, or the script will error.

## Updating Part Numbers

Edit `part_numbers.csv` if a part number changes:

```
Name,PartNumber
Black,MS27488-22-2
Red,MS27488-20-2
...
```

## Scanner Control Characters

Each bench can have different control character sequences embedded in barcodes
to match scanner configuration. Edit the `BENCH_CONTROLS` dict in `generate.py`:

```python
BENCH_CONTROLS = {
    1: {"post_part": "\t\r", "post_lot": "\t", "post_qty": "\t\t\t\t\r\t\r"},
    2: {"post_part": "\t\r", "post_lot": "\t", "post_qty": "\t\t\t\t\r\t\r"},
    ...
}
```

## Output

PDFs are generated in `output/`:
- `conn_prep_bench1.pdf`
- `conn_prep_bench2.pdf`
- `conn_prep_bench3.pdf`
- `conn_prep_bench4.pdf`

Intermediate barcode images are stored in `barcodes/bench{N}/`.

## Barcode Data Format

Each barcode encodes:
```
{PartNumber}{post_part}{LotNumber}{post_lot}{Quantity}{post_qty}
```

With default control characters:
```
MS27488-22-2[TAB][RETURN]DXN123456[TAB]5[TAB][TAB][TAB][TAB][RETURN][TAB][RETURN]
```

This auto-fills the multi-field form when scanned.
