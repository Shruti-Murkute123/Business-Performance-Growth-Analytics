
import pandas as pd


def profile_dataset(df):
    """Inspect a dataset without modifying its original data."""

    if df is None or df.empty:
        raise ValueError("The uploaded dataset is empty.")

    profile = {
        "rows": len(df),
        "columns": len(df.columns),
        "column_details": [],
        "missing_cells": int(df.isna().sum().sum()),
        "duplicate_rows": int(df.duplicated().sum()),
        "memory_usage_kb": round(
            df.memory_usage(deep=True).sum() / 1024, 2
        )
    }

    for column in df.columns:
        series = df[column]

        details = {
            "column": str(column),
            "data_type": str(series.dtype),
            "missing": int(series.isna().sum()),
            "missing_percentage": round(
                series.isna().mean() * 100, 2
            ),
            "unique_values": int(series.nunique()),
            "sample_values": [
                str(x) for x in series.dropna().head(3)
            ]
        }

        if pd.api.types.is_numeric_dtype(series):
            details["detected_type"] = "numeric"
            details["minimum"] = (
                float(series.min()) if series.notna().any()
                else None
            )
            details["maximum"] = (
                float(series.max()) if series.notna().any()
                else None
            )

        elif pd.api.types.is_datetime64_any_dtype(series):
            details["detected_type"] = "date"

        else:
            details["detected_type"] = "categorical_or_text"

            # Check whether text values look like dates.
            if series.notna().any():
                parsed = pd.to_datetime(
                    series.dropna().head(100),
                    errors="coerce"
                )
                if parsed.notna().mean() >= 0.8:
                    details["detected_type"] = "possible_date"

        profile["column_details"].append(details)

    return profile
