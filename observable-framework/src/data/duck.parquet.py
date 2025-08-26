import duckdb
import sys
import io
import pyarrow as pa
import pyarrow.parquet as pq

con = duckdb.connect('my_duckdb.db')

con.execute("INSTALL httpfs;")
con.execute("LOAD httpfs;")

con.execute("SET s3_access_key_id='x';")
con.execute("SET s3_secret_access_key='x';")
con.execute("SET s3_region='eu-north-1';")

s3_object_path = (
    "s3://dublinbikeshistorical/data_warehouse/parquet_f_bike_station_status/"
    "20250817_102807_00103_mrpta_b6cd1f35-b359-4880-9f60-1a77389160e5"
)

# Execute query and return Arrow Table (no Pandas)
arrow_table = con.execute(f"""
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
""").arrow()

buffer = io.BytesIO()
pq.write_table(
    arrow_table,
    buffer,
    compression="snappy",
    use_dictionary=True,
    write_statistics=True,
    data_page_size=1024 * 1024,  # 1MB pages for efficiency
    version="2.6"  # Modern Parquet features
)

sys.stdout.buffer.write(buffer.getvalue())

