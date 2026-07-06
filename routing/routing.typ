// Routing Workstation Barcode Document Template
//
// This template handles ALL data processing and layout logic in pure Typst.
// Python only generates the barcode PNG files.
//
// The generation date is passed in via `--input date=YYYY-MM-DD`;
// it falls back to today's date when compiled standalone.

// =============================================================================
// PAGE SETUP (must match original bash-generated layout exactly)
// =============================================================================

#let generation-date = sys.inputs.at(
  "date",
  default: datetime.today().display("[year]-[month]-[day]"),
)

// State to track current bundle for headers
#let bundle-state = state("bundle", "")

#set page(
  paper: "us-letter",
  flipped: true,
  margin: (x: 0.5in, y: 1in, top: 1.5in),
  header: [
    #set text(size: 12pt)
    #grid(
      columns: (1fr, 1fr),
      align: (left, right),
      [#text(weight: "bold")[Bundle: #context bundle-state.get()]],
      [Generated: #generation-date]
    )
    #line(length: 100%)
  ]
)

#set text(size: 12pt)
#set align(center)

// =============================================================================
// DATA LOADING
// =============================================================================

#let raw-pou = csv("pou_map.csv")

// =============================================================================
// HELPER FUNCTIONS
// =============================================================================

// Build barcode image path from bundle and part name.
// The '/' replacement MUST match sanitize_filename() in generate.py.
#let barcode-path(bundle, part-name) = {
  "barcodes/" + bundle + "_" + part-name.replace("/", "-") + ".png"
}

// =============================================================================
// DATA PROCESSING
// =============================================================================

// Group rows by bundle, preserving CSV row order within each bundle.
// Returns: ((bundle, (part-name, ...)), ...) sorted by bundle
#let process-pou-data() = {
  let data-rows = raw-pou.slice(1).filter(row => row.at(0).trim() != "")

  let bundles = ()
  for row in data-rows {
    let bundle = row.at(0).trim()
    if bundle not in bundles { bundles.push(bundle) }
  }

  let result = ()
  for bundle in bundles.sorted() {
    let parts = data-rows
      .filter(row => row.at(0).trim() == bundle)
      .map(row => row.at(1).trim())
    result.push((bundle, parts))
  }
  result
}

#let pou-data = process-pou-data()

// =============================================================================
// DOCUMENT
// =============================================================================

// Render each bundle as a two-column section of labeled barcodes
#for (bundle, parts) in pou-data {
  bundle-state.update(bundle)
  pagebreak(weak: true)
  columns(2, gutter: 0.5cm)[
    #for name in parts {
      block(breakable: false)[
        #text(size: 10pt, weight: "regular")[#name]
        #v(0.05cm)
        #image(barcode-path(bundle, name), width: 100%)
      ]
      v(0.1cm)
    }
  ]
}
