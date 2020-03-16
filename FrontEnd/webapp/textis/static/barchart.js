function newBarChart(bardata, barChart, cbar1, cbar2, genTwoBars = false) {
    var twoBars = genTwoBars;
    var data = [],
        svg,
        defs,
        gBrush,
        brush,
        main_xScale,
        mini_xScale,
        main_yScale,
        mini_yScale,
        main_yZoom,
        main_xAxis,
        main_yAxis,
        mini_width,
        textScale;

    data = bardata;

    /* sort data */
    data.sort(function(a, b) {
        return d3.descending(a.col1, b.col1)
    })

    init();

    function init() {
        /////////////////////////////////////////////////////////////
        ///////////////// Set-up SVG and wrappers ///////////////////
        /////////////////////////////////////////////////////////////

        //Added only for the mouse wheel
        var zoomer = d3.behavior.zoom()
            .on("zoom", null);

        var chartDivwidth = $("#" + barChart).width();

        var mini_margin = {top: 10, right: 10, bottom: 10, left: 10},
            mini_height = 400 - mini_margin.top - mini_margin.bottom;
        mini_width = 100 - mini_margin.left - mini_margin.right;

        var main_margin = {top: 0, right: 10, bottom: 30, left: 10},
            main_width = chartDivwidth - main_margin.left - main_margin.right - mini_width,
            main_height = 400 - main_margin.top - main_margin.bottom;


        svg = d3.select("#" + barChart).append("svg")
            .attr("class", "svgWrapper" + barChart)
            .attr("width", main_width + main_margin.left + main_margin.right + mini_width + mini_margin.left + mini_margin.right)
            .attr("height", main_height + main_margin.top + main_margin.bottom)
            .call(zoomer)
            .on("wheel.zoom", scroll)
            //.on("mousewheel.zoom", scroll)
            //.on("DOMMouseScroll.zoom", scroll)
            //.on("MozMousePixelScroll.zoom", scroll)
            //Is this needed?
            .on("mousedown.zoom", null)
            .on("touchstart.zoom", null)
            .on("touchmove.zoom", null)
            .on("touchend.zoom", null);

        var mainGroup = svg.append("g")
            .attr("class", "mainGroupWrapper" + barChart)
            .attr("transform", "translate(" + main_margin.left + "," + main_margin.top + ")")
            .append("g") //another one for the clip path - due to not wanting to clip the labels
            .attr("clip-path", "url(#clip)")
            .style("clip-path", "url(#clip)")
            .attr("class", "mainGroup" + barChart);

        var miniGroup = svg.append("g")
            .attr("class", "miniGroup" + barChart)
            .attr("transform", "translate(" + (main_margin.left + main_width + main_margin.right + mini_margin.left) + "," + mini_margin.top + ")");

        var brushGroup = svg.append("g")
            .attr("class", "brushGroup" + barChart)
            .attr("transform", "translate(" + (main_margin.left + main_width + main_margin.right + mini_margin.left) + "," + mini_margin.top + ")");

        /////////////////////////////////////////////////////////////
        ////////////////////// Initiate scales //////////////////////
        /////////////////////////////////////////////////////////////

        main_xScale = d3.scale.linear().range([-1, main_width]);
        mini_xScale = d3.scale.linear().range([-1, mini_width]);

        main_yScale = d3.scale.ordinal().rangeBands([-1, main_height], 0.4, 0);
        mini_yScale = d3.scale.ordinal().rangeBands([-1, mini_height], 0.4, 0);

        //Based on the idea from: http://stackoverflow.com/questions/21485339/d3-brushing-on-grouped-bar-chart
        main_yZoom = d3.scale.linear()
            .range([0, main_height])
            .domain([0, main_height]);

        //Create x axis object
        main_xAxis = d3.svg.axis()
            .scale(main_xScale)
            .orient("bottom")
            .ticks(4)
            //.tickSize(0)
            .outerTickSize(0);

        //Add group for the x axis
        d3.select(".mainGroupWrapper" + barChart)
            .append("g")
            .attr("class", "x axis")
            .attr("transform", "translate(" + 0 + "," + (main_height + 5) + ")");

        //Create y axis object
        main_yAxis = d3.svg.axis()
            .scale(main_yScale)
            .orient("right")
            .tickSize(0)
            .outerTickSize(0);

        //Add group for the y axis
        mainGroup.append("g")
            .attr("class", "y axis")
            .attr("transform", "translate(-5,0)");

        /////////////////////////////////////////////////////////////
        /////////////////////// Update scales ///////////////////////
        /////////////////////////////////////////////////////////////

        //Update the scales
        main_xScale.domain([0, d3.max(data, function (d) {
            return d.col1;
        })]);
        mini_xScale.domain([0, d3.max(data, function (d) {
            return d.col1;
        })]);
        main_yScale.domain(data.map(function (d) {
            return d.letter;
        }));
        mini_yScale.domain(data.map(function (d) {
            return d.letter;
        }));

        //Create the visual part of the y axis
        d3.select(".mainGroup" + barChart).select(".y.axis").call(main_yAxis);

        /////////////////////////////////////////////////////////////
        ///////////////////// Label axis scales /////////////////////
        /////////////////////////////////////////////////////////////

        textScale = d3.scale.linear()
            .domain([15, 50])
            .range([12, 6])
            .clamp(true);

        /////////////////////////////////////////////////////////////
        ///////////////////////// Create brush //////////////////////
        /////////////////////////////////////////////////////////////

        //What should the first extent of the brush become - a bit arbitrary this
        var brushExtent = Math.max(1, Math.min(20, Math.round(data.length * 0.2)));

        brush = d3.svg.brush()
            .y(mini_yScale)
            .extent([mini_yScale(data[0].letter), mini_yScale(data[brushExtent].letter)])
            .on("brush", brushmove);

        //Set up the visual part of the brush
        gBrush = d3.select(".brushGroup" + barChart).append("g")
            .attr("class", "brush")
            .call(brush);

        gBrush.selectAll(".resize")
            .append("line")
            .attr("x2", mini_width);

        gBrush.selectAll(".resize")
            .append("path")
            .attr("d", d3.svg.symbol().type("triangle-up").size(20))
            .attr("transform", function (d, i) {
                return i ? "translate(" + (mini_width / 2) + "," + 4 + ") rotate(180)" : "translate(" + (mini_width / 2) + "," + -4 + ") rotate(0)";
            });

        gBrush.selectAll("rect")
            .attr("width", mini_width);

        //On a click recenter the brush window
        //gBrush.select(".background")
        //  .on("mousedown.brush", brushcenter)
        //  .on("touchstart.brush", brushcenter);

        defs = svg.append("defs")

        //Add the clip path for the main bar chart
        defs.append("clipPath")
            .attr("id", "clip")
            .append("rect")
            .attr("x", -main_margin.left)
            .attr("width", main_width + main_margin.left)
            .attr("height", main_height);

        /////////////////////////////////////////////////////////////
        /////////////// Set-up the mini bar chart ///////////////////
        /////////////////////////////////////////////////////////////

        //The mini brushable bar
        //DATA JOIN
        var mini_bar = d3.select(".miniGroup" + barChart).selectAll(".bar1")
            .data(data, function (d) {
                return d.letter;
            });

        //UDPATE
        mini_bar
            .attr("class", "bar1")
            .attr("width", function (d) {
                return mini_xScale(d.col1);
            })
            .attr("y", function (d, i) {
                return mini_yScale(d.letter);
            })
            .attr("height", mini_yScale.rangeBand());

        //ENTER
        mini_bar.enter().append("rect")
            .attr("class", "bar1")
            .attr("x", 0)
            .attr("width", function (d) {
                return mini_xScale(d.col1);
            })
            .attr("y", function (d, i) {
                return mini_yScale(d.letter);
            })
            .attr("height", mini_yScale.rangeBand());

        //EXIT
        mini_bar.exit()
            .remove();

        //Start the brush
        gBrush.call(brush.event);

    }//init

    //Function runs on a brush move - to update the big bar chart
    function update() {

        /////////////////////////////////////////////////////////////
        ////////// Update the bars of the main bar chart ////////////
        /////////////////////////////////////////////////////////////

        //DATA JOIN
        var bar = d3.select(".mainGroup" + barChart).selectAll("." + cbar1)
            .data(data, function (d) {
                return d.letter;
            });

        //UPDATE
        bar
            .attr("y", function (d, i) {
                return main_yScale(d.letter) - 5;
            })
            .attr("height", main_yScale.rangeBand() + 10)
            .attr("x", -10)
            .transition().duration(50)
            .attr("width", function (d) {
                return main_xScale(d.col1);
            });

        //ENTER
        bar.enter().append("rect")
            .attr("class", cbar1)
            //.style("fill", "url(#gradient-rainbow-main)")
            .attr("y", function (d, i) {
                return main_yScale(d.letter) - 5;
            })
            .attr("height", main_yScale.rangeBand() + 10)
            .attr("x", -10)
            .transition().duration(50)
            .attr("width", function (d) {
                return main_xScale(d.col1);
            });

        //EXIT
        bar.exit()
            .remove();

        var bar = d3.select(".mainGroup" + barChart).selectAll("." + cbar2)
            .data(data, function (d) {
                return d.letter;
            });

        if (twoBars) {
            //UPDATE
            bar
                .attr("y", function (d, i) {
                    return main_yScale(d.letter);
                })
                .attr("height", main_yScale.rangeBand())
                .attr("x", -10)
                .transition().duration(50)
                .attr("width", function (d) {
                    return main_xScale(d.col2);
                });

            //ENTER
            bar.enter().append("rect")
                .attr("class", cbar2)
                //.style("fill", "url(#gradient-rainbow-main)")
                .attr("y", function (d, i) {
                    return main_yScale(d.letter);
                })
                .attr("height", main_yScale.rangeBand())
                .attr("x", -10)
                .transition().duration(50)
                .attr("width", function (d) {
                    return main_xScale(d.col2);
                });

            //EXIT
            bar.exit()
                .remove();
        }

    }//update

    /////////////////////////////////////////////////////////////
    ////////////////////// Brush functions //////////////////////
    /////////////////////////////////////////////////////////////

    //First function that runs on a brush move
    function brushmove() {

        var extent = brush.extent();

        //Which bars are still "selected"
        var selected = mini_yScale.domain()
            .filter(function (d) {
                return (extent[0] - mini_yScale.rangeBand() + 1e-2 <= mini_yScale(d)) && (mini_yScale(d) <= extent[1] - 1e-2);
            });
        //Update the colors of the mini chart - Make everything outside the brush grey
        d3.select(".miniGroup" + barChart).selectAll(".bar1")
            .style("fill", function (d, i) {
                return selected.indexOf(d.letter) > -1 ? "#FFF3CD" : "#e0e0e0";
            });
        //Update the colors of the mini chart - Make everything outside the brush grey
        d3.select(".miniGroup" + barChart).selectAll(".bar1")
            .style("fill", function (d, i) {
                return selected.indexOf(d.letter) > -1 ? "#FFF3CD" : "#e0e0e0";
            });

        //font size depends on the value of word count
        //Update the label size
        d3.selectAll(".y.axis text")
            .style("font-size", textScale(selected.length));

        /////////////////////////////////////////////////////////////
        ///////////////////// Update the axes ///////////////////////
        /////////////////////////////////////////////////////////////


        //Reset the part that is visible on the big chart
        var originalRange = main_yZoom.range();
        main_yZoom.domain(extent);

        //Update the domain of the x & y scale of the big bar chart
        main_yScale.domain(data.map(function (d) {
            return d.letter;
        }));
        main_yScale.rangeBands([main_yZoom(originalRange[0]), main_yZoom(originalRange[1])], 0.4, 0);

        //Update the y axis of the big chart
        d3.select(".mainGroup" + barChart)
            .select(".y.axis")
            .call(main_yAxis);

        //Find the new max of the bars to update the x scale
        var newMaxXScale = d3.max(data, function (d) {
            return d.col1;

            /*
            if scaling axes are needed
            if(selected.indexOf(d.letter) > -1) {
                if (d.col1 > d.col2)
                    return d.col1;
                else
                    return d.col2;
            }
            return 0;
            */
        });
        main_xScale.domain([0, newMaxXScale]);


        //Update the x axis of the big chart
        d3.select(".mainGroupWrapper" + barChart)
            .select(".x.axis")
            .transition().duration(50)
            .call(main_xAxis);

        //Update the big bar chart
        update();

    }//brushmove


    /////////////////////////////////////////////////////////////
    ///////////////////// Scroll functions //////////////////////
    /////////////////////////////////////////////////////////////

    function scroll() {

        //Mouse scroll on the mini chart
        var extent = brush.extent(),
            size = extent[1] - extent[0],
            range = mini_yScale.range(),
            y0 = d3.min(range),
            y1 = d3.max(range) + mini_yScale.rangeBand(),
            dy = d3.event.deltaY,
            topSection;

        if (extent[0] - dy < y0) {
            topSection = y0;
        } else if (extent[1] - dy > y1) {
            topSection = y1 - size;
        } else {
            topSection = extent[0] - dy;
        }

        //Make sure the page doesn't scroll as well
        d3.event.stopPropagation();
        d3.event.preventDefault();

        gBrush
            .call(brush.extent([topSection, topSection + size]))
            .call(brush.event);

    }//scroll
}
