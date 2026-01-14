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
      [Generated: 2025-11-01]
    )
    #line(length: 100%)
  ]
)

#set text(size: 12pt)
#set align(center)

#bundle-state.update("5104")
#pagebreak(weak: true)
#columns(2, gutter: 0.5cm)[
#block(breakable: false)[
  #text(size: 10pt, weight: "regular")[\#10 Red Lug]
  #v(0.05cm)
  #image("barcode_5104_024.png", width: 100%)
]
#v(0.1cm)
#block(breakable: false)[
  #text(size: 10pt, weight: "regular")[\#10 Blue Lug]
  #v(0.05cm)
  #image("barcode_5104_025.png", width: 100%)
]
#v(0.1cm)
#block(breakable: false)[
  #text(size: 10pt, weight: "regular")[Blue Contact]
  #v(0.05cm)
  #image("barcode_5104_026.png", width: 100%)
]
#v(0.1cm)
#block(breakable: false)[
  #text(size: 10pt, weight: "regular")[\#10 High Temp Lug]
  #v(0.05cm)
  #image("barcode_5104_027.png", width: 100%)
]
#v(0.1cm)
#block(breakable: false)[
  #text(size: 10pt, weight: "regular")[Red 9 Splice]
  #v(0.05cm)
  #image("barcode_5104_028.png", width: 100%)
]
#v(0.1cm)
#block(breakable: false)[
  #text(size: 10pt, weight: "regular")[Red Moisture Sleeve]
  #v(0.05cm)
  #image("barcode_5104_029.png", width: 100%)
]
#v(0.1cm)
#block(breakable: false)[
  #text(size: 10pt, weight: "regular")[Yellow 9 Splice]
  #v(0.05cm)
  #image("barcode_5104_030.png", width: 100%)
]
#v(0.1cm)
#block(breakable: false)[
  #text(size: 10pt, weight: "regular")[Yellow Moisture Sleeve]
  #v(0.05cm)
  #image("barcode_5104_031.png", width: 100%)
]
#v(0.1cm)
#block(breakable: false)[
  #text(size: 10pt, weight: "regular")[5104 Big Splice]
  #v(0.05cm)
  #image("barcode_5104_032.png", width: 100%)
]
#v(0.1cm)
#block(breakable: false)[
  #text(size: 10pt, weight: "regular")[TFE 4X 0.25in (VL)]
  #v(0.05cm)
  #image("barcode_5104_033.png", width: 100%)
]
#v(0.1cm)
#block(breakable: false)[
  #text(size: 10pt, weight: "regular")[Solder Sleeve 3-18awg]
  #v(0.05cm)
  #image("barcode_5104_034.png", width: 100%)
]
#v(0.1cm)
#block(breakable: false)[
  #text(size: 10pt, weight: "regular")[Solder Sleeve 3-N]
  #v(0.05cm)
  #image("barcode_5104_035.png", width: 100%)
]
#v(0.1cm)
#block(breakable: false)[
  #text(size: 10pt, weight: "regular")[Jumper Wire 20awg]
  #v(0.05cm)
  #image("barcode_5104_036.png", width: 100%)
]
#v(0.1cm)
#block(breakable: false)[
  #text(size: 10pt, weight: "regular")[Jumper Wire 18awg]
  #v(0.05cm)
  #image("barcode_5104_037.png", width: 100%)
]
#v(0.1cm)
#block(breakable: false)[
  #text(size: 10pt, weight: "regular")[\#1 Coil Spacer]
  #v(0.05cm)
  #image("barcode_5104_038.png", width: 100%)
]
#v(0.1cm)
#block(breakable: false)[
  #text(size: 10pt, weight: "regular")[\#2 Coil Spacer]
  #v(0.05cm)
  #image("barcode_5104_039.png", width: 100%)
]
#v(0.1cm)
#block(breakable: false)[
  #text(size: 10pt, weight: "regular")[\#3 Coil Spacer]
  #v(0.05cm)
  #image("barcode_5104_040.png", width: 100%)
]
#v(0.1cm)
#block(breakable: false)[
  #text(size: 10pt, weight: "regular")[\#4 Coil Spacer]
  #v(0.05cm)
  #image("barcode_5104_041.png", width: 100%)
]
#v(0.1cm)
#block(breakable: false)[
  #text(size: 10pt, weight: "regular")[\#5 Coil Spacer]
  #v(0.05cm)
  #image("barcode_5104_042.png", width: 100%)
]
#v(0.1cm)
#block(breakable: false)[
  #text(size: 10pt, weight: "regular")[Tedlar Tape]
  #v(0.05cm)
  #image("barcode_5104_043.png", width: 100%)
]
#v(0.1cm)
#block(breakable: false)[
  #text(size: 10pt, weight: "regular")[3/16 Heat Shrink]
  #v(0.05cm)
  #image("barcode_5104_044.png", width: 100%)
]
#v(0.1cm)
#block(breakable: false)[
  #text(size: 10pt, weight: "regular")[3/32 Heat Shrink]
  #v(0.05cm)
  #image("barcode_5104_045.png", width: 100%)
]
#v(0.1cm)
#block(breakable: false)[
  #text(size: 10pt, weight: "regular")[3/8 Heat Shrink]
  #v(0.05cm)
  #image("barcode_5104_046.png", width: 100%)
]
#v(0.1cm)
]
#bundle-state.update("6230")
#pagebreak(weak: true)
#columns(2, gutter: 0.5cm)[
#block(breakable: false)[
  #text(size: 10pt, weight: "regular")[\#10 Red Lug]
  #v(0.05cm)
  #image("barcode_6230_001.png", width: 100%)
]
#v(0.1cm)
#block(breakable: false)[
  #text(size: 10pt, weight: "regular")[\#10 Blue Lug]
  #v(0.05cm)
  #image("barcode_6230_002.png", width: 100%)
]
#v(0.1cm)
#block(breakable: false)[
  #text(size: 10pt, weight: "regular")[Red Contact]
  #v(0.05cm)
  #image("barcode_6230_003.png", width: 100%)
]
#v(0.1cm)
#block(breakable: false)[
  #text(size: 10pt, weight: "regular")[Blue Contact]
  #v(0.05cm)
  #image("barcode_6230_004.png", width: 100%)
]
#v(0.1cm)
#block(breakable: false)[
  #text(size: 10pt, weight: "regular")[\#10 High Temp Lug]
  #v(0.05cm)
  #image("barcode_6230_005.png", width: 100%)
]
#v(0.1cm)
#block(breakable: false)[
  #text(size: 10pt, weight: "regular")[Red 9 Splice]
  #v(0.05cm)
  #image("barcode_6230_006.png", width: 100%)
]
#v(0.1cm)
#block(breakable: false)[
  #text(size: 10pt, weight: "regular")[Red Moisture Sleeve]
  #v(0.05cm)
  #image("barcode_6230_007.png", width: 100%)
]
#v(0.1cm)
#block(breakable: false)[
  #text(size: 10pt, weight: "regular")[Blue 9 Splice]
  #v(0.05cm)
  #image("barcode_6230_008.png", width: 100%)
]
#v(0.1cm)
#block(breakable: false)[
  #text(size: 10pt, weight: "regular")[Blue Moisture Sleeve]
  #v(0.05cm)
  #image("barcode_6230_009.png", width: 100%)
]
#v(0.1cm)
#block(breakable: false)[
  #text(size: 10pt, weight: "regular")[6230 Big Splice]
  #v(0.05cm)
  #image("barcode_6230_010.png", width: 100%)
]
#v(0.1cm)
#block(breakable: false)[
  #text(size: 10pt, weight: "regular")[TFE 4X 0.25in (VL)]
  #v(0.05cm)
  #image("barcode_6230_011.png", width: 100%)
]
#v(0.1cm)
#block(breakable: false)[
  #text(size: 10pt, weight: "regular")[Solder Sleeve 3-20awg]
  #v(0.05cm)
  #image("barcode_6230_012.png", width: 100%)
]
#v(0.1cm)
#block(breakable: false)[
  #text(size: 10pt, weight: "regular")[Solder Sleeve 3-18awg]
  #v(0.05cm)
  #image("barcode_6230_013.png", width: 100%)
]
#v(0.1cm)
#block(breakable: false)[
  #text(size: 10pt, weight: "regular")[Jumper Wire 20awg]
  #v(0.05cm)
  #image("barcode_6230_014.png", width: 100%)
]
#v(0.1cm)
#block(breakable: false)[
  #text(size: 10pt, weight: "regular")[\#1 Coil Spacer]
  #v(0.05cm)
  #image("barcode_6230_015.png", width: 100%)
]
#v(0.1cm)
#block(breakable: false)[
  #text(size: 10pt, weight: "regular")[\#2 Coil Spacer]
  #v(0.05cm)
  #image("barcode_6230_016.png", width: 100%)
]
#v(0.1cm)
#block(breakable: false)[
  #text(size: 10pt, weight: "regular")[\#3 Coil Spacer]
  #v(0.05cm)
  #image("barcode_6230_017.png", width: 100%)
]
#v(0.1cm)
#block(breakable: false)[
  #text(size: 10pt, weight: "regular")[\#4 Coil Spacer]
  #v(0.05cm)
  #image("barcode_6230_018.png", width: 100%)
]
#v(0.1cm)
#block(breakable: false)[
  #text(size: 10pt, weight: "regular")[\#5 Coil Spacer]
  #v(0.05cm)
  #image("barcode_6230_019.png", width: 100%)
]
#v(0.1cm)
#block(breakable: false)[
  #text(size: 10pt, weight: "regular")[Tedlar Tape]
  #v(0.05cm)
  #image("barcode_6230_020.png", width: 100%)
]
#v(0.1cm)
#block(breakable: false)[
  #text(size: 10pt, weight: "regular")[3/16 Heat Shrink]
  #v(0.05cm)
  #image("barcode_6230_021.png", width: 100%)
]
#v(0.1cm)
#block(breakable: false)[
  #text(size: 10pt, weight: "regular")[3/32 Heat Shrink]
  #v(0.05cm)
  #image("barcode_6230_022.png", width: 100%)
]
#v(0.1cm)
#block(breakable: false)[
  #text(size: 10pt, weight: "regular")[3/8 Heat Shrink]
  #v(0.05cm)
  #image("barcode_6230_023.png", width: 100%)
]
#v(0.1cm)
]
