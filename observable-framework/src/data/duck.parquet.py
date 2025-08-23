import duckdb
import pandas
import sys
import tempfile
import pyarrow as pa
import pyarrow.parquet as pq


# Connect to a DuckDB database (or create one)
con = duckdb.connect('my_duckdb.db')

con.execute("INSTALL httpfs;")
con.execute("LOAD httpfs;")


con.execute(f"SET s3_access_key_id='x';")
con.execute(f"SET s3_secret_access_key='x';")
con.execute(f"SET s3_region='eu-north-1';")


# Use read_parquet() to explicitly read the file as Parquet
s3_object_path = 's3://dublinbikeshistorical/data_warehouse/parquet_f_bike_station_status/20250817_102807_00103_mrpta_b6cd1f35-b359-4880-9f60-1a77389160e5'

duckdb_conn = duckdb.connect(database=':memory:')
df = con.execute(f"""
    SELECT
        last_reported,
        CAST(station_id AS VARCHAR) AS station_id,
        num_bikes_available,
        num_docks_available,
        is_installed,
        is_renting,
        is_returning,
        capacity
    FROM read_parquet('{s3_object_path}')
""").df()



with tempfile.TemporaryFile() as f:
    df.to_parquet(f)
    f.seek(0)
    sys.stdout.buffer.write(f.read())

# buf = pa.BufferOutputStream()
# table = pa.Table.from_pandas(df)
# pq.write_table(table, buf, compression="snappy")

# # Get the buffer as a bytes object
# buf_bytes = buf.getvalue().to_pybytes()

# # Write the bytes to standard output
# sys.stdout.buffer.write(buf_bytes)