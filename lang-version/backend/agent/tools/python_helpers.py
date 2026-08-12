import pandas as pd

def get_csv_schema(path: str):
    df = pd.read_csv(path, nrows=5)

    return {
        "columns": list(df.columns),
        "preview": df.head(3).to_markdown(index=False),
        "dtypes": df.dtypes.to_dict()
    }