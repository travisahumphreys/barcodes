#set page(
  "us-letter",
  margin: (x:0.75in,y:0.6in,inside:1in),
)
#set text(
  font: "IBM Plex Sans",
  size: 10pt
)
#show table.cell.where(y: 0): set text(weight: "extrabold") 
#show table.cell.where(y: 0): set text(fill: white)
#set table(fill: (_, y) => if y==0 { black })



#let pou-table = csv("update_form.csv")
#table(
  columns: (30%, 25%, 25%, 1.2in),
  stroke: (x: none),
  align: (left + horizon),
  table.header[PART NAME][PART \#][LOT \#][NEW LOT (#emoji.checkmark)],
  ..pou-table.flatten(),
)
