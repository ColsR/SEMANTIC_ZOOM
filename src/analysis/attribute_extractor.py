import json
import logging
import sys
from collections import defaultdict
from datetime import datetime
from pathlib import Path

from pm4py.objects.log.importer.xes import importer as xes_importer
from enum import Enum

logger = logging.getLogger(__name__)

project_root = Path(__file__).resolve().parent.parent.parent
sys.path.append(str(project_root))
FILEPATH = project_root / 'data' / 'working_data'


class ATTRIBUTE_TYPES(str, Enum):
    TIME = "time"
    ACTIVITY = "activity"
    RESOURCE = "resource"
    STRING = "string"
    NUMERICAL = "numerical"


trace_attributes = set()
event_attributes = set()
event_attribute_type_mapping = dict()
trace_attributes_types = defaultdict(set)
event_attributes_types = defaultdict(set)



def load_event_log(file_path):
    if not file_path.endswith(".xes"):
        raise ValueError("Only .xes files are supported.")
    log = xes_importer.apply(file_path, parameters={"timestamp_sort": True, "insert_trace_indices": False})
    return log


def extract_attributes(file_path):
    log = load_event_log(file_path)
    for trace in log:
        trace_attributes.update(trace.attributes.keys())
        for trace_key, trace_value in trace.attributes.items():
            trace_attributes_types[trace_key].add(type(trace_value).__name__)
        for event in trace:
            event_attributes.update(event.keys())
            for key, value in event.items():
                event_attributes_types[key].add(type(value).__name__)

    logger.info(f"event_attributes_types: {event_attributes_types}")
    logger.info(f"trace_attributes_types: {trace_attributes_types}")


def extract_attribute_type_mapping():
    # Match based on attribute name
    for attr in event_attributes_types.keys():
        match attr:
            case "time:timestamp":
                event_attribute_type_mapping.update({attr: ATTRIBUTE_TYPES.TIME})
            case "org:resource":
                event_attribute_type_mapping.update({attr: ATTRIBUTE_TYPES.RESOURCE})
            case "concept:name":
                event_attribute_type_mapping.update({attr: ATTRIBUTE_TYPES.ACTIVITY})
            case "Costs":
                event_attribute_type_mapping.update({attr: ATTRIBUTE_TYPES.NUMERICAL})
            case _:
                pass

    # Match based on attribute type
    for attr, attr_type_set in event_attributes_types.items():
        if attr not in event_attribute_type_mapping.keys():
            logger.debug(f"Matching attribute {attr} based on type. Types: {attr_type_set}")
            selected_attr_type = next(iter(attr_type_set))
            if len(attr_type_set) > 1:
                logger.warning(f"{attr} has more than one type. Types: {attr_type_set}. SETTING to {selected_attr_type}.")
            match selected_attr_type:
                case datetime.__name__:
                    event_attribute_type_mapping.update({attr: ATTRIBUTE_TYPES.TIME})
                case float.__name__:
                    event_attribute_type_mapping.update({attr: ATTRIBUTE_TYPES.NUMERICAL})
                case int.__name__:
                    event_attribute_type_mapping.update({attr: ATTRIBUTE_TYPES.NUMERICAL})
                case str.__name__:
                    event_attribute_type_mapping.update({attr: ATTRIBUTE_TYPES.STRING})
                case _:
                    event_attribute_type_mapping.update({attr: ATTRIBUTE_TYPES.STRING})


def write_to_file():
    with open(f'{FILEPATH}/attributes.json', 'w') as outfile:
        json.dump({
            'eventAttributes':
                {k: v.value for k, v in event_attribute_type_mapping.items()}
        },
            outfile,
            indent=2
        )


def update_attribute(attribute, attribute_type):
    event_attribute_type_mapping.update({attribute: ATTRIBUTE_TYPES(attribute_type)})
    write_to_file()


"""
class AttributeExtractor:
    def __init__(self, file_path):
        self.file_path = file_path
        self.log = self.load_event_log()
        self.trace_attributes = set()
        self.event_attributes = set()
        self.event_attribute_type_mapping = dict()

    def load_event_log(self):
        if not self.file_path.endswith(".xes"):
            raise ValueError("Only .xes files are supported.")
        log = xes_importer.apply(self.file_path, parameters={"timestamp_sort": True, "insert_trace_indices": False})
        return log

    def extract_attributes(self):
        for trace in self.log:
            self.trace_attributes.update(trace.attributes.keys())
            for event in trace:
                self.event_attributes.update(event.keys())

    def extract_attribute_type_mapping(self):
        for attr in self.event_attributes:
            match attr:
                case "time:timestamp":
                    self.event_attribute_type_mapping.update({attr : ATTRIBUTE_TYPES.TIME})
                case "org:resource":
                    self.event_attribute_type_mapping.update({attr : ATTRIBUTE_TYPES.RESOURCE})
                case "concept:name":
                    self.event_attribute_type_mapping.update({attr : ATTRIBUTE_TYPES.ACTIVITY})
                case _ :
                    self.event_attribute_type_mapping.update({attr : ATTRIBUTE_TYPES.STRING})

    def write_to_file(self):
        with open(f'{FILEPATH}/attributes.json', 'w') as outfile:
            json.dump({
                'eventAttributes':
                {k: v.value for k, v in self.event_attribute_type_mapping.items()}
                },
                outfile,
                indent=2
            )
"""