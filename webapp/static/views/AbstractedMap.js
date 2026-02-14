import {convertLogtoGraph, getUniqueValues} from "../utils/processData.mjs";
import {actAccessor, caseAccessor, idAccessor, nodes, parseDate, timeAccessor} from "../utils/parsers.mjs";
import {SCALE} from "../layout/scales.mjs";
import {dimensions} from "../layout/chartDimensions.mjs";
import {defineArrowHeads} from "../components/arrowheads.mjs";
import {defineLinkBezier, defineLinkVertical} from "../vizmodules/linkCalculator.mjs";
import {drawAxis} from "../components/axes.mjs";
import {CONTOURGRAPH} from "../charts/contourGraph.mjs";
import {renderInstanceGraph} from "../charts/instanceGraph.mjs";


export function ABSTRACTEDMAP(csvdata) {
    console.info("Drawing Test View");
    // Your test view drawing code here
    let currentContourBandwidth = 60;
    let currentContourThreshold = 3;
    let opacityLevelYAxis = 1;

    console.log("PARSING:" + parseDate("2010-12-30T14:32:00"));

    const data = convertLogtoGraph(csvdata, caseAccessor, timeAccessor, actAccessor, idAccessor);
    console.log("DATA is:" + data);
    console.log("Nodes are:" + nodes(data));

    let activities = getUniqueValues(nodes(data), actAccessor);
    //const xScale = SCALE.linear(d3.extent(nodes(data), timeAccessor), dimensions, { vertical: false });
    console.log("Extent of dates:", d3.extent(nodes(data), timeAccessor));
    const xScale = SCALE.timeUTC(d3.extent(nodes(data), timeAccessor), dimensions, { vertical: false });
    const yScale = SCALE.categories(activities, dimensions);

    const svg = d3.select('#chart')
        .append("svg")
        .attr("width", dimensions.width)
        .attr("height", dimensions.height)


        // Create marker points for arrowheads
    defineArrowHeads(svg);

    // Draw container
    const ctr = svg.append("g")
        .attr(
            "transform",
            `translate(${dimensions.margin.left}, ${dimensions.margin.top})`
        )

    // Draw edges for instance graph
    const linkInstance = defineLinkVertical(xScale, yScale);
    const linkBundled = defineLinkBezier(xScale, yScale);

    // == AXES ==
    // Draw x-axis
    /*
    drawAxis(ctr, xScale, 'bottom', dimensions, {
        className: 'x-axis',
        axisLabel: 'Relative time (in days)',
        labelDistance: -10,
        });
    */
    drawAxis(ctr, xScale, 'bottom', dimensions, {
    className: 'x-axis',
    axisLabel: 'Time',
    labelDistance: -10,
    tickFormat: d3.timeFormat("%Y-%m-%d %H:%M"),
    tickRotationDegree: 90,
    });
    // Draw y-axis
    drawAxis(ctr, yScale, 'left', dimensions, {
        className: 'y-axis',
        axisLabel: 'Activities',
        ticks: d3.max(nodes(data), caseAccessor),
        tickPadding: 15,
        removeDomain: true,      // remove the y-axis line domain
        opacity: opacityLevelYAxis
    });


    renderInstanceGraph(data, linkInstance, ctr, timeAccessor, xScale, actAccessor, yScale);
    console.log("end")

}