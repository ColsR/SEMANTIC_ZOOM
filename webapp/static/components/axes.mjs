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
// AXES DRAWING
// -----

function drawAxis(container, scale, orientation, dimensions, options = {}) {

    // Axis initialization
    const {
        className = `${orientation}-axis`,
        axisLabel,
        labelDistance = 0,
        labelRotationDegree = 0,
        ticks,
        tickFormat,
        tickPadding,
        opacity = 1,
        removeDomain = false,
        tickRotationDegree = 0,
    } = options;

    // Create the axis
    let axisGenerator = {
        left: d3.axisLeft,
        right: d3.axisRight,
        top: d3.axisTop,
        bottom: d3.axisBottom
    }[orientation];
    if (!axisGenerator) {
        throw new Error("Invalid orientation. Use 'left', 'right', 'top', or 'bottom'.");
    }
    const axis = axisGenerator(scale);
    if (ticks) axis.ticks(ticks);
    if (tickPadding) axis.tickPadding(tickPadding);
    if (tickFormat) axis.tickFormat(tickFormat);

    // Set axis position
    const translate = {
        left: `translate(0, 0)`,
        right: `translate(${dimensions.ctrWidth}, 0)`,
        top: `translate(0, 0)`,
        bottom: `translate(0, ${dimensions.ctrHeight})`
    }[orientation];

    // Draw the axis
    const axisGroup = container.append('g')
        .attr('class', className)
        .attr("transform", translate)
        .call(axis);

    // Conditionally remove the domain
    if (removeDomain) {
        axisGroup.select(".domain").remove();
    }

    if (tickRotationDegree) {
        axisGroup.selectAll(".tick text")
            .attr("transform", `rotate(${tickRotationDegree})`)
            .style("text-anchor", tickRotationDegree === 90 ? "start" : "middle")
            .attr("dx", tickRotationDegree === 90 ? "0.5em" : "0")
            .attr("dy", tickRotationDegree === 90 ? "-0.5em" : "0");
    }

    // Add axis label
    if (axisLabel) {
        // Predefined label positions per orientation
        const labelPos = {
            bottom: {
                x: dimensions.ctrWidth / 2,
                y: dimensions.margin.bottom + labelDistance,
                rotation: labelRotationDegree,
                anchor: 'middle'
            },
            top: {
                x: dimensions.ctrWidth / 2,
                y: -dimensions.margin.top + labelDistance,
                rotation: labelRotationDegree,
                anchor: 'middle'
            },
            left: {
                x: -dimensions.ctrHeight / 2,
                y: dimensions.margin.left + labelDistance,
                rotation: labelRotationDegree || -90,
                anchor: 'middle'
            },
            right: {
                x: dimensions.ctrHeight / 2,
                y: dimensions.ctrWidth + labelDistance, // unlikely use case
                rotation: labelRotationDegree || +90,
                anchor: 'middle'
            }
        }[orientation];

        const label = axisGroup.append('text')
            .attr('x', labelPos.x)
            .attr('y', labelPos.y)
            .attr('fill', 'black')
            .style('text-anchor', labelPos.anchor)
            .style('opacity', opacity)
            .text(axisLabel);

        if (labelPos.rotation !== 0) {
            label.attr('transform', `rotate(${labelPos.rotation}, ${labelPos.x}, ${labelPos.y})`);
        }
    }

    return axisGroup;
}

export { drawAxis };