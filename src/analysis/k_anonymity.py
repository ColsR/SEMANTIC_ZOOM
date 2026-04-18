from pathlib import Path

import pm4py.objects.log.importer.xes.importer as xes_importer


project_root = Path(__file__).parent.parent.parent

XES_VOLATILE_PATH = project_root / 'data' / 'working_data' / 'volatile_working_xes.xes'

def load_event_log(file_path: str):
    """Loads an event log from a temporary file path."""
    if not file_path.endswith(".xes") and not file_path.endswith(".csv"):
        raise ValueError("Only .xes or .csv files are supported.")
    if file_path.endswith(".xes"):
        log = xes_importer.apply(file_path, parameters={"timestamp_sort": True, "insert_trace_indices": False})
    elif file_path.endswith(".csv"):
        raise NotImplementedError("CSV log loading is not implemented yet.")
    else:
        raise ValueError("Only .xes or .csv files are supported.")
    return log

def trace_to_tuple(trace):
    for event in trace:
        if "case" in event:
            del event["case"]
    return tuple(str(event) for event in trace)


# k-anonymity at trace level -> get all events of the trace in a tuple, hash them and use them as key
def count_unique_traces(log):
    trace_count_map = {}
    for trace in log:
        trace_tuple = hash(trace_to_tuple(trace))
        if trace_tuple in trace_count_map:
            trace_count_map[trace_tuple] += 1
        else:
            trace_count_map[trace_tuple] = 1
    return trace_count_map

# k-anonymity at event level -> check event attributes, hash them and use them as key
def count_unique_events(log):
    event_count_map = {}
    for trace in log:
        for event in trace:
            event_hash = hash(event)
            if event_hash in event_count_map:
                event_count_map[event_hash] += 1
            else:
                event_count_map[event_hash] = 1
    return event_count_map

# k-anonymity at edge level -> check traces and two events that follow each other, hash this edge and use them as key
def count_unique_edges(log):
    edge_count_map = {}
    for trace in log:
        old_event = None
        for event in trace:
            if old_event is None:
                old_event = event
                continue
            edge = (hash(old_event), hash(event))
            if edge in edge_count_map:
                edge_count_map[edge] += 1
            else:
                edge_count_map[edge] = 1
    return edge_count_map

# trace edge and event k-anonymity interleaved to increase performance
def get_k_anonymity(file_path):
    edge_count_map = {}
    event_count_map = {}
    trace_count_map = {}
    log = load_event_log(file_path)
    for trace in log:
        old_event = None
        for event in trace:
            # Event
            event_hash = hash(event)
            if event_hash in event_count_map:
                event_count_map[event_hash] += 1
            else:
                event_count_map[event_hash] = 1
            # Edges
            if old_event is None:
                old_event = event
                continue
            edge = (hash(old_event), event_hash)
            if edge in edge_count_map:
                edge_count_map[edge] += 1
            else:
                edge_count_map[edge] = 1
        # Trace
        trace_tuple = hash(trace_to_tuple(trace))
        if trace_tuple in trace_count_map:
            trace_count_map[trace_tuple] += 1
        else:
            trace_count_map[trace_tuple] = 1
    return trace_count_map, edge_count_map, event_count_map




def main():
    log = load_event_log(str(XES_VOLATILE_PATH))
    trace_count_map = count_unique_traces(log)
    print("Unique traces and their counts:")
    print(trace_count_map)
    log = load_event_log(str(XES_VOLATILE_PATH))
    event_count_map = count_unique_events(log)
    print("Unique events and their counts:")
    print(event_count_map)
    log = load_event_log(str(XES_VOLATILE_PATH))
    print("Unique edges and their counts:")
    edge_count_map = count_unique_edges(log)
    print(edge_count_map)
    trace_count_map, edge_count_map, event_count_map = get_k_anonymity(str(XES_VOLATILE_PATH))
    print(trace_count_map)
    print(edge_count_map)
    print(event_count_map)


if __name__ == '__main__':
    main()