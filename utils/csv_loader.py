import pandas as pd
from pathlib import Path

DATA_PATH = Path(__file__).parent.parent / "data"

def load_csv(filename: str) -> pd.DataFrame:
    file_path = DATA_PATH / filename
    return pd.read_csv(file_path)