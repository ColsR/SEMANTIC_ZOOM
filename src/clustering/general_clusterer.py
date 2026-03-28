from pathlib import Path

import pandas as pd
import pm4py

from src.analysis import attribute_extractor
from src.clustering import time_clusterer, activity_clusterer, resource_clusterer, instance_clusterer, \
    numerical_clusterer

ABSTRACTION_FUNCTIONS = None
FLAT_ABSTRACTION_FUNCTIONS = None

def general_abstraction(df, column, abstraction):
    df[column + '_abstracted'] = df[column].apply(lambda x: abstraction(x))
    return df

def rename_abstraction(df, column, abstraction):
    df[column] = df[column].apply(lambda x: abstraction(x))
    return df

def get_abstractions():
    global ABSTRACTION_FUNCTIONS, FLAT_ABSTRACTION_FUNCTIONS

    if FLAT_ABSTRACTION_FUNCTIONS is None:
        ABSTRACTION_FUNCTIONS, FLAT_ABSTRACTION_FUNCTIONS = build_abstractions()
    return ABSTRACTION_FUNCTIONS, FLAT_ABSTRACTION_FUNCTIONS


def reset_abstractions():
    global ABSTRACTION_FUNCTIONS, FLAT_ABSTRACTION_FUNCTIONS
    ABSTRACTION_FUNCTIONS = None
    FLAT_ABSTRACTION_FUNCTIONS = None

def build_abstractions():
    abstraction_functions = {}
    attributes = attribute_extractor.event_attribute_type_mapping
    print(f"attribute_mapping: {attributes}")

    for col_name, attribute_type in attributes.items():
        match attribute_type:
            case attribute_extractor.ATTRIBUTE_TYPES.TIME:
                abstraction_functions[f"time_{col_name}"] = time_clusterer.get_all(col_name)
                print({f"time_{col_name}" : time_clusterer.get_all(col_name)})
            case attribute_extractor.ATTRIBUTE_TYPES.ACTIVITY:
                abstraction_functions[f"activity_{col_name}"] = activity_clusterer.get_all(col_name)
                print({f"activity_{col_name}" : activity_clusterer.get_all(col_name)})
            case attribute_extractor.ATTRIBUTE_TYPES.RESOURCE:
                abstraction_functions[f"resource_{col_name}"] = resource_clusterer.get_all(col_name)
                print({f"resource_{col_name}" : resource_clusterer.get_all(col_name)})
            case attribute_extractor.ATTRIBUTE_TYPES.NUMERICAL:
                abstraction_functions[f"numerical_{col_name}"] = numerical_clusterer.get_all(col_name)
                print({f"numerical_{col_name}": numerical_clusterer.get_all(col_name)})
            case _:
                abstraction_functions[f"misc{col_name}"] = instance_clusterer.get_all(col_name)
                print("Not supported yet")
                print({f"misc{col_name}" : instance_clusterer.get_all(col_name)})

    flat_abstraction_functions = {k: v for group in abstraction_functions.values() for k, v in group.items()}
    print(f"Flat: {flat_abstraction_functions}")
    print("T")
    return abstraction_functions, flat_abstraction_functions

"""
ABSTRACTION_FUNCTIONS = {
    "time":
        {
            "time_month": ('time:timestamp', time_clusterer.abstract_time_to_month),
            "time_week": ('time:timestamp', time_clusterer.abstract_time_to_week),
            "time_day": ('time:timestamp', time_clusterer.abstract_time_to_day),
            "time_hour": ('time:timestamp', time_clusterer.abstract_time_to_hour),
            "time_minute": ('time:timestamp', time_clusterer.abstract_time_to_minute),
            "time_not_abstracted": ('time:timestamp', instance_clusterer.abstract_instance)
        },
    "activity":
        {
            "activity_abstracted2": ('concept:name', activity_clusterer.abstract_activity2),
            "activity_abstracted": ('concept:name', activity_clusterer.abstract_activity),
            "activity_not_abstracted": ('concept:name', instance_clusterer.abstract_instance)
        },
    "resource":
        {
            "resource_abstracted": ('org:resource', ressource_clusterer.abstract_resource_complete),
            "resource_not_abstracted": ('org:resource', instance_clusterer.abstract_instance)
        },
}
"""



#FLAT_ABSTRACTION_FUNCTIONS = {k: v for group in ABSTRACTION_FUNCTIONS.values() for k, v in group.items()}


def abstraction_1(df):
    print(df.columns)
    df = rename_abstraction(df, 'concept:name', activity_clusterer.abstract_activity2)
    print("abstracted activities")
    print(df)
    return rename_abstraction(df, 'time:timestamp', time_clusterer.abstract_time_to_week)

if __name__ == '__main__':
    project_root = Path(__file__).resolve().parent.parent.parent
    FILEPATH = project_root / 'data'
    df = pm4py.read_xes(str(FILEPATH / 'evaluation_data' / 'runningexample.xes'))
    df_abstracted = general_abstraction(df, 'time:timestamp', time_clusterer.abstract_time_to_day)
    df_abstracted = general_abstraction(df_abstracted, 'org:resource', resource_clusterer.abstract_resource_complete)
    df_abstracted = general_abstraction(df_abstracted, 'concept:name', activity_clusterer.abstract_activity)
    df.to_csv(FILEPATH / 'abstracted_df.csv')
