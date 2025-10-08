---
sql:
  occupancy_query: ./data/duck.parquet
  bike_availability: ./data/bike_availability.parquet
  another:    ./data/new_data.csv
  dim_stations:    ./data/dim_stations.parquet
  timestamps:    ./data/timestamps.parquet
---


```sql 
select *
from bike_availability
limit 10
```

```sql 
select *
from occupancy_query
limit 10
```

```sql 
select *
from timestamps
inner join dim_stations_ds
limit 10
```


Here we have interactions by day. September's data is missing due to data issues on the providers side. We see a dip in bike usage over the Winter period with a sharp drop around Christmas.
```sql id = weekly 
select  strptime(substr(cast(hour_rounded as varchar),0,11),'%Y-%m-%d')as  week, cast(sum(interactions) as int) as weekly_interactions
from timestamps
group by 1
order by 1
```


```js
const weekl = Plot.plot({
  x: {
    tickRotate: -20,
    label: "Date",
  },
  y: {
    transform: (d) => d,
    label: "↑ Interactions",
    grid: 5
  },
  marks: [
    Plot.ruleY([0]),
    Plot.line(weekly, {
      x: "week",
      y: "weekly_interactions",
      stroke: "steelblue"
      })
  ]
});

display(weekl)
```






```sql id = occup display
select station_type, hours, avg(occupancy_rate) bike_availability_rate
from occupancy_query bd
inner join dim_stations ds on  bd.address_id = ds.address_id
--  where ds.address_id in (55,93,21,54,28,19,32,61,74,57,68)
group by 1,2
```


```js
const occupan = occup.toArray()

const occupancy = // assuming `occupan` is your table
Plot.plot({
  x: {
    label: "Hour of Day",
    tickFormat: d => d // show hour directly
  },
  y: {
    label: "Bike Availability Rate (%)"
  },
  color: {
    legend: true,
    label: "Station Type"
  },
  marks: [
    Plot.line(occupan, {
      x: "hours",
      y: "bike_availability_rate",
      stroke: "station_type"
    }),
    Plot.dot(occupan, {
      x: "hours",
      y: "bike_availability_rate",
      fill: "station_type"
    })
  ]
})

display(occupancy)
```

 ```sql echo id = stations display
SELECT *
FROM dim_stations 
``` 


```sql echo id = timesta display
SELECT address_id, max(interactions)--hour_rounded, cast(interactions as integer)
FROM timestamps
group by 1
``` 


```sql echo id = timestam display
SELECT 
  address,
  cast(SUM(interactions) as integer) AS total_interactions
FROM timestamps t
inner join dim_stations ds on ds.address_id = t.address_id
GROUP BY ds.address
ORDER BY 2 desc
limit 10;
``` 

```js


const bars = addTooltips(Plot.plot({
  marginBottom: 60,
  x: {
    tickRotate: -20,
    label: "Address",
  },
  y: {
    transform: (d) => d /1000,
    label: "↑ Interaction (Thousands)",
    grid: 5
  },
  marks: [
    Plot.ruleY([0]),
    Plot.barY(timestam, {
      x: "address",
      y: "total_interactions",
      sort: {x: "-y"},
      fill: "steelblue"
    })
  ],
    tooltip: {
    fill: "red"
  },
  height: 500,
  width: 800
}),
  { fill: "gray", opacity: 0.5, "stroke-width": "3px", stroke: "red" }
);

display(bars)
```


```js
display(Inputs.table(timestam))
```

<!-- ```js
const rawd = Array.from(timestamps, row => ({
  ...row,
  hour_rounded: new Date(row.hour_rounded) // if in ms
}));
display(rawd)
``` -->

```sql echo
SELECT *
FROM occupancy_query 
```



## Dublin Bikes - What's the story?
This analysis takes data from Dublin Bike's api through JC Deceaux and data.gov.ie and give an update for all stations every 5 minutes.

Let's start by taking a look at some timeseries trends. The below chart gives a view of when Dubliners interact with the bikes. Each black line represents the average number of interactions in an hour. There is one for every hour of the year. The further to the right the line is, the more interactions there were and you'll see the colour appears more purple as the mean of the observations increases.



