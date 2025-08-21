-- After loading the data into S3 and joining the CSVs with AWS Glue I started modelling the data. My goal is to make dimensional tables to make
-- the data easier to query.



-- This makes a new dim_bike_stations table which holds all data for
--the bike stations and joins it with a station_type table I loaded in which classifies each station as either Dublin Central or Dublin Periphery.
--The data contained a station_id column but was missing all values within, the xxhash64 will create a unique station ID for each address
create table dim_bike_stations as
select distinct xxhash64(cast(a.address as varbinary)) as  station_id, station_type, b.address,  trim(both '"' from b.address) as address_trimmed, lat, lon, capacity
from (
        select distinct address,capacity,lat,lon
        from f_station_statusraw a
        where system_id = '"dublin_bikes"' 
        and capacity is not null
        --group by 1,3
) a
inner join dim_station_type b on a.address = b.address
;




-- Next I cleaned up the fact table, removing columns that are now better accessed through dim tables and trimming columns that are wrapped in double quotes.
create table f_bike_station_status as
select      
    cast(trim(both '"' from last_reported) as timestamp) as last_reported,
    b.station_id, -- new station ID
    num_bikes_available,
    num_docks_available,
    is_installed,
    is_renting,
    is_returning,
    b.capacity
from ( 
    select distinct *
    from dublin_bikes.f_station_statusraw 
    where system_id = '"dublin_bikes"' 
    and capacity is not null -- Some rows were duplicated, same station appearing twice, one with no details on its capacity.
) a
inner join dim_bike_stations b 
    on a.address = b.address 
;