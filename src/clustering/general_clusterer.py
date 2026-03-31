import configparser
import json
import logging
from pathlib import Path

import pandas as pd
import pm4py

from src.analysis import attribute_extractor
from src.clustering import time_clusterer, activity_clusterer, resource_clusterer, instance_clusterer, \
    numerical_clusterer, custom_clusterer

logger = logging.getLogger(__name__)

ABSTRACTION_FUNCTIONS = None
FLAT_ABSTRACTION_FUNCTIONS = None

def general_abstraction(df, column, abstraction):
    df[column + '_abstracted'] = df[column].apply(lambda x: abstraction(x))
    return df

def rename_abstraction(df, target_column, source_column, abstraction):
    if source_column not in df.columns or target_column not in df.columns:
        logger.warning("Cannot Apply abstraction because source or target column is not in dataframe")
        return df
    df[target_column] = df[source_column].apply(lambda x: abstraction(x))
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
    logger.info(f"attribute_mapping: {attributes}")
    custom_columns = set()

    # load custom abstractions
    custom_cluster = custom_clusterer.get_all(None)
    for col_name, clusterer in custom_cluster.items():
        custom_columns.add(col_name)
        abstraction_functions[f"custom{col_name}"] = clusterer
        logger.debug({f"custom{col_name}": time_clusterer.get_all(col_name)})


    for col_name, attribute_type in attributes.items():
        if col_name not in custom_columns:
            match attribute_type:
                case attribute_extractor.ATTRIBUTE_TYPES.TIME:
                    abstraction_functions[f"time_{col_name}"] = time_clusterer.get_all(col_name)
                    logger.debug({f"time{col_name}" : time_clusterer.get_all(col_name)})
                case attribute_extractor.ATTRIBUTE_TYPES.ACTIVITY:
                    abstraction_functions[f"activity_{col_name}"] = activity_clusterer.get_all(col_name)
                    logger.debug({f"activity{col_name}" : activity_clusterer.get_all(col_name)})
                case attribute_extractor.ATTRIBUTE_TYPES.RESOURCE:
                    abstraction_functions[f"resource{col_name}"] = resource_clusterer.get_all(col_name)
                    logger.debug({f"resource{col_name}" : resource_clusterer.get_all(col_name)})
                case attribute_extractor.ATTRIBUTE_TYPES.NUMERICAL:
                    abstraction_functions[f"numerical{col_name}"] = numerical_clusterer.get_all(col_name)
                    logger.debug({f"numerical_{col_name}": numerical_clusterer.get_all(col_name)})
                case _:
                    abstraction_functions[f"misc{col_name}"] = instance_clusterer.get_all(col_name)
                    logger.debug("Not supported yet")
                    logger.debug({f"misc{col_name}" : instance_clusterer.get_all(col_name)})

    flat_abstraction_functions = {k: v for group in abstraction_functions.values() for k, v in group.items()}
    logger.debug(f"Flat: {flat_abstraction_functions}")
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
    df = rename_abstraction(df, 'concept:name','concept:name', activity_clusterer.abstract_activity2)
    print("abstracted activities")
    print(df)
    return rename_abstraction(df, 'time:timestamp','time:timestamp', time_clusterer.abstract_time_to_week)


