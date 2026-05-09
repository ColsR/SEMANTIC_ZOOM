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

import {edges, nodes} from "../utils/parsers.mjs";
import {getAccessors} from "../utils/parserGenerator.mjs";

let tooltipDocumentClickHandler = null;
let tooltipDocumentKeydownHandler = null;

function normalizeCoordinate(value) {
    if (value instanceof Date) {
        return `date:${value.getTime()}`;
    }

    if (typeof value === "number") {
        return `num:${Number.isFinite(value) ? value.toFixed(3) : String(value)}`;
    }

    if (value === null) return "null";
    if (value === undefined) return "undefined";

    return `${typeof value}:${String(value)}`;
}

function escapeHtml(value) {
    return String(value)
        .replace(/&/g, "&amp;")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;")
        .replace(/"/g, "&quot;")
        .replace(/'/g, "&#39;");
}

function formatTooltipValue(value) {
    if (value instanceof Date) {
        return d3.timeFormat("%Y-%m-%d %H:%M:%S")(value);
    }

    if (value === null || value === undefined || value === "") {
        return "-";
    }

    return escapeHtml(value);
}

function buildTooltipHtml(eventsAtPoint, accessors) {
    const eventLabel = eventsAtPoint.length === 1 ? "Event" : "Events";
    let html = `<div class="tooltip-title">${eventsAtPoint.length} ${escapeHtml(eventLabel)} an dieser Position</div>`;

    eventsAtPoint.forEach((event, index) => {
        html += `<div class="tooltip-entry">`;
        html += `<div class="tooltip-entry-title">Event ${index + 1}</div>`;

        for (const [key, accessor] of Object.entries(accessors)) {
            html += `<div class="tooltip-row"><b>${escapeHtml(key)}:</b> ${formatTooltipValue(accessor(event))}</div>`;
        }

        html += `</div>`;
    });

    return html;
}

async function renderInstanceGraph(graphData, link, container, xAccessor, xScale, yAccessor, yScale, options = {}) {
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
        xProject = (value) => xScale(value),
        yProject = (value) => yScale(value),
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
            yProject(d.source_coordinates[1]) > yProject(d.target_coordinates[1])
                ? classNameEdgeUp
                : classNameEdgeDown
            );

    // Draw events

    const tooltip = d3.select("body")
      .selectAll("div.tooltip")
      .data([null])
      .join("div")
      .attr("id", "tooltip")
      .attr("class", "tooltip")
      .style("position", "absolute")
      .style("visibility", "hidden");

    tooltip.on("click", (event) => {
        event.stopPropagation();
    });

    const events = ctrInstance.append('g')
        .attr("class", classNameNodes)
    const accessors = await getAccessors();
    const getPositionKey = (node) => `${normalizeCoordinate(xProject(xAccessor(node)))}|${normalizeCoordinate(yProject(yAccessor(node)))}`;
    const graphNodes = nodes(graphData).map((node) => ({
        ...node,
        __positionKey: getPositionKey(node)
    }));
    const nodesByPosition = d3.group(graphNodes, (node) => node.__positionKey);

    let tooltipPinned = false;

    const updateTooltipPosition = (event) => {
        tooltip
            .style("top", (event.pageY + 10) + "px")
            .style("left", (event.pageX + 10) + "px");
    };

    const updateHoverHighlight = (positionKey) => {
        events.selectAll('circle')
            .classed("event-circle-hovered", node => node.__positionKey === positionKey);
    };

    const hideTooltip = () => {
        tooltipPinned = false;
        tooltip
            .style("visibility", "hidden")
            .attr("data-pinned", null)
            .html("");
        events.selectAll('circle').classed("event-circle-hovered", false);
    };

    const showTooltipForNode = (event, node, pinned = false) => {
        const hoveredKey = node.__positionKey;
        const eventsAtPoint = nodesByPosition.get(hoveredKey) ?? [node];

        tooltipPinned = pinned;
        tooltip
            .attr("data-pinned", pinned ? "true" : null)
            .style("visibility", "visible")
            .html(buildTooltipHtml(eventsAtPoint, accessors));

        updateHoverHighlight(hoveredKey);
        updateTooltipPosition(event);
    };

    if (tooltipDocumentClickHandler) {
        document.removeEventListener("click", tooltipDocumentClickHandler);
    }
    if (tooltipDocumentKeydownHandler) {
        document.removeEventListener("keydown", tooltipDocumentKeydownHandler);
    }

    tooltipDocumentClickHandler = (event) => {
        if (!tooltipPinned) return;

        const tooltipNode = tooltip.node();
        if (tooltipNode && tooltipNode.contains(event.target)) return;
        if (event.target instanceof Element && event.target.closest(`.${classNameNode}`)) return;

        hideTooltip();
    };

    tooltipDocumentKeydownHandler = (event) => {
        if (event.key === "Escape") {
            hideTooltip();
        }
    };

    document.addEventListener("click", tooltipDocumentClickHandler);
    document.addEventListener("keydown", tooltipDocumentKeydownHandler);

    events.selectAll('circle')
        .data(graphNodes)
        .join('circle')
        .attr('id', d => `node-${d.id}`) // keys to find these elements
        .attr('cx', d => xProject(xAccessor(d)))
        .attr('cy', d => yProject(yAccessor(d)))
        .attr('r', 4)
        .attr('class', classNameNode)
        .attr('data-position-key', d => d.__positionKey)
        .on("mouseover", function(event, d) {
            if (!tooltipPinned) {
                showTooltipForNode(event, d, false);
            }
        })
        .on("mousemove", function(event) {
            if (!tooltipPinned) {
                updateTooltipPosition(event);
            }
        })
        .on("mouseout", function() {
            if (!tooltipPinned) {
                hideTooltip();
            }
        })
        .on("click", function(event, d) {
            event.stopPropagation();
            showTooltipForNode(event, d, true);
        })
    ;
}

export { renderInstanceGraph };