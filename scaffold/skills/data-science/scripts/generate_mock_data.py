"""Script to generate mock data for testing the Data Science skill."""

import argparse
from pathlib import Path

import numpy as np
import pandas as pd


def generate_mock_data(output_path: str, rows: int = 100):
    """Generate a synthetic dataset with numeric, categorical, and null values.

    Args:
        output_path: Where to save the CSV file.
        rows: Number of rows to generate.
    """
    np.random.seed(42)

    data = pd.DataFrame(
        {
            "id": range(1, rows + 1),
            "date": pd.date_range(start="2023-01-01", periods=rows, freq="D"),
            "category": np.random.choice(
                ["A", "B", "C", None], rows, p=[0.3, 0.4, 0.2, 0.1]
            ),
            "feature_1": np.random.randn(rows) * 10 + 50,
            "feature_2": np.abs(np.random.normal(0, 1, rows)) * 100,
            "target": np.where(np.random.randn(rows) > 0, 1, 0),
        }
    )

    # Introduce some logical duplicates
    data = pd.concat([data, data.head(5)], ignore_index=True)

    # Add some outliers
    data.loc[0, "feature_1"] = 500

    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)

    data.to_csv(path, index=False)
    print(f"✅ Mock dataset generated at: {path}")
    print(f"Summary: {data.shape[0]} rows, {data.shape[1]} columns")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate mock datasets.")
    parser.add_argument(
        "--output", default="data/mock_dataset.csv", help="Output CSV path"
    )
    parser.add_argument("--rows", type=int, default=100, help="Number of rows")
    args = parser.parse_args()
    generate_mock_data(args.output, args.rows)
