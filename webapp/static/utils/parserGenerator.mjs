
const parseDate = d3.isoParse;

const buildAccessors = (schema) => {
  const accessors = {};

  for (const [key, type] of Object.entries(schema.eventAttributes)) {
    console.log(`Building accessor for key: ${key}, type: ${type}`);
    let fn;
    if (type === "time") {
      fn = (d) => parseDate(d[key]);
    } else if (type === "number") {
      fn = (d) => +d[key];
    }
    else {
      fn = (d) => d[key];
    }
    fn.type = type;
    accessors[key] = fn;
  }

  return accessors;
};

async function getAccessors(){
    const response = await fetch("/api/attributes");
    let schema = await response.json();
    const accessors = buildAccessors(schema);
    console.log("Accessors built from schema:", accessors);
    return accessors;
}


export {getAccessors}
