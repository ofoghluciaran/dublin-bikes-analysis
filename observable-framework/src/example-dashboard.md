


```js
import * as duckdb from "npm:@duckdb/duckdb-wasm@1.29.0";

import {DuckDBClient} from "npm:@observablehq/duckdb";

const db = DuckDBClient.of({gaias: FileAttachment("./data/duck.parquet").parquet()});
```

```js
const bins = db.sql`SELECT
  station_id, count(distinct last_reported)
FROM
  gaias
group by station_id`

display(Inputs.table(bins))
```
ghj

 ```js
// Import the CSV file from user uploads or a URL
const raw_data = FileAttachment("./data/new_data.csv").csv();


 ```

```js
const dams = FileAttachment("data/news.parquet").parquet();
display(Inputs.table(dams))

 
```
```js
// Load CSV data
// Load CSV data
display(Inputs.table(raw_data))
```
 
```js
// Create a line plot showing the rolling average
Inputs.table(raw_data, {columns:["hour_rounded", "interactions"], width: width < 400 ? width : 400})
```
 
```js
Inputs.radio(new Map([["Hourly (no smoothing)", 1] ,["Daily", 24], ["Weekly", 168], ["28-day period", 24 * 28]]), {value:1, label:"Rolling Average:"})
```
```js
import * as Plot from "npm:@observablehq/plot";
 
const facet_options = new Map(["Hour", "Day", "Weekend", "Week", "Month", "Quarter", "None"].map(d => [d, d.toLowerCase()]))
 
 
 
const x_facet = Inputs.radio(facet_options, {
  label: "Break out Horizontally by:",
  value: "quarter"
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
  return `Avg. Demand: ${avg} MWh \n` +
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

