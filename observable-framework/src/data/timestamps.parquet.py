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
    "s3://dublinbikeshistorical/cleaned/query__time_and_date_and_addresses/20250920_154035_00183_msxz7_ed253b2d-ff66-4083-aece-87e658e6a623"
)

# Execute query and return Arrow Table (no Pandas)
arrow_table = con.execute(f"""
    SELECT
        *
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

