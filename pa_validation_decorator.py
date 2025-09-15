from pathlib import Path
from typing import Union

import pandas as pd
import pandera as pa

from inferred_schema import schema 

@pa.check_output(schema, lazy=True)
def retrieve_data(path: Union[Path, str]) -> pd.DataFrame:
    return pd.read_csv(path)

def main() -> None:
    dataset_path = Path().absolute() 

    data = retrieve_data(dataset_path / "mock_data/weekly_financials.csv")

    print(data.head())

if __name__ == "__main__":
    main()