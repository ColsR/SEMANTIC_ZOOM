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
// SCALES
// -----

import {sortStringArrayByStartNumber} from "../utils/processData.mjs";

const SCALE = (function () {
    function categories (categories, dimensions, { sort = true, vertical = true } = {}) {
        const domain = sort 
            ? sortStringArrayByStartNumber(categories, true)
            : categories;
        const range = vertical 
            ? [dimensions.ctrHeight, 0]
            : [0, dimensions.ctrWidth];
        
        return d3.scalePoint()
        .domain(domain)
        .range(range)
        .padding(1);
    }  


    function linear (domain, dimensions, { vertical = true } = {}) {
        const range = vertical 
            ? [dimensions.ctrHeight, 0]
            : [0, dimensions.ctrWidth];
        //function scalewrapper()
        return d3.scaleLinear()
            .domain(domain)
            .range(range)
            .clamp(true);

        //return scaleWrapper;
    }



    function timeUTC (domain, dimensions, { vertical = true } = {}) {
        const range = vertical 
            ? [dimensions.ctrHeight, 0]
            : [0, dimensions.ctrWidth];
        return d3.scaleTime()
            .domain(domain)
            .range(range);
    }

    return {
        categories,
        linear,
        timeUTC
    };
})();

export { SCALE };