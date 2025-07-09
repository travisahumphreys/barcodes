# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a barcode generation system that creates Code 128 barcodes from CSV data and compiles them into organized PDF documents. The system uses the `zint` barcode library for generation and Typst for PDF document creation.

## Architecture

The system follows a single-script workflow in `barcode_gen_pdf.sh`:
1. **CSV Processing**: Reads `~/Laser-pou.csv` and processes each row (skipping header)
2. **Barcode Generation**: Uses `zint` to create PNG images with naming pattern `barcode_{key}_{sequence}.png`
3. **Dynamic PDF Creation**: Generates Typst document on-the-fly with proper grouping by key
4. **PDF Compilation**: Compiles the generated Typst document to `all_barcodes.pdf`
5. **Cleanup**: Removes temporary Typst file
6. **Auto-Archive**: Moves PNG files to timestamped archive directory, copies PDF
7. **Git Versioning**: Automatically commits archive to git with descriptive message

## Key Components

- **CSV Data Source**: `~/Laser-pou.csv` - Contains the source data for barcode generation
- **Main Script**: `barcode_gen_pdf.sh` - Complete end-to-end workflow with auto-archiving
- **Barcode Generation**: Uses `zint` library with Code 128 format (-b 20)
- **PDF Compilation**: Uses Typst typesetting system to create organized PDF documents
- **Archive Structure**: `arch/` directory contains timestamped subdirectories with barcode files and PDFs from each run
- **Version Control**: Automatic git commits track archive history with barcode counts

## Common Commands

### Generate Barcodes and PDF (Primary Workflow)
```bash
# Generate all barcodes from CSV and create PDF
./barcode_gen_pdf.sh
```

### Compile PDF from Existing Barcodes
```bash
# Compile existing Typst document to PDF
typst compile barcodes_example.typ all_barcodes.pdf
```

## File Structure

- `barcode_gen_pdf.sh` - Main script containing complete workflow with auto-archiving
- `barcodes_example.typ` - Example/reference Typst template showing expected format
- `all_barcodes.pdf` - Current/latest compiled PDF with all barcodes grouped by key (always in root)
- `arch/` - Archive directory containing timestamped subdirectories from each run
  - `arch/YYYY-MM-DD_HH-MM-SS/` - Timestamped archive for each generation run
    - `barcode_*.png` - All generated barcode images from that run
    - `all_barcodes.pdf` - Copy of the PDF from that run

## Dependencies

- `zint` - Barcode generation library
- `typst` - Document typesetting system
- `awk` - Text processing (used for CSV parsing)
- Standard Unix utilities (bash, cut, sort, ls, etc.)

## Data Format

The CSV file (`~/Laser-pou.csv`) should have the following structure:
- Column 1: Key/ID for grouping barcodes
- Column 2-4: Data fields that get encoded in the barcode (tab-separated in final encoding)
- Header row is skipped during processing (NR > 1)

## Barcode Naming Convention

Generated barcodes follow the pattern: `barcode_{key}_{sequence}.png`
- `key`: Value from column 1 of CSV
- `sequence`: Zero-padded 3-digit sequence number (001, 002, etc.) using `sprintf("%03d", NR-1)`

## PDF Generation Process

1. Process CSV with awk to generate individual barcode PNG files
2. Extract unique keys from generated barcode filenames using `ls | cut -d_ -f2 | sort -u`
3. Create Typst document dynamically with:
   - US Letter format with 0.75" horizontal and 1" vertical margins
   - 14pt body text, 20pt bold headings
   - Page breaks between key groups
   - Centered alignment for all content
4. Add all barcode images for each key with proper spacing (0.5cm after heading, 0.25cm between images)
5. Compile to PDF using Typst
6. Clean up temporary Typst file
7. Archive all PNG files to timestamped directory (arch/YYYY-MM-DD_HH-MM-SS/)
8. Copy PDF to archive directory
9. Commit archive to git with descriptive message including barcode count