


"""
checks the XES File at the xes_path (in general the Volatile-Working-XES) if the expected privacy requirements are matched
if a trace violates one of the privacy requirements it is removed from the XES
then the process is started again, because the deletion of the trace can cause other traces to violate the privacy requirements, which can lead to a cascade effect of trace deletions
"""
import logging
from pathlib import Path

import pm4py
from pm4py.objects.log.obj import EventLog

from src.analysis.privacy.k_anonymity import get_k_anonymity, load_event_log, trace_to_tuple, count_unique_traces, \
    count_unique_events, count_unique_edges
from src.analysis.privacy.l_diversity import get_l_diversity, calc_l_div, get_l_diversity_single_event

logger = logging.getLogger(__name__)

def check_metrics(xes_path, k_trace=-1, k_event=-1, k_edge=-1, l_div=-1, single_event_l_div=False, follow_event_l_div=False) -> bool:
    log = load_event_log(xes_path)

    print("Checking privacy metrics for the log...")
    if k_trace > 0 and k_event > 0 and k_edge > 0:
        trace_count_map, edge_count_map, event_count_map = get_k_anonymity(xes_path, log)
        for k_trace_value in trace_count_map.values():
            if k_trace_value < k_trace:
                return False
        for k_event_value in edge_count_map.values():
            if k_event_value < k_event:
                return False
        for k_edge_value in event_count_map.values():
            if k_edge_value < k_edge:
                return False
    else:
        if k_trace > 0:
            trace_count_map = count_unique_traces(xes_path, log)
            for k_trace_value in trace_count_map.values():
                if k_trace_value < k_trace:
                    return False
        if k_event > 0:
            event_count_map = count_unique_events(xes_path, log)
            for k_event_value in event_count_map.values():
                if k_event_value < k_event:
                    return False
        if k_edge > 0:
            edge_count_map = count_unique_edges(xes_path, log)
            for k_edge_value in edge_count_map.values():
                if k_edge_value < k_edge:
                    return False


    if l_div > 0:
        if single_event_l_div:
            if not get_l_diversity_single_event(xes_path, l_div, log):
                return False
        if follow_event_l_div:
            div_map = get_l_diversity(xes_path, log)
            l_div_counts = calc_l_div(div_map)
            for event_hash, l_div_values in l_div_counts.items():
                for _, l_div_val in l_div_values.items():
                    if l_div_val < l_div:
                        return False

    return True







def delete_trace(xes_path, min_k_trace=-1, min_k_event=-1, min_k_edge=-1, min_l_event=-1):
    log = load_event_log(xes_path)
    privacy_reached = False
    while not privacy_reached:
        if check_empty_log(xes_path):
            logger.warning("Log is empty after deletions, stopping process.")
            break
        trace_k_map, edge_k_map, event_k_map = get_k_anonymity(xes_path, log)
        logger.debug(f"trace_k_map: {trace_k_map}")
        logger.debug(f"edge_k_map: {edge_k_map}")
        logger.debug(f"event_k_map: {event_k_map}")

        if min_k_event > 0:
            event_privacy_reached = True
            event_hashes= []
            for event_hash, k_val in event_k_map.items():
                if k_val < min_k_event:
                    event_hashes.append(event_hash)
            event_privacy_reached = delete_event_by_hash(xes_path, event_hashes, log) and event_privacy_reached
            if not event_privacy_reached:
                # a trace is deleted from the log -> load log again and start analysis again
                continue
            print("Check Event K-anonymity completed")


        if min_k_edge > 0:
            edge_privacy_reached = True
            edges_hashes = []
            for trace_hash_tuple, k_val in edge_k_map.items():
                if k_val < min_k_edge:
                    edges_hashes.append(trace_hash_tuple)
            edge_privacy_reached = delete_edge_by_hash(xes_path, edges_hashes, log) and edge_privacy_reached
            if not edge_privacy_reached:
                # a trace is deleted from the log -> load log again and start analysis again
                continue
            print("Check Edge K-anonymity completed")

        if min_k_trace > 0:
            trace_privacy_reached = True
            trace_hashes = []
            for trace_hash, k_val in trace_k_map.items():
                if k_val < min_k_trace:
                    trace_hashes.append(trace_hash)
            trace_privacy_reached = delete_trace_by_hash(xes_path, trace_hashes, log) and trace_privacy_reached
            if not trace_privacy_reached:
                # a trace is deleted from the log -> load log again and start analysis again
                continue
            print("Check Trace K-anonymity completed")


        if min_l_event > 0:
            event_l_div_reached = True
            l_div_event_hashes = []
            l_div_counts = calc_l_div(get_l_diversity(load_event_log(xes_path)))
            print(l_div_counts)
            for event_hash, l_div_values in l_div_counts.items():
                for _, l_div_val in l_div_values.items():
                    if l_div_val < min_l_event:
                        l_div_event_hashes.append(event_hash)
            event_l_div_reached = delete_event_by_hash(xes_path, l_div_event_hashes) and event_l_div_reached
            if not event_l_div_reached:
                # a trace is deleted from the log -> load log again and start analysis again
                continue
            print("Check Event L-diversity completed")

        privacy_reached = True

