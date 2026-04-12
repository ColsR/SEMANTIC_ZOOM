"""
ALGO:
Für jeden Trace
    Skip Start-Event
    Für jedes Event:
        nimm Event (cur_event) und Event davor (prev_event):
        hashe prev_event
            für jedes Attribut in cur_event:
                lies aus welche Möglichkeiten es für dieses Attribut gibt
                füge diese Möglichkeiten in die l-diversity Map für den hash(prev_event) key ein

Resultat ist eine Map mit allen Events als Keys und für jedes Attribut die Möglichkeiten, die das Attribut im folgenden Event annehmen kann
"""

import json
import logging
from collections import defaultdict
from datetime import datetime
from pathlib import Path

from src.analysis.k_anonymity import load_event_log

project_root = Path(__file__).parent.parent.parent

XES_VOLATILE_PATH = project_root / 'data' / 'working_data' / 'volatile_working_xes.xes'
L_DIVERSITY_PATH = project_root / 'data' / 'working_data' / 'l_diversity.json'

logger = logging.getLogger(__name__)

def load_l_diversity_map(file_path):
    with open(file_path, 'r') as f:
        return json.load(open(str(L_DIVERSITY_PATH), 'r'))


def get_l_diversity(log):
    event_attribute_l_div_map = defaultdict(dict)
    l_diversity_map = load_l_diversity_map(str(L_DIVERSITY_PATH))
    for trace in log:
        prev_event = None
        for event in trace:
            if prev_event is None:
                prev_event = event
                continue
            prev_event_hash = hash(prev_event)
            for column, abstracted_value in event.items():
                if isinstance(abstracted_value, datetime):
                    abstracted_value = str(abstracted_value)
                possible_follower = l_diversity_map[column][abstracted_value]
                if column not in event_attribute_l_div_map[prev_event_hash].keys():
                    event_attribute_l_div_map[prev_event_hash][column] = set()
                if event_attribute_l_div_map[prev_event_hash][column]:
                    logger.debug(f"Already existing possible followers for {prev_event} and column {column}: {event_attribute_l_div_map[prev_event_hash][column]}")
                event_attribute_l_div_map[prev_event_hash][column] = event_attribute_l_div_map[prev_event_hash][column].union(possible_follower)
            prev_event = event
    return event_attribute_l_div_map

def calc_l_div(event_attribute_l_div_map):
    for event_hash, column_follower_map in event_attribute_l_div_map.items():
        for column, possible_follower in column_follower_map.items():
            column_follower_map[column] = len(column_follower_map[column])
    return event_attribute_l_div_map
def main():
    log = load_event_log(str(XES_VOLATILE_PATH))
    trace_count_map = get_l_diversity(log)
    print("Unique traces and their counts:")
    print(trace_count_map)
    l_div_counts = calc_l_div(trace_count_map)
    print(l_div_counts)

if __name__ == "__main__":
    main()