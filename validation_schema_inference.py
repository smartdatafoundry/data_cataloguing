from pathlib import Path
import pandas as pd
import pandera as pa

# from altered_schema import schema

# GO THROUGH EACH OF THE COLUMNS AND CHECK IT ACTUALLY MAKES SENSE

# ADD CHECKS LIKE Checks.greather_than_or_equal_to(min_value=1)

# THEN CHECK NEW DATASETS WITH THE SCHEMA THAT YOU HAVE USING A DECORATOR 

def retrieve_data(path: Path) -> pd.DataFrame:
    return pd.read_csv(path)

def main() -> None:
    dataset_path = Path().absolute()
    data = retrieve_data(dataset_path / "test_data/2019-01-06.csv")
    data_inferred_schema = pa.infer_schema(data)
    with open('inferred_schema.py', 'w') as file:
        file.write(data_inferred_schema.to_script())

if __name__ == "__main__":
    main()