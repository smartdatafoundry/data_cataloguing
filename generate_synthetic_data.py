import pandera as pa
from inferred_schema import schema
from pathlib import Path
import pandas as pd

def main():
    strategy = schema.strategy(size=100)
    synthetic_df = strategy.example()
    print("Synthetic Data Example:")
    print(synthetic_df)

    # Write synthetic data to synthetic_data/ folder
    output_dir = Path("synthetic_data")
    output_dir.mkdir(exist_ok=True)
    output_path = output_dir / "synthetic_data.csv"
    synthetic_df.to_csv(output_path, index=False)
    print(f"Synthetic data written to {output_path}")

if __name__ == "__main__":
    main()