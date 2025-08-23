# Load libraries (must be installed in environment)
import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq
import sys
import tempfile

df = pd.read_csv("https://nid.sec.usace.army.mil/api/nation/csv", low_memory=False, skiprows=1).loc[:, ["Dam Name", "Primary Purpose", "Primary Dam Type", "Hazard Potential Classification"]]


with tempfile.TemporaryFile() as f:
    df.to_parquet(f)
    f.seek(0)
    sys.stdout.buffer.write(f.read())