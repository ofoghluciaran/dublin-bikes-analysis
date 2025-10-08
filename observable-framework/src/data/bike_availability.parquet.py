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
    "s3://dublinbikeshistorical/cleaned/fact_station_status/20250918_194047_00623_x6va3_2ceaa28d-62dc-4008-9748-c3742febf798"
)

# Execute query and return Arrow Table (no Pandas)
arrow_table = con.execute(f"""
with rates as (
    SELECT
    address_id, 
    date(last_reported) dates,
    hour(last_reported) as hours,
    avg(num_docks_available),
    (avg(num_bikes_available) + avg(num_docks_available)),
    (avg(num_bikes_available) / (avg(num_bikes_available) + avg(num_docks_available))) * 100 as bike_availability_rate
    FROM read_parquet('{s3_object_path}')
    group by 1,2,3
    having ((avg(num_bikes_available)/ (avg(num_bikes_available) + avg(num_docks_available))) * 100 < 5
    or (avg(num_bikes_available)  / (avg(num_bikes_available) + avg(num_docks_available))) * 100 >95
    )
    and (avg(num_bikes_available) + avg(num_docks_available)) >0
    order by 1,2,3
)
select 
    address_id, 
    case when bike_availability_rate >95 then 'Empty' else 'Full' end as levels, 
    count(hours) as num_hours,
    round(avg(hours),0) as avg_time,
    count(distinct dates) as num_day
from rates
where hours between 7 and 18
group by 1,2
order by 1,2
""").arrow()

# import pandas as pd
# print("max_columns:", pd.get_option('display.max_columns'))
# print("width:", pd.get_option('display.width'))
# print("expand_frame_repr:", pd.get_option('display.expand_frame_repr'))
# print("max_colwidth:", pd.get_option('display.max_colwidth'))
# print("num columns:", len(arrow_table.columns))
# print("column names:", arrow_table.columns.tolist())   # shows every column name




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

