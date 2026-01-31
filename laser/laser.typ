// Laser Workstation Barcode Document Template
//
// This template handles ALL data processing and layout logic in pure Typst.
// Python only generates the barcode PNG files.
//
// Usage: typst compile laser.typ output/laser.pdf

// =============================================================================
// PAGE SETUP (must match original bash-generated layout exactly)
// =============================================================================

#set page(
  paper: "us-letter",
  margin: (x: 0.75in, y: 1in),
)

#set text(size: 14pt)
#set align(center)

// =============================================================================
// DATA LOADING
// =============================================================================

#let raw-csv = csv("Laser-pou.csv")

// =============================================================================
// HELPER FUNCTIONS
// =============================================================================

// Convert part number to safe filename (replace / with -)
#let safe-filename(part-num) = {
  part-num.replace("/", "-")
}

// Build barcode image path from bundle and part number
#let barcode-path(bundle, part-num) = {
  "barcodes/" + bundle + "_" + safe-filename(part-num) + ".png"
}

// =============================================================================
// DATA PROCESSING
// =============================================================================

// Parse CSV into structured data grouped by bundle
// Returns: ((bundle, ((part-num, lot-num, qty), ...)), ...)
#let process-csv-data() = {
  // Skip header row
  let data-rows = raw-csv.slice(1)

  // Group rows by bundle, preserving CSV order within each bundle
  let bundles = (:)
  let bundle-order = ()  // Track insertion order for sorting

  for row in data-rows {
    let bundle = row.at(0).trim()
    let part-num = row.at(1).trim()
    let lot-num = row.at(2).trim()
    let qty = row.at(3).trim()

    if bundle == "" { continue }

    if bundle not in bundles {
      bundles.insert(bundle, ())
      bundle-order.push(bundle)
    }

    bundles.at(bundle).push((part-num, lot-num, qty))
  }

  // Sort bundles (matching `sort -u` behavior from bash script)
  let sorted-bundles = bundle-order.sorted()

  // Build result array
  let result = ()
  for bundle in sorted-bundles {
    result.push((bundle, bundles.at(bundle)))
  }
  result
}

#let pou-data = process-csv-data()

// =============================================================================
// DOCUMENT
// =============================================================================

// Render each bundle
#for (bundle, parts) in pou-data {
  pagebreak(weak: true)
  text(size: 20pt, weight: "bold")[#bundle]
  v(0.3cm)

  // Add all barcodes for this bundle (maintaining CSV row order)
  for (part-num, _lot-num, _qty) in parts {
    image(barcode-path(bundle, part-num))
    v(0.25cm)
  }
}
