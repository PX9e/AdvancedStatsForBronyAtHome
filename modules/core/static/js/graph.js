function graphA(project_stat, property) {
    var vis = d3.select("#graph_area").append("svg");
    var w = document.getElementById('graph_area').offsetWidth;
    console.log(w);
    var h = w * 0.75;
    console.log(h);
    vis.attr("width", w)
        .attr("height", h);
    vis.text("test").select("#graph_area");


    var y = d3.scale.linear()
        .domain([d3.min(project_stat, function(d) { return d[property]; }), d3.max(project_stat, function(d) { return d[property]; })])
        .range([20, h-10]);

    var x = d3.scale.linear()
        .domain([d3.min(project_stat, function(d) { return d.date; }), d3.max(project_stat, function(d) { return d.date; })])
        .range([10, w-10]);

    var node = vis.selectAll("circle.node")
        .data(project_stat)
        .enter().append("g")
        .attr("class", "node");


    var xAxis = d3.svg.axis()
        .ticks(5)
        .scale(x)
        .orient("bottom");


    vis.append("g")
        .attr("class", "x axis")
        .attr("transform", "translate(0," + (h-20) + ")")
        .call(xAxis);

    node.append("svg:circle")
        .attr("cx", function(d) { return x(d.date); })
        .attr("cy", function(d) { return y(d[property]); })
        .attr("r", "3px")
        .attr("fill", "blue");


    vis.selectAll("circle.nodes")
        .data(project_stat)
        .enter()
        .append("svg:circle")
        .attr("cx", function(d) { return x(d.date); });
}