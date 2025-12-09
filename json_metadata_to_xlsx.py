import json
from pathlib import Path
import argparse
import polars as pl

def main():
    parser = argparse.ArgumentParser(description="Convert metadata JSON to XLSX and optionally CSV data to Parquet.")
    parser.add_argument("json_path", help="Path to the input metadata JSON file")
    parser.add_argument("csv_data_path", nargs="?", help="Path to the input CSV data file to convert to Parquet (optional)")
    args = parser.parse_args()

    json_path = Path(args.json_path)
    with open(json_path, "r") as f:
        metadata = json.load(f)

    fields = metadata.get("fields", {})
    rows = []
    for field in fields.values():
        rows.append([
            field.get("field_name", ""),
            field.get("type", ""),
            field.get("description", ""),
            field.get("constraints", "")
        ])

    # Convert to XLSX using Polars
    output_dir = Path("data_dictionary_xlsx")
    output_dir.mkdir(exist_ok=True)
    output_path = output_dir / f"{json_path.stem}.xlsx"
    df_xlsx = pl.DataFrame(rows, schema=["field_name", "type", "description", "constraints"])
    df_xlsx.write_excel(output_path)
    print(f"XLSX saved to {output_path}")

    # Optional: convert CSV data to Parquet if provided
    if args.csv_data_path:
        csv_data_path = Path(args.csv_data_path)
        df = pl.read_csv(csv_data_path)
        parquet_dir = Path("resulting_data")
        parquet_dir.mkdir(exist_ok=True)
        parquet_path = parquet_dir / f"{csv_data_path.stem}.parquet"
        df.write_parquet(parquet_path)
        print(f"Parquet saved to {parquet_path}")

if __name__ == "__main__":
    main()