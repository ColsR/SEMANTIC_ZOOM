import json
import sys
from pathlib import Path

from pm4py.objects.log.importer.xes import importer as xes_importer
from enum import Enum


project_root = Path(__file__).resolve().parent.parent.parent
sys.path.append(str(project_root))
FILEPATH = project_root / 'data' / 'working_data'


class ATTRIBUTE_TYPES(Enum):
    TIME = "time"
    ACTIVITY = "activity"
    RESOURCE = "resource"
    STRING = "string"
    NUMERICAL = "numerical"


trace_attributes = set()
event_attributes = set()
event_attribute_type_mapping = dict()


def load_event_log(file_path):
    if not file_path.endswith(".xes"):
        raise ValueError("Only .xes files are supported.")
    log = xes_importer.apply(file_path, parameters={"timestamp_sort": True, "insert_trace_indices": False})
    return log


def extract_attributes(file_path):
    log = load_event_log(file_path)
    for trace in log:
        trace_attributes.update(trace.attributes.keys())
        for event in trace:
            event_attributes.update(event.keys())


def extract_attribute_type_mapping():
    for attr in event_attributes:
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