```js
// These imports set up duckdb and then load in the data
import * as duckdb from "npm:@duckdb/duckdb-wasm@1.29.0";
 
import {DuckDBClient} from "npm:@observablehq/duckdb";

const db = DuckDBClient.of({occupancy_query: FileAttachment("./data/duck.parquet").parquet(),
  another: FileAttachment("./data/new_data.csv").csv()});
```

```js 
const quick_view = db.sql`SELECT
*
from occupancy_query `

// display(Inputs.table(quick_view))
```

 ```js

const result = await db.sql`
SELECT 
case
when cast(hour_rounded as timestamp) >= '2024-03-30 01:00:00'::timestamp 
  and cast(hour_rounded as timestamp) <  '2024-10-26 01:00:00'::timestamp
then cast((cast(hour_rounded as timestamp) + interval '1 hour') as varchar)
when cast(hour_rounded as timestamp) >= '2025-03-30 01:00:00'::timestamp 
  and cast(hour_rounded as timestamp) <  '2025-10-26 01:00:00'::timestamp
then cast((cast(hour_rounded as timestamp) + interval '1 hour') as varchar)
else hour_rounded
end as hour_rounded,
station_type,
hour,
day,
weekend,
week,
month,
quarter,
dayOfMonth,
interactions
FROM another
where left(hour_rounded,7) <> '2025-05'

`;
// display(Inputs.table(result))

// Convert DuckDBResult to a plain array of objects ( needed for data viz )
const raw_data = result.toArray();
// display(result.toArray())
 ```

```js
const test = FileAttachment("./data/new_data.csv").csv()
```
 

```js
import * as Plot from "npm:@observablehq/plot";
 
const facet_options = new Map(["Hour", "Day", "Weekend", "Week", "Month", "Quarter", "None"].map(d => [d, d.toLowerCase()]))
 
 
 
const x_facet = Inputs.radio(facet_options, {
  label: "Break out Horizontally by:",
  value: "weekend"
})
display(x_facet)
 
const y_facet = Inputs.radio(facet_options, {
  label: "Break out Vertically by:",
  value: "hour"
})
display(y_facet)
 
 

```
 



