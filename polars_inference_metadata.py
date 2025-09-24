import polars as pl
import re
import json
from pathlib import Path

def infer_regex_from_values(values):
    values = [str(v) for v in values if v is not None]
    if not values:
        return ""
    if all(v.isdigit() for v in values):
        return r"^\d+$"
    if all(v.isupper() for v in values):
        return r"^[A-Z]+$"
    if all(v.isalnum() for v in values):
        return r"^\w+$"
    lengths = set(len(v) for v in values)
    if len(lengths) == 1:
        l = lengths.pop()
        return rf"^.{{{l}}}$"
    return r"^.*$"

def polars_dtype_to_metadata_type(dtype):
    if dtype in [pl.Utf8, pl.String]:
        return "string"
    if dtype in [pl.Float32, pl.Float64]:
        return "float"
    if dtype in [pl.Int8, pl.Int16, pl.Int32, pl.Int64, pl.UInt8, pl.UInt16, pl.UInt32, pl.UInt64]:
        return "int"
    if dtype in [pl.Date, pl.Datetime]:
        return "date"
    return str(dtype)

def main():
    path = "test_data/2019-01-06.csv"
    lf = pl.scan_csv(path)

    dtypes = lf.dtypes
    columns = lf.columns

    # Null counts for all columns (lazy)
    null_counts_expr = [pl.col(c).null_count().alias(c) for c in columns]
    null_counts = lf.select(null_counts_expr).collect().to_dict(as_series=False)

    fields = {}

    # String columns
    string_cols = [col for col, dtype in zip(columns, dtypes) if dtype == pl.Utf8 or dtype == pl.String]
    # Numeric columns
    numeric_cols = [col for col, dtype in zip(columns, dtypes) if dtype in [pl.Float32, pl.Float64, pl.Int8, pl.Int16, pl.Int32, pl.Int64, pl.UInt8, pl.UInt16, pl.UInt32, pl.UInt64]]

    # Date columns: dtype or parseable as date
    date_cols = set()
    for col, dtype in zip(columns, dtypes):
        if dtype == pl.Date or dtype == pl.Datetime:
            date_cols.add(col)
        elif dtype == pl.Utf8 or dtype == pl.String:
            # Try to parse as date
            sample = lf.select(pl.col(col)).collect()[col].drop_nulls().to_list()[:10]
            if all(re.match(r"\d{4}-\d{2}-\d{2}", str(val)) for val in sample if val is not None):
                date_cols.add(col)

    # Collect string columns for regex and unique values
    if string_cols:
        string_df = lf.select(string_cols).collect()
    # Collect date columns for min/max
    date_minmax = {}
    for col in date_cols:
        minmax = lf.select([pl.col(col).min().alias("min"), pl.col(col).max().alias("max")]).collect().to_dict(as_series=False)
        date_minmax[col] = minmax

    for col, dtype in zip(columns, dtypes):
        # If it's a date column, override type
        field_type = "date" if col in date_cols else polars_dtype_to_metadata_type(dtype)
        field = {
            "field_name": col,
            "type": field_type,
            "description": "",
        }
        constraints = []
        # Nulls
        constraints.append(f"nulls: {null_counts[col][0]}")
        if field_type == "date":
            min_val = date_minmax[col]["min"][0]
            max_val = date_minmax[col]["max"][0]
            constraints.append(f"min: {min_val}, max: {max_val}")
        elif field_type == "string":
            values = string_df[col].drop_nulls().unique().to_list()
            regex = infer_regex_from_values(values)
            if regex and regex != r"^.*$":
                constraints.append(f"regex: [\"{regex}\"]")
            # Unique values for categoricals
            if len(values) <= 20:
                allowed = ', '.join([f'"{v}"' for v in values])
                constraints.append(f"allowed_values: [{allowed}]")
        field["constraints"] = ", ".join(constraints)
        fields[col] = field

    metadata = {
        "dataset": {
            "name": "",
            "description": ""
        },
        "fields": fields
    }

    output_dir = Path("json")
    output_dir.mkdir(exist_ok=True)
    output_path = output_dir / "polars_inference.json"
    with open(output_path, "w") as f:
        json.dump(metadata, f, indent=2)
    print(f"Summary saved to {output_path}")

if __name__ == "__main__":
    main()