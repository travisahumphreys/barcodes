#!/usr/bin/env bash

# Generate barcodes from CSV
awk -F, 'NR > 1 {
    data = $2 "\t " $3 "\t"  $4 "\t\t\t\t "
    system("zint -b 20 -d \"" data "\" -o barcode_" $1 "_" sprintf("%03d", NR-1) ".png")
}' ./Laser-pou.csv

# Wait for all barcodes to be generated
sleep 1

# Create Typst document
cat >barcodes.typ <<'EOF'
#set page(
  paper: "us-letter",
  margin: (x: 0.75in, y: 1in),
)

#set text(size: 14pt)
#set align(center)

EOF

# Add each key group to the Typst document
for key in $(ls barcode_*.png | cut -d_ -f2 | sort -u); do
    echo "#pagebreak(weak: true)" >>barcodes.typ
    echo "#text(size: 20pt, weight: \"bold\")[$key]" >>barcodes.typ
    echo "#v(0.5cm)" >>barcodes.typ

    # Add all images for this key
    for img in barcode_${key}_*.png; do
        echo "#image(\"$img\")" >>barcodes.typ
        echo "#v(0.25cm)" >>barcodes.typ
    done
done

# Compile to PDF
typst compile barcodes.typ all_barcodes.pdf

# Clean up
rm barcodes.typ

echo "Generated all_barcodes.pdf with barcodes grouped by key"

# Archive barcodes and PDF
timestamp=$(date +"%Y-%m-%d_%H-%M-%S")
archive_dir="arch/$timestamp"
mkdir -p "$archive_dir"

# Move PNGs to archive, copy PDF
mv barcode_*.png "$archive_dir/"
cp all_barcodes.pdf "$archive_dir/"

echo "Archived to: $archive_dir"

# Git commit the archive
if git rev-parse --git-dir >/dev/null 2>&1; then
    barcode_count=$(ls "$archive_dir"/barcode_*.png 2>/dev/null | wc -l)
    git add "$archive_dir"
    git commit -m "Archive barcode run $timestamp

Generated $barcode_count barcodes
PDF: all_barcodes.pdf"
    echo "Committed to git"
else
    echo "Not a git repository - skipping git commit"
fi
