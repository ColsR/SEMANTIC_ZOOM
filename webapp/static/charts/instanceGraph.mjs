/*
SEAMLESS_ZOOM — A technique for seamless zooming between process models and process instances.
Copyright (C) 2025  Christoffer Rubensson

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU Affero General Public License as
published by the Free Software Foundation, either version 3 of the
License, or any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU Affero General Public License for more details.

You should have received a copy of the GNU Affero General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.

Website: https://hu-berlin.de/rubensson
E-Mail: {firstname.lastname}@hu-berlin.de
*/

// -----
// DRAW AN INSTANCE GRAPH
// -----

import { caseAccessor, actAccessor, timeAccessor, resAccessor, nodes, edges } from "../utils/parsers.mjs";

function renderInstanceGraph(graphData, link, container, xAccessor, xScale, yAccessor, yScale, options = {}) {
    // Graph initialization
    const {
        classNameGraph = "instance-graph",
        classNameNodes = "instance-nodes",
        classNameNode = "event-circle",
        classNameEdges = "instance-edges",
        classNameEdgeUp = "link link-up",
        classNameEdgeDown = "link link-down",
        opacityGraph = 1,
        opacityStroke = 0.6,
        strokeWidth = 1.0,
    } = options;


    const ctrInstance = container.append('g')
        .attr('class', classNameGraph)
        .style('opacity', opacityGraph)
    
    const edge = ctrInstance.append('g')
        .attr('class', classNameEdges)
        .attr('fill', 'none')
        //.attr('stroke', '#feb24c')
        .attr('stroke-opacity', opacityStroke)
        .attr('stroke-width', strokeWidth)
    edge.selectAll()
        .data(edges(graphData))
        .join('path')
        .attr('id', d => `edge-${d.id}`)
        .attr('d', link)
        .attr('class', d =>
            yScale(d.source_coordinates[1]) > yScale(d.target_coordinates[1])
                ? classNameEdgeUp
                : classNameEdgeDown
            );

    // Draw events

    const tooltip = d3.select("body")
      .append("div")
      .attr("class", "tooltip")
      .style("position", "absolute")
      .style("visibility", "hidden")
      .style("background", "white")
      .style("border", "1px solid #ccc")
      .style("padding", "5px")
      .style("font-size", "12px");

    const events = ctrInstance.append('g')
        .attr("class", classNameNodes)

    events.selectAll('circle')
        .data(nodes(graphData))
        .join('circle')
        .attr('id', d => `node-${d.id}`) // keys to find these elements
        .attr('cx', d => xScale(xAccessor(d)))
        .attr('cy', d => yScale(yAccessor(d)))
        .attr('r', 4)
        .attr('class', classNameNode)
        .attr('case', caseAccessor)
        .attr('activity', actAccessor)
        .attr('timestamp', timeAccessor)
        .attr('resource', resAccessor)
        .on("mouseover", function(event, d) {
            d3.select(this).classed("event-circle-hovered", true)
            tooltip
              .style("visibility", "visible")
              .html(`
                <b>Activity:</b> ${actAccessor(d)}<br>
                <b>Case:</b> ${caseAccessor(d)}<br>
                <b>Resource:</b> ${resAccessor(d)}<br>
                <b>Timestamp:</b> ${timeAccessor(d)}
              `);

        })
        .on("mousemove", function(event) {
            tooltip
              .style("top", (event.pageY + 10) + "px")
              .style("left", (event.pageX + 10) + "px");
        })
        .on("mouseout", function() {
            d3.select(this).classed("event-circle-hovered", false)
            tooltip.style("visibility", "hidden");
        })
    ;
}

export { renderInstanceGraph };