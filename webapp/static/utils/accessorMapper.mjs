import {actAccessor, resAccessor, timeAccessor} from "./parsers.mjs";


function getAccessor(accessorName) {
    switch (accessorName) {
        case "activity":
            return actAccessor;
        case "resource":
            return resAccessor;
        case "time":
            return timeAccessor;
        default:
            console.warn(`Unknown accessor name: ${accessorName}. Defaulting to activity accessor.`);
            return actAccessor;
    }
}


export {getAccessor};