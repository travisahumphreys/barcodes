#!/usr/bin/env python3
"""
Connector Prep Barcode Generator

Generates barcode PDFs for each workbench by:
1. Joining part_numbers.csv, bench_lots.csv, and conn_prep_pou.csv
2. Generating Code 128 barcodes with zint
3. Compiling PDFs with Typst

Usage:
    python generate.py --bench 1        # Generate for bench 1 only
    python generate.py --bench all      # Generate for all benches
    python generate.py --list-benches   # Show configured benches
"""

import argparse
import csv
import os
import subprocess
import sys
from pathlib import Path

# =============================================================================
# CONFIGURATION
# =============================================================================

# Control characters for barcode data, per bench.
# Adjust these if a bench's scanner has different suffix requirements.
# Format: {PartNumber}{post_part}{LotNumber}{post_lot}{Quantity}{post_qty}
BENCH_CONTROLS = {
    1: {"post_part": "\t\r", "post_lot": "\t", "post_qty": "\t\t\t\t\r\t\r"},
    2: {"post_part": "\t\r", "post_lot": "\t", "post_qty": "\t\t\t\t\r\t\r"},
    3: {"post_part": "\t\r", "post_lot": "\t", "post_qty": "\t\t\t\t\r\t\r"},
    4: {"post_part": "\t\r", "post_lot": "\t", "post_qty": "\t\t\t\t\r\t\r"},
}

# File paths (relative to script location)
SCRIPT_DIR = Path(__file__).parent.resolve()
PART_NUMBERS_FILE = SCRIPT_DIR / "part_numbers.csv"
BENCH_LOTS_FILE = SCRIPT_DIR / "bench_lots.csv"
CONN_PREP_POU_FILE = SCRIPT_DIR / "conn_prep_pou.csv"
OUTPUT_DIR = SCRIPT_DIR / "output"
BARCODE_DIR = SCRIPT_DIR / "barcodes"

# =============================================================================
# DATA LOADING
# =============================================================================


