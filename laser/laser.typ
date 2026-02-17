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

#let raw-part-lots = csv("part_lots.csv")
#let raw-pou = csv("pou_map.csv")

// =============================================================================
// HELPER FUNCTIONS
// =============================================================================

// Build barcode image path from bundle and part name
#let barcode-path(bundle, part-name) = {
  "barcodes/" + bundle + "_" + part-name + ".png"
}

// =============================================================================
// DATA PROCESSING
// =============================================================================

// Build part-lots lookup: part-name -> (part-num, lot-num)
#let part-lots = {
  let lookup = (:)
  for row in raw-part-lots.slice(1) {
    let name = row.at(0).trim()
    if name != "" {
      lookup.insert(name, (row.at(1).trim(), row.at(2).trim()))
    }
  }
  lookup
}

// Extract part names from pou_map header (all columns except BUNDLE)
#let part-names = raw-pou.at(0).slice(1)

// Process pou_map into structured data grouped by bundle
// Returns: ((bundle, ((part-name, part-num, lot-num, qty), ...)), ...)
#let process-pou-data() = {
  let data-rows = raw-pou.slice(1)

  let result = ()
  for row in data-rows {
    let bundle = row.at(0).trim()
    if bundle == "" { continue }

    let parts = ()
    for (i, name) in part-names.enumerate() {
      let qty = row.at(i + 1).trim()
      if qty != "" {
        let (part-num, lot-num) = part-lots.at(name)
        parts.push((name, part-num, lot-num, qty))
      }
    }

    if parts.len() > 0 {
      result.push((bundle, parts))
    }
  }

  // Sort bundles alphabetically
  result.sorted(key: entry => entry.at(0))
}

#let pou-data = process-pou-data()

// =============================================================================
// DOCUMENT
// =============================================================================

// Render each bundle
#for (bundle, parts) in pou-data {
  pagebreak(weak: true)
  text(size: 20pt, weight: "bold")[#bundle]
  v(0.3cm)

  // Add all barcodes for this bundle (maintaining pou_map column order)
  for (name, _part-num, _lot-num, _qty) in parts {
    image(barcode-path(bundle, name))
    v(0.25cm)
  }
}
