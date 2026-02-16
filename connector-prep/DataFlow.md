# Global Variables

## **BENCH_CONTROLS** ( _nested dict_ )

- Top-Level Key (_int_)
  - The number referring to a workbench
- Top-Level Values (_dict_)
  - A dictionary of _string:string_ keys:values

- Second-Level Keys (_string_)
  - The position the corresponding value will hold in the Barcoded string, i.e. **"post_part"** will be after the part number.
- Second-Level Values:
  - A series of control characters to traverse a multi-field form.

## SCRIPT*DIR ( \_file path* )

- The path that holds the generate.py script.

## BARCODE*DIR ( \_file path* )

- The path that generate_barcodes() outputs the raw barcode images.

## OUTPUT*DIR ( \_file path* )

- The path that compile_pdf() outputs the final PDF.

---

# Functions

## load_csv_as_dict(filepath, key_col, val_col):

### Parameters:

**filepath:**

- Used in the `open()` CSV method to point to `part_numbers.csv` and load data from the _Name -> PartNumber_ mapping.

**key_col:**

- Points to the Part Name (first column) of the _Name -> PartNumber_ mapping and assigns the value in the column as the key of the returned dictionary `lookup{}`

**val_column:**

- Points to the Part Number (second column) of the _Name -> PartNumber_ mapping and assigns the string in the column as the corresponding key's value in the returned dicitonary `lookup{}`

### Calls:

None

### Called By:

`generate_barcodes()`

## load_bench_lots(filepath, bench)

### Parameters:

**filepath:**

- Used in the `open()` CSV method to point to `bench_lots.csv` and load data from the _Bench -> Name -> LotNumber_ mapping.

**bench:**

- Used to specify for which bench to load lot number data.
  > [!NOTE]
  > when `--bench all` is specified from the commandline, the invocation in `main()` loops through all available benches.

### Calls:

### Called By:

`generate_barcodes()`

## load_pou(filepath)

### Parameters:

**filepath:**

- Used in the `open()` CSV method to point to `pou_map.csv` and load data from the quantity matrix.

### Calls:

### Called By:

generate_barcodes()

## generate_barcodes(bench)

### Parameters:

### Calls:

- `load_csv_as_dict()`
- `load_bench_lots()`
- `load_pou()`

### Called By:

`main()`

## compile_pdf(bench)

### Calls:

### Called By:

## process_bench(bench)

### Calls:

### Called By:

## main()
