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
// MODULES FOR PROCESSING DATA
// -----
function convertLogtoGraph(d, groupBy, xAccessor, yAccessor, idAccessor){
    let graph = [{type: "directed"}]
    let nodes = d.map((object, index) => ({
        ...object,
        id: String('n' + index)
    }));
    let edges = deriveDFRelations(nodes, groupBy, xAccessor, yAccessor, idAccessor);
    return { 'graph': graph, 'nodes': nodes, 'edges': edges };
};

function deriveDFRelations(d, groupBy, xAccessor, yAccessor, idAccessor){
    const eventgroups = d3.group(d, groupBy);
    const traces = getUniqueValues(d, groupBy);
    let dirfol = [];
    let edgeId = 0;

    // Define all directly follows relation over each entity-instance
    for (let i = 0; i < traces.length; i++){
        let sortedTrace = eventgroups.get(traces[i]).sort((a, b) => xAccessor(a) - xAccessor(b));
        for (let j = 0; j < sortedTrace.length - 1; j++) {
            let currentSource = sortedTrace[j];
            let currentTarget = sortedTrace[j + 1];

            let source = idAccessor(currentSource);
            let target = idAccessor(currentTarget);
            // TODO: Might need to create a coordinate mapping function for this instead
            let source_coordinates = [xAccessor(currentSource), yAccessor(currentSource)];
            let target_coordinates = [xAccessor(currentTarget), yAccessor(currentTarget)];
            let entity = groupBy(currentSource);
            dirfol.push({ 
                id: `e${edgeId++}`, 
                source: source, target: target, 
                source_coordinates: source_coordinates, target_coordinates: target_coordinates,
                entity: entity });
        };
    };
    return dirfol;
};

function getUniqueValues(d, accessor, reverse = true) {
    if (reverse) {
        return [...new Set(d.map(accessor))].sort().reverse();
    } else {
        return [...new Set(d.map(accessor))].sort();
    }
};

function sortStringArrayByStartNumber (arr, descending = false) {
    const sortedArr = arr.slice().sort((a, b) => {
        const [numA, strA = ""] = a.split(/_(.*)/s);
        const [numB, strB = ""] = b.split(/_(.*)/s);

        const intA = parseInt(numA, 10);
        const intB = parseInt(numB, 10);

        return intA !== intB
            ? intA - intB
            : strA.localeCompare(strB)
    });

    return descending ? sortedArr.reverse() : sortedArr;
};

export { convertLogtoGraph, deriveDFRelations, getUniqueValues, sortStringArrayByStartNumber };