def load_part_numbers(filepath):
    """
    Load part_numbers.csv into a dict: {Name: PartNumber}
    Expected columns: Name, PartNumber
    """
    lookup = {}
    with open(filepath, newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            name = row["Name"].strip()
            part_num = row["PartNumber"].strip()
            lookup[name] = part_num
    return lookup


def load_bench_lots(filepath):
    """
    Load bench_lots.csv into a nested dict: {Bench: {Name: LotNumber}}
    Expected columns: Bench, Name, LotNumber
    """
    lookup = {}
    with open(filepath, newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            bench = int(row["Bench"].strip())
            name = row["Name"].strip()
            lot_num = row["LotNumber"].strip()
            if bench not in lookup:
                lookup[bench] = {}
            lookup[bench][name] = lot_num
    return lookup


def load_conn_prep_pou(filepath):
    """
    Load conn_prep_pou.csv and return (headers, rows).
    Headers = list of column names (first is 'Bundle', rest are part names)
    Rows = list of dicts
    """
    with open(filepath, newline="") as f:
        reader = csv.DictReader(f)
        headers = reader.fieldnames
        rows = list(reader)
    return headers, rows


# =============================================================================
# DATA TRANSFORMATION
# =============================================================================


def unpack_assembly_row(row, part_names, part_numbers, bench_lots, bench, controls):
    """
    Given a single row from conn_prep_pou, yield barcode records for each
    non-empty quantity cell.

    Yields dicts with keys:
        - bundle: Assembly number (e.g., "3755-300")
        - name: Friendly name (e.g., "Black")
        - part_number: Actual part number (e.g., "MS27488-22-2")
        - lot_number: Lot number for this bench
        - quantity: Integer quantity
        - barcode_data: Formatted string with control characters
    """
    bundle = row["Bundle"].strip()

    for name in part_names:
        qty_str = row.get(name, "").strip()
        if not qty_str:
            continue

        try:
            quantity = int(qty_str)
        except ValueError:
            print(
                f"Warning: Non-integer quantity '{qty_str}' for {bundle}/{name}, skipping",
                file=sys.stderr,
            )
            continue

        # Look up part number
        if name not in part_numbers:
            print(f"Error: No part number found for '{name}'", file=sys.stderr)
            sys.exit(1)
        part_number = part_numbers[name]

        # Look up lot number for this bench
        if bench not in bench_lots or name not in bench_lots[bench]:
            print(
                f"Error: No lot number found for bench {bench}, part '{name}'",
                file=sys.stderr,
            )
            sys.exit(1)
        lot_number = bench_lots[bench][name]

        # Build barcode data string with control characters
        barcode_data = (
            f"{part_number}{controls['post_part']}"
            f"{lot_number}{controls['post_lot']}"
            f"{quantity}{controls['post_qty']}"
        )

        yield {
            "bundle": bundle,
            "name": name,
            "part_number": part_number,
            "lot_number": lot_number,
            "quantity": quantity,
            "barcode_data": barcode_data,
        }


def generate_all_records(part_numbers, bench_lots, pou_headers, pou_rows, bench):
    """
    Generate all barcode records for a given bench.
    Returns a list of dicts, sorted by bundle.
    """
    # Part names are all columns except 'Bundle'
    part_names = [h for h in pou_headers if h != "Bundle"]
    controls = BENCH_CONTROLS[bench]

    records = []
    for row in pou_rows:
        for record in unpack_assembly_row(
            row, part_names, part_numbers, bench_lots, bench, controls
        ):
            records.append(record)

    return records


# =============================================================================
# BARCODE GENERATION
# =============================================================================


def generate_barcodes(records, bench):
    """
    Generate PNG barcodes using zint for each record.
    Returns records with 'barcode_file' key added.
    """
    bench_barcode_dir = BARCODE_DIR / f"bench{bench}"
    bench_barcode_dir.mkdir(parents=True, exist_ok=True)

    for i, record in enumerate(records):
        # Filename: bench_bundle_index.png
        filename = f"{record['bundle']}_{i:04d}.png"
        filepath = bench_barcode_dir / filename

        # Generate barcode with zint
        # -b 20 = Code 128
        # --notext = don't include human-readable text (we'll add labels in Typst)
        result = subprocess.run(
            [
                "zint",
                "-b",
                "20",
                "-d",
                record["barcode_data"],
                "--notext",
                "--height=30",
                "-o",
                str(filepath),
            ],
            capture_output=True,
            text=True,
        )

        if result.returncode != 0:
            print(
                f"Error generating barcode for {record['bundle']}/{record['name']}: "
                f"{result.stderr}",
                file=sys.stderr,
            )
            sys.exit(1)

        record["barcode_file"] = filepath

    return records


# =============================================================================
# TYPST GENERATION
# =============================================================================


def generate_lot_update_form(bench, part_numbers, bench_lots):
    """
    Generate Typst source for a lot number update request form.
    """
    lines = []

    lines.append(
        f'#align(center, text(size: 16pt, weight: "bold")[Bench {bench} - Lot Number Update Request])'
    )
    lines.append("#v(1em)")
    lines.append(
        "#align(center)[If a lot number needs updating, write the new lot number in the box.]"
    )
    lines.append("#v(1em)")
    lines.append("")

    # Table header and rows
    lines.append("#table(")
    lines.append("  columns: (1fr, 1.5fr, 1.5fr, 1.5fr),")
    lines.append("  align: (left, left, left, left, center),")
    lines.append("  stroke: 0.5pt,")
    lines.append("  inset: 8pt,")
    lines.append("  [*Part Name*], [*Part Number*], [*Current Lot*], [*New Lot*],")

    # Sort by part name for consistent ordering
    for name in sorted(part_numbers.keys()):
        part_num = part_numbers[name]
        lot_num = bench_lots.get(bench, {}).get(name, "???")
        lines.append(
            f"  [{name.upper()}], [{part_num.upper()}], [{lot_num.upper()}], [],"
        )

    lines.append(")")
    lines.append("")
    lines.append("#v(2em)")
    lines.append(
        "#align(center)[Requested by: #underline[#h(15em)] Date: #underline[#h(8em)]]"
    )
    lines.append("")

    return "\n".join(lines)


def group_by_assembly(records):
    """
    Group records by assembly prefix (first 4 digits of bundle).
    Returns dict: {prefix: {bundle: [records]}}
    """
    assemblies = {}
    for record in records:
        bundle = record["bundle"]
        # Extract Assembly ID (without dash number)
        if "-" in bundle:
            prefix = bundle.split("-")[0]
        else:
            prefix = bundle[:4]

        if prefix not in assemblies:
            assemblies[prefix] = {}
        if bundle not in assemblies[prefix]:
            assemblies[prefix][bundle] = []
        assemblies[prefix][bundle].append(record)

    return assemblies


def generate_typst_source(records, bench, part_numbers, bench_lots):
    """
    Generate Typst source code for the PDF.
    """
    assemblies = group_by_assembly(records)

    lines = []

    # Document setup
    lines.append('#set page(paper: "us-letter", margin: (inside: 1in, rest: 0.5in),)')
    lines.append('#set text(font: "Liberation Sans", size: 10pt)')
    lines.append("")

    # Lot update request form as first page
    lines.append(generate_lot_update_form(bench, part_numbers, bench_lots))
    lines.append('#pagebreak(to: "odd")')
    lines.append("")

    # Title
    lines.append(
        f'#align(center, text(size: 16pt, weight: "bold")[Connector Prep - Bench {bench}])'
    )
    lines.append("#v(0.5em)")
    lines.append("")

    # Process each assembly prefix
    sorted_prefixes = sorted(assemblies.keys())

    for prefix_idx, prefix in enumerate(sorted_prefixes):
        bundles = assemblies[prefix]
        sorted_bundles = sorted(bundles.keys())

        # Assembly header
        lines.append(f'#text(size: 14pt, weight: "bold")[Assembly {prefix}]')
        lines.append("#v(0.3em)")
        lines.append("")

        for bundle in sorted_bundles:
            bundle_records = bundles[bundle]

            # Wrap each variant in a block that won't break
            lines.append("#block(breakable: false)[")
            lines.append(f'  #text(size: 12pt, weight: "bold")[{bundle}]')
            lines.append("  #v(0.2em)")
            lines.append("  #grid(")
            lines.append("    columns: (1fr, 1fr),")
            lines.append("    gutter: 1em,")

            for record in bundle_records:
                barcode_path = os.path.relpath(record["barcode_file"], OUTPUT_DIR)
                label = record["name"]
                lines.append(
                    "    box(stroke: 0.5pt + gray, inset: 0.5em, radius: 3pt)["
                )
                lines.append("      #align(center)[")
                lines.append(f'        #text(weight: "bold")[{label}]')
                lines.append("        #v(0.2em)")
                lines.append(f'        #image("{barcode_path}", width: 100%)')
                lines.append("      ]")
                lines.append("    ],")

            lines.append("  )")
            lines.append("  #v(0.5em)")
            lines.append("]")
            lines.append("")

        # Page break between assembly prefixes (except after the last one)
        if prefix_idx < len(sorted_prefixes) - 1:
            lines.append('#pagebreak(to: "odd")')
            lines.append("")

    return "\n".join(lines)


def compile_pdf(typst_source, bench):
    """
    Write Typst source to file and compile to PDF.
    """
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    typst_file = OUTPUT_DIR / f"conn_prep_bench{bench}.typ"
    pdf_file = OUTPUT_DIR / f"conn_prep_bench{bench}.pdf"

    # Write Typst source
    with open(typst_file, "w") as f:
        f.write(typst_source)

    result = subprocess.run(
        ["typst", "compile", "--root", str(SCRIPT_DIR), str(typst_file), str(pdf_file)],
        capture_output=True,
        text=True,
    )

    if result.returncode != 0:
        print(f"Error compiling PDF: {result.stderr}", file=sys.stderr)
        sys.exit(1)

    print(f"Generated: {pdf_file}")
    return pdf_file


# =============================================================================
# MAIN
# =============================================================================


def process_bench(bench, part_numbers, bench_lots, pou_headers, pou_rows):
    """
    Full pipeline for a single bench.
    """
    print(f"\n{'=' * 60}")
    print(f"Processing Bench {bench}")
    print("=" * 60)

    # Generate records
    print("Generating barcode records...")
    records = generate_all_records(
        part_numbers, bench_lots, pou_headers, pou_rows, bench
    )
    print(f"  {len(records)} barcodes to generate")

    # Generate barcode images
    print("Generating barcode images with zint...")
    records = generate_barcodes(records, bench)

    # Generate Typst and compile PDF
    print("Generating PDF with Typst...")
    typst_source = generate_typst_source(records, bench, part_numbers, bench_lots)
    pdf = compile_pdf(typst_source, bench)

    return pdf


def main():
    parser = argparse.ArgumentParser(description="Generate Connector Prep barcode PDFs")
    parser.add_argument(
        "--bench", type=str, required=True, help='Bench number (1-4) or "all"'
    )
    parser.add_argument(
        "--list-benches", action="store_true", help="List configured benches and exit"
    )
    args = parser.parse_args()

    if args.list_benches:
        print("Configured benches:")
        for bench in sorted(BENCH_CONTROLS.keys()):
            print(f"  Bench {bench}")
        sys.exit(0)

    # Determine which benches to process
    if args.bench.lower() == "all":
        benches = sorted(BENCH_CONTROLS.keys())
    else:
        try:
            bench = int(args.bench)
            if bench not in BENCH_CONTROLS:
                print(
                    f"Error: Bench {bench} not configured. "
                    f"Available: {sorted(BENCH_CONTROLS.keys())}",
                    file=sys.stderr,
                )
                sys.exit(1)
            benches = [bench]
        except ValueError:
            print(
                f"Error: Invalid bench '{args.bench}'. Use a number or 'all'.",
                file=sys.stderr,
            )
            sys.exit(1)

    # Check for required files
    for filepath, desc in [
        (PART_NUMBERS_FILE, "part_numbers.csv"),
        (BENCH_LOTS_FILE, "bench_lots.csv"),
        (CONN_PREP_POU_FILE, "conn_prep_pou.csv"),
    ]:
        if not filepath.exists():
            print(f"Error: {desc} not found at {filepath}", file=sys.stderr)
            sys.exit(1)

    # Load data
    print("Loading data...")
    part_numbers = load_part_numbers(PART_NUMBERS_FILE)
    print(f"  Loaded {len(part_numbers)} part numbers")

    bench_lots = load_bench_lots(BENCH_LOTS_FILE)
    print(f"  Loaded lot numbers for {len(bench_lots)} benches")

    pou_headers, pou_rows = load_conn_prep_pou(CONN_PREP_POU_FILE)
    print(f"  Loaded {len(pou_rows)} assemblies")

    # Process each bench
    for bench in benches:
        process_bench(bench, part_numbers, bench_lots, pou_headers, pou_rows)

    print("\nDone!")


if __name__ == "__main__":
    main()
