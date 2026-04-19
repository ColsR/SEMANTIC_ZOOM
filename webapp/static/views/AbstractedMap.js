import {convertLogtoGraph, getUniqueValues} from "../utils/processData.mjs";
import {actAccessor, caseAccessor, idAccessor, nodes, parseDate, resAccessor, timeAccessor} from "../utils/parsers.mjs";
import {SCALE} from "../layout/scales.mjs";
import {dimensions} from "../layout/chartDimensions.mjs";
import {defineArrowHeads} from "../components/arrowheads.mjs";
import {defineLinkBezier, defineLinkVertical} from "../vizmodules/linkCalculator.mjs";
import {drawAxis} from "../components/axes.mjs";
import {CONTOURGRAPH} from "../charts/contourGraph.mjs";
import {renderInstanceGraph} from "../charts/instanceGraph.mjs";


export function ABSTRACTEDMAP(csvdata, x_accessor=timeAccessor, y_accessor=actAccessor) {
    console.info("Drawing Test View");

    // Your test view drawing code here
    let currentContourBandwidth = 60;
    let currentContourThreshold = 3;
    let opacityLevelYAxis = 1;

    console.log("PARSING:" + parseDate("2010-12-30T14:32:00"));

    const data = convertLogtoGraph(csvdata, caseAccessor, x_accessor, y_accessor, idAccessor);
    console.log("DATA is:" + data);
    console.log("Nodes are:" + nodes(data));

    const isNumericalAccessor = (accessor) => ["number", "numerical", "numeric", "relativetime"].includes(accessor?.type);
    const getFiniteNumericValues = (accessor) => nodes(data)
        .map((d) => +accessor(d))
        .filter(Number.isFinite);
    const NAN_SLOT_LABEL = "NaN";
    const NAN_SLOT_PADDING = 24;

    let activities = getUniqueValues(nodes(data), actAccessor);
    let y_values = getUniqueValues(nodes(data), y_accessor, false);
    console.log("Extent of dates:", d3.extent(nodes(data), timeAccessor));
    let xScale;
    let xValueToPixel;
    let hasNaNSlotOnXAxis = false;
    let xNaNSlotPosition = null;
    if (x_accessor.type === "time") {
        console.log("Using time scale for x-axis");
        xScale = SCALE.timeUTC(d3.extent(nodes(data), x_accessor), dimensions, { vertical: false });
        xValueToPixel = (value) => xScale(value);
    } else if (isNumericalAccessor(x_accessor)) {
        console.log("Using linear scale for x-axis");
        const xNumericValues = getFiniteNumericValues(x_accessor);
        const hasNaNValues = nodes(data).some((d) => !Number.isFinite(+x_accessor(d)));

        if (xNumericValues.length > 0) {
            const xDomain = d3.extent(xNumericValues);
            if (hasNaNValues) {
                // Keep a dedicated right slot for NaN while preserving a linear scale for numeric values.
                xScale = d3.scaleLinear()
                    .domain(xDomain)
                    .range([0, dimensions.ctrWidth - NAN_SLOT_PADDING])
                    .clamp(true);
                hasNaNSlotOnXAxis = true;
                xNaNSlotPosition = dimensions.ctrWidth;
                xValueToPixel = (value) => {
                    const numericValue = +value;
                    return Number.isFinite(numericValue) ? xScale(numericValue) : xNaNSlotPosition;
                };
            } else {
                xScale = SCALE.linear(xDomain, dimensions, { vertical: false });
                xValueToPixel = (value) => xScale(+value);
            }
        } else {
            xScale = SCALE.categories(getUniqueValues(nodes(data), x_accessor, false), dimensions, { vertical: false });
            xValueToPixel = (value) => xScale(value);
        }
    } else {
        console.log("Using categorical scale for x-axis");
        xScale = SCALE.categories(getUniqueValues(nodes(data), x_accessor, false), dimensions, { vertical: false });
        xValueToPixel = (value) => xScale(value);
    }
    let yScale;
    let yValueToPixel;
    let hasNaNSlotOnYAxis = false;
    let yNaNSlotPosition = null;
    if (isNumericalAccessor(y_accessor)) {
        console.log("Using linear scale for y-axis, because of numerical type");
        const yNumericValues = getFiniteNumericValues(y_accessor);
        const hasNaNValues = nodes(data).some((d) => !Number.isFinite(+y_accessor(d)));

        if (yNumericValues.length > 0) {
            const yDomain = d3.extent(yNumericValues);
            if (hasNaNValues) {
                // Keep a dedicated bottom slot for NaN while preserving a linear scale for numeric values.
                yScale = d3.scaleLinear()
                    .domain(yDomain)
                    .range([dimensions.ctrHeight - NAN_SLOT_PADDING, 0])
                    .clamp(true);
                hasNaNSlotOnYAxis = true;
                yNaNSlotPosition = dimensions.ctrHeight;
                yValueToPixel = (value) => {
                    const numericValue = +value;
                    return Number.isFinite(numericValue) ? yScale(numericValue) : yNaNSlotPosition;
                };
            } else {
                yScale = SCALE.linear(yDomain, dimensions, { vertical: true });
                yValueToPixel = (value) => yScale(+value);
            }
        } else {
            yScale = SCALE.categories(y_values, dimensions);
            yValueToPixel = (value) => yScale(value);
        }
    } else {
        console.log("Using categories scale for y-axis, as standard");
        yScale = SCALE.categories(y_values, dimensions);
        yValueToPixel = (value) => yScale(value);
    }


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
    const linkInstance = defineLinkVertical(xScale, yScale, {
        xProject: xValueToPixel,
        yProject: yValueToPixel
    });
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
    const xTickFormat = x_accessor.type === "time"
        ? d3.timeFormat("%Y-%m-%d %H:%M")
        : (d) => `${d}`;

    drawAxis(ctr, xScale, 'bottom', dimensions, {
    className: 'x-axis',
    axisLabel: 'Time',
    labelDistance: -10,
    tickFormat: xTickFormat,
    tickRotationDegree: 90,
    });

    if (hasNaNSlotOnXAxis && Number.isFinite(xNaNSlotPosition)) {
        const xAxisNaNSlot = ctr.append('g').attr('class', 'x-axis-nan-slot');
        xAxisNaNSlot.append('line')
            .attr('x1', xNaNSlotPosition)
            .attr('x2', xNaNSlotPosition)
            .attr('y1', dimensions.ctrHeight)
            .attr('y2', dimensions.ctrHeight + 6)
            .attr('stroke', 'currentColor');

        xAxisNaNSlot.append('text')
            .attr('x', xNaNSlotPosition)
            .attr('y', dimensions.ctrHeight + 9)
            .attr('dy', '0.71em')
            .style('text-anchor', 'start')
            .attr('transform', `rotate(90, ${xNaNSlotPosition}, ${dimensions.ctrHeight + 9})`)
            .text(NAN_SLOT_LABEL);
    }
    // Draw y-axis
    const yAxisOptions = {
        className: 'y-axis',
        axisLabel: 'Activities',
        tickPadding: 15,
        removeDomain: true,      // remove the y-axis line domain
        opacity: opacityLevelYAxis
    };

    if (isNumericalAccessor(y_accessor) && typeof yScale.ticks === 'function') {
        yAxisOptions.ticks = 8;
        yAxisOptions.tickFormat = d3.format('~g');
    }

    drawAxis(ctr, yScale, 'left', dimensions, yAxisOptions);

    if (hasNaNSlotOnYAxis && Number.isFinite(yNaNSlotPosition)) {
        const yAxisNaNSlot = ctr.append('g').attr('class', 'y-axis-nan-slot');
        yAxisNaNSlot.append('line')
            .attr('x1', -6)
            .attr('x2', 0)
            .attr('y1', yNaNSlotPosition)
            .attr('y2', yNaNSlotPosition)
            .attr('stroke', 'currentColor');

        yAxisNaNSlot.append('text')
            .attr('x', -9)
            .attr('y', yNaNSlotPosition)
            .attr('dy', '0.32em')
            .style('text-anchor', 'end')
            .text(NAN_SLOT_LABEL);
    }


    renderInstanceGraph(data, linkInstance, ctr, x_accessor, xScale, y_accessor, yScale, {
        xProject: xValueToPixel,
        yProject: yValueToPixel
    });
    console.log("end")

}