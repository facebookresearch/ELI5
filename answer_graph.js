var color = "gray";

// Generate a 1000 data points using normal distribution with mean=20, deviation=5
// var values = d3.range(1000).map(d3.random.normal(20, 5));
d3.json("answer_length_data.json", function(rawData) {
  values = rawData["distribution"]
  d3.json("answer_markers.json", function(markers) {    
    var margin = {top: 20, right: 30, bottom: 50, left: 60},
        width = 560 - margin.left - margin.right,
        height = 300 - margin.top - margin.bottom;

  var tip = d3.tip()
      .attr("class", "d3-tip")
      .style("max-width", width - 100)
      .offset([-10, 0])
      .html(tooltipHTML);

    var max = d3.max(values);
    var min = d3.min(values);
    var x = d3.scale.log()
          .base(Math.E)
          .domain([min, max])
          .range([0, width]);

    // Generate a histogram using twenty uniformly-spaced bins.
    var histogramBins = d3.layout.histogram()
        .bins(x.ticks(200))
        (values);

    var yMax = d3.max(histogramBins, function(d){return d.length});
    var yMin = d3.min(histogramBins, function(d){return d.length});

    var y = d3.scale.linear()
        .domain([0, yMax*1.2])
        .range([height, 0]);

    var xAxis = d3.svg.axis()
        .scale(x)
        .orient("bottom");

    var yAxis = d3.svg.axis()
        .scale(y)
        .orient("left");

    var svg = d3.select("#answergraph")
        .append("div")
        .classed("svg-container", true)
        // .classed("ui", true)
        // .classed("basic", true)
        // .classed("segment", true)
        .append("svg")
        .attr("preserveAspectRatio", "xMinYMin meet")
        .attr("viewBox", "0 0 600 400")
        .classed("svg-content-responsive", true)
        // .attr("width", width + margin.left + margin.right)
        // .attr("height", height + margin.top + margin.bottom)
      .append("g")
        .attr("transform", "translate(" + margin.left + "," + margin.top + ")");

    svg.call(tip)

    var line = d3.svg.line()
        .interpolate('basis')
        .x(function(d) { return x(d.x + d.dx / 2); })
        .y(function(d) { return y(d.y); });

    svg.datum(histogramBins)

    svg.append('path')
        .attr('class', 'median-line')
        .attr('d', line)

    svg.append("g")
        .attr("class", "x axis")
        .attr("transform", "translate(0," + height + ")")
        .call(xAxis);

    svg.append("g")
        .attr("class", "y axis")
        .call(yAxis);

    svg.append("text")
        .attr("transform",
              "translate(" + (width / 2) + " ," +
                             (height + margin.top + 20) + ")")
        .style("text-anchor", "middle")
        .text("Log length")

    markers.forEach(function(marker) {
      addMarker(marker, svg, tip, height, x);
    });
  });
});

function tooltipHTML(marker) {
  return "<b>Question</b>: " + marker.question + "<br><br><b>Answer</b>: " + marker.answer ;
}

function addMarker(marker, svg, tip, chartHeight, x) {
  var radius = 10,
      xPos = x(marker.length) - radius - 3,
      yPosStart = chartHeight - radius - 3,
      yPosEnd = marker.y + radius - 3;

  var markerG = svg.append('g')
    .attr('class', 'marker client')
    .attr('transform', 'translate(' + xPos + ', ' + yPosStart + ')')
    .attr('opacity', 0);

  markerG.transition()
    .duration(1000)
    .attr('transform', 'translate(' + xPos + ', ' + yPosEnd + ')')
    .attr('opacity', 1);
    
  markerG.append('circle')
    .datum(marker)
    .attr('class', 'marker-bg')
    .attr('cx', radius)
    .attr('cy', radius)
    .attr('r', radius)
    .on("mouseover", tip.show)
    .on("mouseout", tip.hide);

  markerG.append('path')
    .attr('d', 'M' + radius + ',' + (chartHeight-yPosStart) + 'L' + radius + ',' + (chartHeight-yPosStart))
    .transition()
      .duration(1000)
      .attr('d', 'M' + radius + ',' + (chartHeight-yPosEnd) + 'L' + radius + ',' + (radius*2));

  markerG.append('text')
    .attr('x', radius)
    .attr('y', radius*0.9)

  markerG.append('text')
    .attr('x', radius)
    .attr('y', radius*1.5);
}