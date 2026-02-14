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
// PARSERS
// -----

// Access and parse data attributes
const parseDate = d3.isoParse;
const idAccessor = (d) => d.id;
//const timeAccessor = (d) => parseDate(d.time_abstracted);
const timeAccessor = (d) => parseDate(d.timestamps);
//const timeAccessor = (d) => parseFloat(d.timestamp_relative_seconds)  / 86400; // 86400 seconds in a day
const actAccessor = (d) => d.activity;
const caseAccessor = (d) => d.case; //parseInt(d.case)
const resAccessor = (d) => d.resources;
const nodes = (d) => d.nodes;
const edges = (d) => d.edges;

export {
  idAccessor,
  timeAccessor,
  actAccessor,
  caseAccessor,
  resAccessor,
  nodes,
  edges,
  parseDate};