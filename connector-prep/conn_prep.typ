// Connector Prep Barcode Document Template
//
// This template handles ALL data processing and layout logic in pure Typst.
// Python only generates the barcode PNG files - nothing else.
//
// Usage: typst compile conn_prep.typ output.pdf --input bench=1

// =============================================================================
// CONFIGURATION
// =============================================================================

// Bench number passed from command line (default to 1)
#let bench = int(sys.inputs.at("bench", default: "1"))

// =============================================================================
// DATA LOADING
// =============================================================================

// Load CSV files
#let raw-part-numbers = csv("part_numbers.csv")
#let raw-bench-lots = csv("bench_lots.csv")
#let raw-pou = csv("pou_map.csv")

// Build part numbers lookup: Name -> PartNumber
#let part-numbers = {
  let lookup = (:)
  for row in raw-part-numbers.slice(1) {  // skip header
    let name = row.at(0)
    let part-num = upper(row.at(1))  // uppercase part numbers
    lookup.insert(name, part-num)
  }
  lookup
}

// Build bench lots lookup: Name -> LotNumber (filtered by current bench)
#let bench-lots = {
  let lookup = (:)
  for row in raw-bench-lots.slice(1) {  // skip header
    let row-bench = int(row.at(0))
    if row-bench == bench {
      let name = row.at(1)
      let lot-num = row.at(2)
      lookup.insert(name, lot-num)
    }
  }
  lookup
}

// Get part names from POU header (all columns except Bundle)
#let pou-header = raw-pou.at(0)
#let part-names = pou-header.slice(1)

// =============================================================================
// HELPER FUNCTIONS
// =============================================================================

// Extract assembly prefix from bundle (e.g., "3755-300" -> "3755")
#let get-assembly-prefix(bundle) = {
  let parts = bundle.split("-")
  if parts.len() > 0 { parts.at(0) } else { bundle.slice(0, 4) }
}

// Build barcode image path from bundle and part name
#let barcode-path(bundle, name) = {
  "barcodes/bench" + str(bench) + "/" + bundle + "_" + name + ".png"
}

// =============================================================================
// DOCUMENT COMPONENTS
// =============================================================================

// Lot Number Update Request Form
#let lot-update-form() = {
  align(center, text(size: 16pt, weight: "bold")[Bench #bench - Lot Number Update Request])
  v(1em)
  align(center)[If a lot number needs updating, write the new lot number in the box.]
  v(1em)

  table(
    columns: (1fr, 1.5fr, 1.5fr, 1.5fr),
    align: (left, left, left, left),
    stroke: 0.5pt,
    inset: 8pt,
    [*Part Name*], [*Part Number*], [*Current Lot*], [*New Lot*],
    ..for name in part-names {
      let part-num = part-numbers.at(name, default: "???")
      let lot-num = bench-lots.at(name, default: "???")
      ([#name], [#part-num], [#lot-num], [])
    }
  )

  v(2em)
  align(center)[Requested by: #underline[#h(15em)] Date: #underline[#h(8em)]]
}

// Single barcode card
#let barcode-card(bundle, name) = {
  box(stroke: 0.5pt + gray, inset: 0.5em, radius: 3pt)[
    #align(center)[
      #text(weight: "bold")[#name]
      #v(0.2em)
      #image(barcode-path(bundle, name), width: 100%)
    ]
  ]
}

// Bundle section (all barcodes for one bundle number)
#let bundle-section(bundle, parts-with-qty) = {
  block(breakable: false)[
    #text(size: 12pt, weight: "bold")[#bundle]
    #v(0.2em)
    #grid(
      columns: (1fr, 1fr),
      gutter: 1em,
      ..for (name, _qty) in parts-with-qty {
        (barcode-card(bundle, name),)
      }
    )
    #v(0.5em)
  ]
}

// =============================================================================
// DATA PROCESSING
// =============================================================================

// Process POU data into structured format: ((assembly, ((bundle, parts), ...)), ...)
#let process-pou-data() = {
  // Group bundles by assembly prefix
  let assemblies = (:)

  for row in raw-pou.slice(1) {  // skip header
    let bundle = row.at(0).trim()
    if bundle == "" { continue }

    let prefix = get-assembly-prefix(bundle)

    // Get parts with non-empty quantities
    let parts-with-qty = ()
    for (i, name) in part-names.enumerate() {
      let qty-str = row.at(i + 1, default: "").trim()
      if qty-str != "" {
        // Verify we have lot info for this part on this bench
        if bench-lots.at(name, default: none) != none {
          parts-with-qty.push((name, qty-str))
        }
      }
    }

    if parts-with-qty.len() > 0 {
      if prefix not in assemblies {
        assemblies.insert(prefix, (:))
      }
      assemblies.at(prefix).insert(bundle, parts-with-qty)
    }
  }

  // Convert to sorted array format for iteration
  let result = ()
  for prefix in assemblies.keys().sorted() {
    let bundles = assemblies.at(prefix)
    let bundle-list = ()
    for bundle in bundles.keys().sorted() {
      bundle-list.push((bundle, bundles.at(bundle)))
    }
    result.push((prefix, bundle-list))
  }
  result
}

#let pou-data = process-pou-data()

// =============================================================================
// DOCUMENT
// =============================================================================

#set page(paper: "us-letter", margin: (inside: 1in, rest: 0.5in))
#set text(font: "Liberation Sans", size: 10pt)

// Page 1: Lot Update Request Form
#lot-update-form()
#pagebreak(to: "odd")

// Title
#align(center, text(size: 16pt, weight: "bold")[Connector Prep - Bench #bench])
#v(0.5em)

// Render each assembly
#for (i, (prefix, bundles)) in pou-data.enumerate() {
  text(size: 14pt, weight: "bold")[Assembly #prefix]
  v(0.3em)

  for (bundle, parts-with-qty) in bundles {
    bundle-section(bundle, parts-with-qty)
  }

  // Page break between assemblies (except after last)
  if i < pou-data.len() - 1 {
    pagebreak(to: "odd")
  }
}
