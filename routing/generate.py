#!/usr/bin/env python3
"""
Routing Workstation Barcode Generator

Minimal Python script that ONLY:
1. Generates barcode PNG files with zint
2. Writes update_form.csv (derived from pou_map.csv)
3. Invokes Typst to compile the PDFs

All layout logic lives in routing.typ and update_form.typ

Usage:
    python generate.py           # Generate barcodes and PDFs
    python generate.py --clean   # Clean barcodes directory first
"""

import argparse
import csv
import shutil
import subprocess
import sys
from datetime import datetime
from pathlib import Path

# =============================================================================
# CONFIGURATION
# =============================================================================

SCRIPT_DIR = Path(__file__).parent.resolve()
BARCODE_DIR = SCRIPT_DIR / "barcodes"
OUTPUT_DIR = SCRIPT_DIR / "output"
POU_FILE = SCRIPT_DIR / "pou_map.csv"
UPDATE_FORM_CSV = SCRIPT_DIR / "update_form.csv"
BARCODE_PDF = OUTPUT_DIR / "router_barcodes.pdf"
UPDATE_FORM_PDF = OUTPUT_DIR / "update_form.pdf"


# =============================================================================
# DATA LOADING
# =============================================================================


def load_pou(filepath):
    """Load pou_map.csv, return list of row dicts."""
    with open(filepath, newline="") as f:
        return list(csv.DictReader(f))


# =============================================================================
# BARCODE GENERATION
# =============================================================================


def build_barcode_data(part_num, lot_num, quantity):
    """
    Build barcode data string with control characters.

    Format: {part}\\t {lot}\\t{qty}\\r\\t\\t\\t\\t{space}
    (tab+space after part, tab after lot, CR after quantity,
    four tabs and a trailing space at the end)

    Note: the CR after quantity reproduces the original bash/awk pipeline,
    where the CRLF line endings of the pou CSV leaked into awk's last
    field ($5, QUANTITY). It is part of the scanned payload and MUST be
    preserved. Here it is explicit, so the payload no longer depends on the
    CSV's line endings.
    """
    return f"{part_num}\t {lot_num}\t{quantity}\r\t\t\t\t "


def sanitize_filename(name):
    """
    Make a part name safe for use in a filename ('/' is the only unsafe
    character in use, e.g. '3/16 Heat Shrink').

    MUST match barcode-path() in routing.typ.
    """
    return name.replace("/", "-")


def generate_barcodes():
    """
    Generate all barcode PNGs.

    Naming convention: {bundle}_{sanitized_part_name}.png
    This allows Typst to construct paths from CSV data.
    """
    pou_rows = load_pou(POU_FILE)

    BARCODE_DIR.mkdir(parents=True, exist_ok=True)

    count = 0
    for row in pou_rows:
        bundle = row["BUNDLE"].strip()
        if not bundle:
            continue

        name = row["PART-NAME"].strip()
        barcode_data = build_barcode_data(
            row["PART-NUM"].strip(),
            row["LOT-NUM"].strip(),
            row["QUANTITY"].strip(),
        )
        filepath = BARCODE_DIR / f"{bundle}_{sanitize_filename(name)}.png"

        result = subprocess.run(
            [
                "zint",
                "-b",
                "20",
                "--height=25",
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
# UPDATE FORM
# =============================================================================


def write_update_form():
    """
    Derive update_form.csv from pou_map.csv.

    Matches the original pipeline exactly:
        awk -F',' 'NR>1 {print $2","toupper($3)","$4","}' | sort -uV
    GNU `sort -uV` (version sort) is shelled out to, so the output stays
    byte-identical to the original script.
    """
    lines = []
    with open(POU_FILE, newline="") as f:
        reader = csv.reader(f)
        next(reader)  # skip header
        for row in reader:
            if not row:
                continue
            lines.append(f"{row[1]},{row[2].upper()},{row[3]},")

    result = subprocess.run(
        ["sort", "-uV"],
        input="\n".join(lines) + "\n",
        capture_output=True,
        text=True,
    )

    if result.returncode != 0:
        print(f"sort error:\n{result.stderr}", file=sys.stderr)
        sys.exit(1)

    UPDATE_FORM_CSV.write_text(result.stdout)


# =============================================================================
# PDF COMPILATION
# =============================================================================


def compile_pdf(typst_name, pdf_file, inputs=None):
    """Invoke Typst to compile a PDF."""
    cmd = ["typst", "compile", "--root", str(SCRIPT_DIR)]
    for key, value in (inputs or {}).items():
        cmd += ["--input", f"{key}={value}"]
    cmd += [str(SCRIPT_DIR / typst_name), str(pdf_file)]

    result = subprocess.run(cmd, capture_output=True, text=True)

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
    parser = argparse.ArgumentParser(
        description="Generate Router barcode PDF and update form"
    )
    parser.add_argument(
        "--clean", action="store_true", help="Clean barcodes directory first"
    )
    args = parser.parse_args()

    # Validate required files
    for f in ["pou_map.csv", "routing.typ", "update_form.typ"]:
        if not (SCRIPT_DIR / f).exists():
            print(f"Error: {f} not found", file=sys.stderr)
            sys.exit(1)

    if args.clean:
        clean_barcodes()

    print("Generating barcodes...")
    count = generate_barcodes()
    print(f"  Generated {count} barcodes")

    print("Writing update form data...")
    write_update_form()
    print(f"  Created {UPDATE_FORM_CSV.name}")

    print("Compiling PDFs...")
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    generation_date = datetime.now().strftime("%Y-%m-%d")
    compile_pdf("routing.typ", BARCODE_PDF, inputs={"date": generation_date})
    print(f"  Created {BARCODE_PDF.name}")
    compile_pdf("update_form.typ", UPDATE_FORM_PDF)
    print(f"  Created {UPDATE_FORM_PDF.name}")

    print("\nDone!")


if __name__ == "__main__":
    main()
