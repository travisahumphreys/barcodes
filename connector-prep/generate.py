#!/usr/bin/env python3
"""
Connector Prep Barcode Generator (Refactored)

Minimal Python script that ONLY:
1. Generates barcode PNG files with zint
2. Invokes Typst to compile the PDF

All data processing, layout, and document logic lives in conn_prep.typ

Usage:
    python generate.py --bench 1        # Generate for bench 1 only
    python generate.py --bench all      # Generate for all benches
    python generate.py --list-benches   # Show configured benches
"""

import argparse
import csv
import subprocess
import sys
from pathlib import Path

# =============================================================================
# CONFIGURATION
# =============================================================================

# Control characters for barcode data, per bench.
# These MUST stay in Python - they get embedded in the barcode image.
BENCH_CONTROLS = {
    1: {"post_part": "\t\r", "post_lot": "\t", "post_qty": "\t\t\t\t\r\t\r"},
    2: {"post_part": "\t\r", "post_lot": "\t", "post_qty": "\t\t\t\t\r\t\r"},
    3: {"post_part": "\t\r", "post_lot": "\t", "post_qty": "\t\t\t\t\r\t\r"},
    4: {"post_part": "\t\r", "post_lot": "\t", "post_qty": "\t\t\t\t\r\t\r"},
}

SCRIPT_DIR = Path(__file__).parent.resolve()
BARCODE_DIR = SCRIPT_DIR / "barcodes"
OUTPUT_DIR = SCRIPT_DIR / "output"


# =============================================================================
# DATA LOADING (minimal - just what's needed for barcode generation)
# =============================================================================


def load_csv_as_dict(filepath, key_col, val_col):
    """Load CSV into dict mapping key_col -> val_col."""
    lookup = {}
    with open(filepath, newline="") as f:
        for row in csv.DictReader(f):
            lookup[row[key_col].strip()] = row[val_col].strip()
    return lookup


def load_bench_lots(filepath, bench):
    """Load lot numbers for a specific bench: Name -> LotNumber."""
    lookup = {}
    with open(filepath, newline="") as f:
        for row in csv.DictReader(f):
            if int(row["Bench"].strip()) == bench:
                lookup[row["Name"].strip()] = row["LotNumber"].strip()
    return lookup


def load_pou(filepath):
    """Load POU CSV, return (part_names, rows)."""
    with open(filepath, newline="") as f:
        reader = csv.DictReader(f)
        part_names = [h for h in reader.fieldnames if h != "Bundle"]
        rows = list(reader)
    return part_names, rows


# =============================================================================
# BARCODE GENERATION
# =============================================================================


def generate_barcodes(bench):
    """
    Generate all barcode PNGs for a bench.

    Naming convention: {bundle}_{part_name}.png
    This allows Typst to construct paths from CSV data.
    """
    part_numbers = load_csv_as_dict(SCRIPT_DIR / "part_numbers.csv", "Name", "PartNumber")
    bench_lots = load_bench_lots(SCRIPT_DIR / "bench_lots.csv", bench)
    part_names, pou_rows = load_pou(SCRIPT_DIR / "conn_prep_pou.csv")
    controls = BENCH_CONTROLS[bench]

    bench_dir = BARCODE_DIR / f"bench{bench}"
    bench_dir.mkdir(parents=True, exist_ok=True)

    count = 0
    for row in pou_rows:
        bundle = row["Bundle"].strip()
        if not bundle:
            continue

        for name in part_names:
            qty_str = row.get(name, "").strip()
            if not qty_str:
                continue

            try:
                qty = int(qty_str)
            except ValueError:
                print(f"Warning: Non-integer '{qty_str}' for {bundle}/{name}, skipping", file=sys.stderr)
                continue

            if name not in part_numbers:
                print(f"Error: No part number for '{name}'", file=sys.stderr)
                sys.exit(1)

            if name not in bench_lots:
                print(f"Error: No lot number for bench {bench}, part '{name}'", file=sys.stderr)
                sys.exit(1)

            # Build barcode data with control characters
            barcode_data = (
                f"{part_numbers[name]}{controls['post_part']}"
                f"{bench_lots[name]}{controls['post_lot']}"
                f"{qty}{controls['post_qty']}"
            )

            # Predictable filename: {bundle}_{name}.png
            filepath = bench_dir / f"{bundle}_{name}.png"

            result = subprocess.run(
                ["zint", "-b", "20", "-d", barcode_data, "--notext", "-o", str(filepath)],
                capture_output=True,
                text=True,
            )

            if result.returncode != 0:
                print(f"Error generating barcode {bundle}/{name}: {result.stderr}", file=sys.stderr)
                sys.exit(1)

            count += 1

    return count


# =============================================================================
# PDF COMPILATION
# =============================================================================


def compile_pdf(bench):
    """Invoke Typst to compile the PDF."""
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    typst_file = SCRIPT_DIR / "conn_prep.typ"
    pdf_file = OUTPUT_DIR / f"conn_prep_bench{bench}.pdf"

    result = subprocess.run(
        [
            "typst", "compile",
            "--root", str(SCRIPT_DIR),
            "--input", f"bench={bench}",
            str(typst_file),
            str(pdf_file),
        ],
        capture_output=True,
        text=True,
    )

    if result.returncode != 0:
        print(f"Typst error:\n{result.stderr}", file=sys.stderr)
        sys.exit(1)

    return pdf_file


# =============================================================================
# MAIN
# =============================================================================


def process_bench(bench):
    """Generate barcodes and compile PDF for one bench."""
    print(f"\n{'=' * 50}")
    print(f"Bench {bench}")
    print("=" * 50)

    print("Generating barcodes...")
    count = generate_barcodes(bench)
    print(f"  Generated {count} barcodes")

    print("Compiling PDF...")
    pdf = compile_pdf(bench)
    print(f"  Created {pdf}")


def main():
    parser = argparse.ArgumentParser(description="Generate Connector Prep barcode PDFs")
    parser.add_argument("--bench", type=str, required=True, help='Bench number (1-4) or "all"')
    parser.add_argument("--list-benches", action="store_true", help="List configured benches")
    args = parser.parse_args()

    if args.list_benches:
        print("Configured benches:", sorted(BENCH_CONTROLS.keys()))
        sys.exit(0)

    # Validate required files
    for f in ["part_numbers.csv", "bench_lots.csv", "conn_prep_pou.csv", "conn_prep.typ"]:
        if not (SCRIPT_DIR / f).exists():
            print(f"Error: {f} not found", file=sys.stderr)
            sys.exit(1)

    # Determine benches to process
    if args.bench.lower() == "all":
        benches = sorted(BENCH_CONTROLS.keys())
    else:
        try:
            bench = int(args.bench)
            if bench not in BENCH_CONTROLS:
                print(f"Error: Bench {bench} not configured", file=sys.stderr)
                sys.exit(1)
            benches = [bench]
        except ValueError:
            print(f"Error: Invalid bench '{args.bench}'", file=sys.stderr)
            sys.exit(1)

    for bench in benches:
        process_bench(bench)

    print("\nDone!")


if __name__ == "__main__":
    main()
