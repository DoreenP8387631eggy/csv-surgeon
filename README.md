# csv-surgeon

A CLI tool for performing complex transformations and filtering on large CSV files without loading them fully into memory.

---

## Installation

```bash
pip install csv-surgeon
```

Or install from source:

```bash
git clone https://github.com/yourusername/csv-surgeon.git
cd csv-surgeon && pip install -e .
```

---

## Usage

```bash
# Filter rows where the "age" column is greater than 30
csv-surgeon filter --input data.csv --output result.csv --where "age > 30"

# Drop columns and rename headers
csv-surgeon transform --input data.csv --output result.csv --drop "ssn,internal_id" --rename "fname:first_name"

# Chain operations using a config file
csv-surgeon run --config pipeline.yaml --input data.csv --output result.csv
```

**Example `pipeline.yaml`:**

```yaml
steps:
  - filter: "status == 'active'"
  - drop: ["password", "token"]
  - rename:
      dob: date_of_birth
```

csv-surgeon streams data row by row, making it suitable for files too large to fit in RAM.

---

## Features

- Stream-based processing — handles multi-GB files with low memory usage
- Filter rows using simple expression syntax
- Drop, rename, and reorder columns
- Pipeline support via YAML config files
- Fast output with minimal dependencies

---

## License

This project is licensed under the [MIT License](LICENSE).