```js
const addTooltips = (chart, styles) => {
  const stroke_styles = { stroke: "blue", "stroke-width": 3 };
  const fill_styles = { fill: "blue", opacity: 0.5 };

  // Workaround if it's in a figure
  const type = d3.select(chart).node().tagName;
  let wrapper =
    type === "FIGURE" ? d3.select(chart).select("svg") : d3.select(chart);

  // Workaround if there's a legend....
  const svgs = d3.select(chart).selectAll("svg");
  if (svgs.size() > 1) wrapper = d3.select([...svgs].pop());
  wrapper.style("overflow", "visible"); // to avoid clipping at the edges

  // Set pointer events to visibleStroke if the fill is none (e.g., if its a line)
  wrapper.selectAll("path").each(function (data, index, nodes) {
    // For line charts, set the pointer events to be visible stroke
    if (
      d3.select(this).attr("fill") === null ||
      d3.select(this).attr("fill") === "none"
    ) {
      d3.select(this).style("pointer-events", "visibleStroke");
      if (styles === undefined) styles = stroke_styles;
    }
  });
  
  if (styles === undefined) styles = fill_styles;

  const tip = wrapper
    .selectAll(".hover")
    .data([1])
    .join("g")
    .attr("class", "hover")
    .style("pointer-events", "none")
    .style("text-anchor", "middle");

  // Add a unique id to the chart for styling
  const id = id_generator();

  // Add the event listeners
  d3.select(chart).classed(id, true); // using a class selector so that it doesn't overwrite the ID
  wrapper.selectAll("title").each(function () {
    // Get the text out of the title, set it as an attribute on the parent, and remove it
    const title = d3.select(this); // title element that we want to remove
    const parent = d3.select(this.parentNode); // visual mark on the screen
    const t = title.text();
    if (t) {
      parent.attr("__title", t).classed("has-title", true);
      title.remove();
    }
    // Mouse events
    parent
      .on("pointerenter pointermove", function (event) {
        const text = d3.select(this).attr("__title");
        const pointer = d3.pointer(event, wrapper.node());
        if (text) tip.call(hover, pointer, text.split("\n"));
        else tip.selectAll("*").remove();

        // Raise it
        d3.select(this).raise();
        // Keep within the parent horizontally
        const tipSize = tip.node().getBBox();
        if (pointer[0] + tipSize.x < 0)
          tip.attr(
            "transform",
            `translate(${tipSize.width / 2}, ${pointer[1] + 7})`
          );
        else if (pointer[0] + tipSize.width / 2 > wrapper.attr("width"))
          tip.attr(
            "transform",
            `translate(${wrapper.attr("width") - tipSize.width / 2}, ${
              pointer[1] + 7
            })`
          );
      })
      .on("pointerout", function (event) {
        tip.selectAll("*").remove();
        // Lower it!
        d3.select(this).lower();
      });
  });

  // Remove the tip if you tap on the wrapper (for mobile)
  wrapper.on("touchstart", () => tip.selectAll("*").remove());

  // Define the styles
  chart.appendChild(html`<style>
  .${id} .has-title { cursor: pointer;  pointer-events: all; }
  .${id} .has-title:hover { ${Object.entries(styles).map(([key, value]) => `${key}: ${value};`).join(" ")} }`);

  return chart;
}


const id_generator = () => {
  var S4 = function () {
    return (((1 + Math.random()) * 0x10000) | 0).toString(16).substring(1);
  };
  return "a" + S4() + S4();
}




const hover = (tip, pos, text) => {
  const side_padding = 10;
  const vertical_padding = 5;
  const vertical_offset = 15;

  // Empty it out
  tip.selectAll("*").remove();

  // Append the text
  tip
    .style("text-anchor", "middle")
    .style("pointer-events", "none")
    .attr("transform", `translate(${pos[0]}, ${pos[1] + 7})`)
    .selectAll("text")
    .data(text)
    .join("text")
    .style("dominant-baseline", "ideographic")
    .text((d) => d)
    .attr("y", (d, i) => (i - (text.length - 1)) * 15 - vertical_offset)
    .style("font-weight", (d, i) => (i === 0 ? "bold" : "normal"));

  const bbox = tip.node().getBBox();

  // Add a rectangle (as background)
  tip
    .append("rect")
    .attr("y", bbox.y - vertical_padding)
    .attr("x", bbox.x - side_padding)
    .attr("width", bbox.width + side_padding * 2)
    .attr("height", bbox.height + vertical_padding * 2)
    .style("fill", "white")
    .style("stroke", "#d3d3d3")
    .lower();
}
```







 
```js
const get_title = (d) => {
  const avg = d3.format(",.0f")(d3.mean(d, (d) => d.value));
  const x_value = x_facet.value === "hour" ? d[0].hour + ":00 PST" : d[0][x_facet.value];
  const y_value = y_facet.value === "hour" ? d[0].hour + ":00 PST" : d[0][y_facet.value];
  return `Avg. Interactions: ${avg}  \n` +
    (x_facet.value == 'none' ? "" : `${capitalize(x_facet.value)}: ${x_value}\n `) +
    (y_facet.value == "none" ? "" : `${capitalize(y_facet.value)}: ${y_value}`);
};
 
const x_facet_value = x_facet.value;  // string like "hour"
const y_facet_value = y_facet.value;
 
 
const capitalize = (string) => {
  return string.charAt(0).toUpperCase() + string.slice(1);
}
 
const months =  ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"]
 
const weekdays = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
 
const get_facet_options = (facet, direction = "x") => facet === "day"
  ? { domain: weekdays, tickFormat:d => (direction === "x" && width < 600) ?d.slice(0, 1) :d}
  : facet === "month"
  ? { domain: months, tickFormat: d => (direction === "x" && width < 600) ? d.slice(0, 1) : d }
  : (facet === "hour" && width > 800) ? {tickFormat: d => d + ":00"}:{}
 
 
 
// Load the Temporal API using a Polyfill
const { Temporal } = await import('@js-temporal/polyfill');
 
 
const data = raw_data.map((d) => {
  const tzdate = Temporal.PlainDateTime.from(d.hour_rounded);
  return {
    date: new Date(d.hour_rounded),
    hour: Number(tzdate.hour),
    day: weekdays[tzdate.dayOfWeek - 1],
    weekend: tzdate.dayOfWeek > 5 ? "Weekend" : "Weekday",
    week: String(tzdate.weekOfYear), // make week a string for faceting
    month: months[tzdate.month - 1],
    quarter:
      tzdate.month < 4
        ? "Q1: Jan - Mar"
        : tzdate.month < 7
        ? "Q2: Apr - Jun"
        : tzdate.month < 10
        ? "Q3: Jul - Sep"
        : "Q4: Oct - Dec",
    value: Number(d.interactions),
    dayOfMonth: Number(tzdate.day)
  };
});
 
 
 
 
 
 
// Your inputs stay the same:
display(x_facet);
display(y_facet);
 
// Container for chart
const chartDiv = document.createElement("div");
display(chartDiv);
 
function renderPlot() {
  chartDiv.innerHTML = ""; // Clear old chart
  chartDiv.appendChild(
    addTooltips(
      Plot.plot({
      width,
      facet: {
        data,
        x: x_facet.value,
        y: y_facet.value,
        marginLeft: y_facet.value === "week" || y_facet.value === "hour" ? 30 : 80
      },
      fy: {
        label: null,
        ...get_facet_options(y_facet.value, "y")
      },
      fx: {
        label: x_facet.value === "week" ? "Week" : null,
        ...get_facet_options(x_facet.value)
      },
      marks: [
        x_facet.value !== "week" ? Plot.frame() : null,
        Plot.rect(
          data,
          Plot.groupZ(
            { fill: "mean", title: get_title },
            {
              fill: "value",
              fillOpacity: 0.4,
            }
          )
        ),
        Plot.tickX(data, { x: "value", strokeOpacity: 0.2 })
      ],
      color: {
        scheme: "warm",
        reverse: true
      },
      x: { label: "Interactions →" },
      y: { label: "hour →" }
    },
      { stroke: "black", "stroke-width": "3px" } // tooltip styles
)
    ));
  }

 
// Initial render
renderPlot();
 
// Re-render on change
x_facet.addEventListener("input", renderPlot);
y_facet.addEventListener("input", renderPlot);
 
 
```

