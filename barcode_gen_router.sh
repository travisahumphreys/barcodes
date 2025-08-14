#!/usr/bin/env bash

# Generate barcodes from Router CSV with labels
# Router CSV format: BUNDLE,PART-NAME,PART-NUM,LOT-NUM,QUANTITY
awk -F, 'NR > 1 {
    # Handle CSV quoted fields - remove outer quotes and unescape inner quotes
    for (i = 1; i <= NF; i++) {
        if ($i ~ /^".*"$/) {
            # Remove outer quotes
            gsub(/^"|"$/, "", $i)
            # Unescape doubled quotes
            gsub(/""/, "\"", $i)
        }
    }
    # Encode columns 3-5: PART-NUM, LOT-NUM, QUANTITY (same as Laser system)
    data = $3 "\t " $4 "\t"  $5 "\t\t\t\t "
    # Escape quotes for shell but preserve the character in the barcode
    gsub(/"/, "\\\"", data)
    system("zint -b 20 --height=35 -d \"" data "\" -o barcode_" $1 "_" sprintf("%03d", NR-1) ".png")
}' ./Router-pou.csv

# Wait for all barcodes to be generated
sleep 1

# Create Typst document
cat >barcodes_router.typ <<'EOF'
#set page(
  paper: "us-letter",
  margin: (x: 0.75in, y: 1in),
)

#set text(size: 14pt)
#set align(center)

EOF

# Add each key group to the Typst document
for key in $(ls barcode_*.png | cut -d_ -f2 | sort -u); do
    echo "#pagebreak(weak: true)" >>barcodes_router.typ
    echo "#text(size: 20pt, weight: \"bold\")[$key]" >>barcodes_router.typ
    echo "#v(0.5cm)" >>barcodes_router.typ

    # Get labels for this key from CSV and add images with labels
    awk -F, -v key="$key" 'NR > 1 && $1 == key {
        # Handle CSV quoted fields for labels
        for (i = 1; i <= NF; i++) {
            if ($i ~ /^".*"$/) {
                # Remove outer quotes
                gsub(/^"|"$/, "", $i)
                # Unescape doubled quotes
                gsub(/""/, "\"", $i)
            }
        }
        printf "barcode_%s_%03d.png:%s\n", $1, NR-1, $2
    }' ./Router-pou.csv | while IFS=: read -r img label; do
        if [[ -f "$img" ]]; then
            # Escape # symbols for Typst (# is special in Typst syntax)
            escaped_label="${label//\#/\\#}"
            echo "#block(breakable: false)[" >>barcodes_router.typ
            echo "  #text(size: 12pt, weight: \"regular\")[${escaped_label}]" >>barcodes_router.typ
            echo "  #v(0.1cm)" >>barcodes_router.typ
            echo "  #image(\"$img\")" >>barcodes_router.typ
            echo "]" >>barcodes_router.typ
            echo "#v(0.15cm)" >>barcodes_router.typ
        fi
    done
done

# Compile to PDF
typst compile barcodes_router.typ router_barcodes.pdf

# Clean up
rm barcodes_router.typ

echo "Generated router_barcodes.pdf with Router barcodes grouped by key with labels"

# Archive barcodes and PDF
timestamp=$(date +"%Y-%m-%d_%H-%M-%S")
archive_dir="arch/$timestamp"
mkdir -p "$archive_dir"

# Move PNGs to archive, copy PDF
mv barcode_*.png "$archive_dir/"
cp router_barcodes.pdf "$archive_dir/"

echo "Archived to: $archive_dir"

# Git commit the archive
if git rev-parse --git-dir >/dev/null 2>&1; then
    barcode_count=$(ls "$archive_dir"/barcode_*.png 2>/dev/null | wc -l)
    git add "$archive_dir"
    git commit -m "Archive barcode run $timestamp

Generated $barcode_count Router barcodes with labels
PDF: router_barcodes.pdf"
    echo "Committed to git"
else
    echo "Not a git repository - skipping git commit"
fi
