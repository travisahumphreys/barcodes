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
CSV_FILE = SCRIPT_DIR / "Laser-pou.csv"


# =============================================================================
# DATA LOADING
# =============================================================================


def load_csv():
    """Load Laser-pou.csv as list of dicts."""
    with open(CSV_FILE, newline="") as f:
        return list(csv.DictReader(f))


# =============================================================================
# BARCODE GENERATION
# =============================================================================


def build_barcode_data(part_num, lot_num, quantity):
    """
    Build barcode data string with control characters.

    Format: {part}\t {lot}\t{qty}\t\t\t\t
    (note space after first tab, space at end)
    """
    return f"{part_num}\t {lot_num}\t{quantity}\t\t\t\t "


def safe_filename(part_num):
    """Convert part number to safe filename (replace / with -)."""
    return part_num.replace("/", "-")


def generate_barcodes(rows):
    """
    Generate all barcode PNGs.

    Naming convention: {bundle}_{safe_part}.png
    This allows Typst to construct paths from CSV data.
    """
    BARCODE_DIR.mkdir(parents=True, exist_ok=True)

    count = 0
    for row in rows:
        bundle = row["BUNDLE"].strip()
        part_num = row["PART-NUM"].strip()
        lot_num = row["LOT-NUM"].strip()
        quantity = row["QUANTITY"].strip()

        if not bundle or not part_num:
            continue

        barcode_data = build_barcode_data(part_num, lot_num, quantity)
        safe_part = safe_filename(part_num)
        filepath = BARCODE_DIR / f"{bundle}_{safe_part}.png"

        result = subprocess.run(
            [
                "zint",
                "-b", "20",
                "--height=35",
                "-d", barcode_data,
                "-o", str(filepath),
            ],
            capture_output=True,
            text=True,
        )

        if result.returncode != 0:
            print(
                f"Error generating barcode {bundle}/{part_num}: {result.stderr}",
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
            "--root", str(SCRIPT_DIR),
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
    if not CSV_FILE.exists():
        print(f"Error: {CSV_FILE.name} not found", file=sys.stderr)
        sys.exit(1)

    typst_file = SCRIPT_DIR / "laser.typ"
    if not typst_file.exists():
        print(f"Error: laser.typ not found", file=sys.stderr)
        sys.exit(1)

    if args.clean:
        clean_barcodes()

    print("Loading CSV data...")
    rows = load_csv()
    print(f"  Found {len(rows)} rows")

    print("Generating barcodes...")
    count = generate_barcodes(rows)
    print(f"  Generated {count} barcodes")

    print("Compiling PDF...")
    pdf = compile_pdf()
    print(f"  Created {pdf}")

    print("\nDone!")


if __name__ == "__main__":
    main()