How does bike availability change throughout the day and throughout the city?

```js
display(occupancy)

```

Dublin's city centre gets full during the day while the outskirts empties as people commute to work.


What's more interesting is finding the stations that are frequently empty or too full to deposit a bike leading to disruptions.

```sql id = bike_availabilit display
select station_type, levels, address, num_day as num_days, num_hours, avg_time
from bike_availability bd
inner join dim_stations ds on  bd.address_id = ds.address_id
where levels = 'Empty'
order by num_days desc
limit 10
```
```js
const empty =Plot.plot({
  marks: [
    Plot.barY(bike_availabilit, { x: "address", y: "num_days" }),

    () =>
      Plot.plot({
        // dimensions
        marginLeft: 70,
        marginRight: 50,
        marginBottom: 50,
        width: Math.min(width, 780),
        height: 400,

        marks: [
          Plot.line(data, {
            x: "address",
            y: "num_hours",
          }),
          Plot.dot(data, {
            x: "address",
            y: "num_hours",
            fill: "white"
          })
        ],
        y: { axis: "right", nice: true, line: true }
      })
  ],

  marginLeft: 70,
  marginRight: 50,
  marginBottom: 50,
  width: Math.min(width, 780),
  height: 400,

  x: { tickRotate: -45, tickFormat: "" },
  y: { axis: "left" }})
```


```js
  const v1 = (d) => d.num_days;
  const v2 = (d) => d.num_hours;
  const y2 = d3.scaleLinear(d3.extent(bike_availabilit, v2), [0, d3.max(bike_availabilit, v1)]);
  const diff = Plot.plot({
    marks: [
      Plot.axisY(y2.ticks(), {color: "steelblue", anchor: "right", label: "efficiency (mpg)", y: y2, tickFormat: y2.tickFormat()}),
      Plot.ruleY([0]),
      Plot.barY(bike_availabilit, {x: "address", y: v1}),
      Plot.barY(bike_availabilit, Plot.mapY((D) => D.map(y2), {x: "address", y: v2, stroke: "steelblue"}))
    ]
  });

  display(diff)
```




```js
display(empty)
```