# returns true if event was deleted, false if not
def delete_event_by_hash(file_path:str, event_hashes_to_delete, log=None) -> bool:
    if log is None:
        log = load_event_log(str(file_path))
    logger.debug(f"deleting event: {event_hashes_to_delete}")
    filtered_case_ids =[]
    for trace in log:
        for event in trace:
            event_hash = hash(event)
            if event_hash in event_hashes_to_delete:
                filtered_case_ids.append(trace.attributes["concept:name"])

    filtered_log = filter_eventlog_by_cases(log, filtered_case_ids)
    pm4py.write_xes(filtered_log, file_path)
    return filtered_case_ids == []

def delete_edge_by_hash(file_path:str, edge_hashes_to_delete, log=None) -> bool:
    if log is None:
        log = load_event_log(str(file_path))
    logger.debug(f"deleting edge: {edge_hashes_to_delete}")
    filtered_case_ids = []
    for trace in log:
        old_event = None
        for event in trace:
            if old_event is None:
                old_event = event
                continue
            edge_hash = (hash(old_event), hash(event))
            if edge_hash in edge_hashes_to_delete:
                filtered_case_ids.append(trace.attributes["concept:name"])

    filtered_log = filter_eventlog_by_cases(log, filtered_case_ids)
    pm4py.write_xes(filtered_log, file_path)
    return filtered_case_ids == []

def delete_trace_by_hash(file_path:str, trace_hashes, log=None) -> bool:
    if log is None:
        log = load_event_log(str(file_path))
    logger.debug(f"deleting trace: {trace_hashes}")
    filtered_case_ids =[]
    for trace in log:
        trace_tuple = hash(trace_to_tuple(trace))
        if trace_tuple in trace_hashes:
            case_id = trace.attributes["concept:name"]
            filtered_case_ids.append(case_id)

    filtered_log = filter_eventlog_by_cases(log, filtered_case_ids)
    pm4py.write_xes(filtered_log, file_path)
    return filtered_case_ids == []

def filter_eventlog_by_cases(log, cases_to_remove):
    filtered_traces = [
        trace for trace in log
        if trace.attributes["concept:name"] not in cases_to_remove
    ]
    return EventLog(filtered_traces)




def check_empty_log(file_path:str, log=None):
    if log is None:
        log = load_event_log(str(file_path))
    return len(log) == 0

def main():
    if __debug__:
        logging.basicConfig(level=logging.DEBUG)
    project_root = Path(__file__).parent.parent.parent.parent

    XES_VOLATILE_PATH = project_root / 'data' / 'working_data' / 'volatile_working_xes.xes'
    delete_trace(str(XES_VOLATILE_PATH), min_k_event=3, min_k_edge=3, min_l_event=2)


if __name__ == '__main__':
    main()