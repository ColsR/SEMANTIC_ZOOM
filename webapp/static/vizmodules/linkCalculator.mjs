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
// DEFINE LINKS FOR GRAPHS
// -----

function defineLinkVertical(xScale, yScale, options = {}) {
    const {
        curve = d3.curveBumpY,
        xProject = (value) => xScale(value),
        yProject = (value) => yScale(value),
    } = options;
    return d3.linkVertical(curve)
        .source(d => d.source_coordinates)
        .target(d => d.target_coordinates)
        .x(d => xProject(d[0]))
        .y(d => yProject(d[1]))
}

function defineLinkBezier(xScale, yScale, options = {}) {
    const {
        curveStrength = 0.3,
        curveOffset = 0,
        xProject = (value) => xScale(value),
        yProject = (value) => yScale(value),
    } = options;
    return function linkBezier(d) {
        // Calculate the source and target coordinates
        const [sourceX, sourceY] = [xProject(d.source_coordinates[0]), yProject(d.source_coordinates[1])];
        const [targetX, targetY] = [xProject(d.target_coordinates[0]), yProject(d.target_coordinates[1])];
        const verticalMidPointY = sourceY + (targetY - sourceY) * curveStrength - curveOffset;
        
        return `M${sourceX},${sourceY} C${sourceX},${verticalMidPointY} ${targetX},${verticalMidPointY} ${targetX},${targetY}`;
    }
        
}

export { defineLinkVertical, defineLinkBezier };