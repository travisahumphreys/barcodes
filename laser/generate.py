#!/usr/bin/env python3
"""
Laser Workstation Barcode Generator

Minimal Python script that ONLY:
1. Generates barcode PNG files with zint
2. Invokes Typst to compile the PDF

All data processing and layout logic lives in laser.typ

Usage:
    python generate.py           # Generate barcodes and PDF
    python generate.py --clean   # Clean barcodes directory first
"""

import argparse
import csv
import shutil
import subprocess
import sys
from pathlib import Path

# =============================================================================
# CONFIGURATION
# =============================================================================

SCRIPT_DIR = Path(__file__).parent.resolve()
BARCODE_DIR = SCRIPT_DIR / "barcodes"
OUTPUT_DIR = SCRIPT_DIR / "output"
PART_LOTS_FILE = SCRIPT_DIR / "part_lots.csv"
POU_MAP_FILE = SCRIPT_DIR / "pou_map.csv"


# =============================================================================
# DATA LOADING
# =============================================================================


def load_part_lots(filepath):
    """Load part_lots.csv into dict: PART-NAME -> (PART-NUM, LOT-NUM)."""
    lookup = {}
    with open(filepath, newline="") as f:
        for row in csv.DictReader(f):
            lookup[row["PART-NAME"].strip()] = (
                row["PART-NUM"].strip(),
                row["LOT-NUM"].strip(),
            )
    return lookup


def load_pou(filepath):
    """Load pou_map.csv, return (part_names, rows)."""
    with open(filepath, newline="") as f:
        reader = csv.DictReader(f)
        part_names = [h for h in reader.fieldnames if h != "BUNDLE"]
        rows = list(reader)
    return part_names, rows


# =============================================================================
# BARCODE GENERATION
# =============================================================================


def build_barcode_data(part_num, lot_num, quantity):
    """
    Build barcode data string with control characters.

    Format: {part}\t\r{lot}\t{qty}\t\t\t\t\r\t\r
    (note space after first tab, space at end)
    """
    return f"{part_num}\t\r{lot_num}\t{quantity}\t\t\t\t\r\t\r"


def generate_barcodes():
    """
    Generate all barcode PNGs.

    Naming convention: {bundle}_{part_name}.png
    This allows Typst to construct paths from CSV data.
    """
    part_lots = load_part_lots(PART_LOTS_FILE)
    part_names, pou_rows = load_pou(POU_MAP_FILE)

    BARCODE_DIR.mkdir(parents=True, exist_ok=True)

    count = 0
    for row in pou_rows:
        bundle = row["BUNDLE"].strip()
        if not bundle:
            continue

        for name in part_names:
            qty_str = row.get(name, "").strip()
            if not qty_str:
                continue

            qty = int(qty_str)
            part_num, lot_num = part_lots[name]

            barcode_data = build_barcode_data(part_num, lot_num, str(qty))
            filepath = BARCODE_DIR / f"{bundle}_{name}.png"

            result = subprocess.run(
                [
                    "zint",
                    "-b",
                    "20",
                    "--height=35",
                    "-d",
                    barcode_data,
                    "-o",
                    str(filepath),
                ],
                capture_output=True,
                text=True,
            )

            if result.returncode != 0:
                print(
                    f"Error generating barcode {bundle}/{name}: {result.stderr}",
                    file=sys.stderr,
                )
                sys.exit(1)

            count += 1

    return count


# =============================================================================
# PDF COMPILATION
# =============================================================================


def compile_pdf():
    """Invoke Typst to compile the PDF."""
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    typst_file = SCRIPT_DIR / "laser.typ"
    pdf_file = OUTPUT_DIR / "laser.pdf"

    result = subprocess.run(
        [
            "typst",
            "compile",
            "--root",
            str(SCRIPT_DIR),
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


def clean_barcodes():
    """Remove all generated barcode PNGs."""
    if BARCODE_DIR.exists():
        shutil.rmtree(BARCODE_DIR)
        print(f"Cleaned {BARCODE_DIR}")


def main():
    parser = argparse.ArgumentParser(description="Generate Laser barcode PDF")
    parser.add_argument(
        "--clean", action="store_true", help="Clean barcodes directory first"
    )
    args = parser.parse_args()

    # Validate required files
    for f in ["part_lots.csv", "pou_map.csv", "laser.typ"]:
        if not (SCRIPT_DIR / f).exists():
            print(f"Error: {f} not found", file=sys.stderr)
            sys.exit(1)

    if args.clean:
        clean_barcodes()

    print("Generating barcodes...")
    count = generate_barcodes()
    print(f"  Generated {count} barcodes")

    print("Compiling PDF...")
    pdf = compile_pdf()
    print(f"  Created {pdf}")

    print("\nDone!")


if __name__ == "__main__":
    main()
