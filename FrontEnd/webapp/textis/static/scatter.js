// text IS scatter plot
function textisscatterd3(data, targetDiv) {
    var chartDivwidth = $(targetDiv).width();

    var margin = {top: 25, right: 100, bottom: 30, left: 50},
        width = chartDivwidth - margin.left - margin.right,
        height = 700 - margin.top - margin.bottom;

    /*
     * value accessor - returns the value to encode for a given data object.
     * scale - maps value to a visual display encoding, such as a pixel position.
     * map function - maps from data value to display value
     * axis - sets up axis
     */

// setup x
    var xValue = function (d) {
            return d.size;
        }, // data -> value
        xScale = d3.scale.log().base(2).range([0, width]), // value -> display
        xMap = function (d) {
            return xScale(xValue(d));
        }, // data -> display
        xAxis = d3.svg.axis().scale(xScale).orient("bottom").tickFormat(d3.format(".2f"));

// setup y
    var yValue = function (d) {
            return d.edge;
        }, // data -> value
        yScale = d3.scale.linear().range([height, 0]), // value -> display
        yMap = function (d) {
            return yScale(yValue(d));
        }, // data -> display
        yAxis = d3.svg.axis().scale(yScale).orient("left");

// setup fill color
    var cValue = function (d) {
            return d.letter;
        };

    var svg = d3.select(targetDiv).append("svg")
        .attr("width", width + margin.left + margin.right)
        .attr("height", height + margin.top + margin.bottom)
        .append("g")
        .attr("transform", "translate(" + margin.left + "," + margin.top + ")");


    // don't want dots overlapping axis, so add in buffer to data domain
    xScale.domain([d3.min(data, xValue), d3.max(data, xValue) + 1]);
    yScale.domain([0.35, d3.max(data, yValue)]);

    // x-axis
    svg.append("g")
        .attr("class", "x scatteraxis")
        .attr("transform", "translate(0," + height + ")")
        .call(xAxis)
        .append("text")
        .attr("class", "label")
        .attr("x", width)
        .attr("y", -6)
        .style("text-anchor", "end")
        .text("Count/Add");

    // y-axis
    svg.append("g")
        .attr("class", "y scatteraxis")
        .call(yAxis)
        .append("text")
        .attr("class", "label")
        .attr("transform", "rotate(-90)")
        .attr("y", 6)
        .attr("dy", ".71em")
        .style("text-anchor", "end")
        .text("Association Strength");

    // draw dots
    var chart = svg.selectAll(".dot")
        .data(data)
        .enter();


    chart.append("text")
        .attr("class", "scattertext")
        .text(function(d) {
            $(this).attr("id", "scatter_" + d.letter.replace(/\s+/g, '_'));

            if(d.letter.endsWith('**')) {
                var fixedLetter = d.letter.substring(0, d.letter.length - 2);
                $(this).addClass("selectedword");
                return fixedLetter;
            }
            return d.letter;
        })
        .attr("x", xMap)
        .attr("y", yMap)
        .attr("dy", "-.55em");

    chart.append("circle")
        .attr("class", "dot")
        .attr("r", 3.5)
        .attr("cx", xMap)
        .attr("cy", yMap)
        .on("mouseover", handleMouseOver)
        .on("mouseout", handleMouseOut);
       ;
     // Create Event Handlers for mouse
      function handleMouseOver(d, i) {  // Add interactivity

            // Use D3 to select element, change color and size
            d3.select(this).attr({
              r: 5
            });

            var letter = d.letter;
            if(d.letter.endsWith('**')) {
                letter = d.letter.substring(0, d.letter.length - 2);
            }
            // Specify where to put label of text
            d3.selectAll("#scatter_" + letter.replace(/\s+/g, '_')).attr("class", "scattertext_hover");
          }

      function handleMouseOut(d, i) {
            // Use D3 to select element, change color back to normal
            d3.select(this).attr({
              r: 3.5
            });

            var letter = d.letter;
            if(d.letter.endsWith('**')) {
                letter = d.letter.substring(0, d.letter.length - 2);
            }
            d3.selectAll("#scatter_" + letter.replace(/\s+/g, '_')).attr("class", "scattertext");
          }
};