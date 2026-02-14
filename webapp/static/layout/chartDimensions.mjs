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
// CHART DIMENSIONS
// -----

// Define chart dimensions
let dimensions = {
    width: 800, // default: 800
    height: 500, // default: 500
    margin: 
    {
        top: 50,
        bottom: 100,
        left: 230, //140 for standard // 230 for large activity names
        right: 50,
    }
};

    // Container dimensions
dimensions.ctrWidth = dimensions.width - dimensions.margin.left - dimensions.margin.right
dimensions.ctrHeight = dimensions.height - dimensions.margin.top - dimensions.margin.bottom

export { dimensions };