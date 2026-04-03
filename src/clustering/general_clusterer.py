import configparser
import json
import logging
from pathlib import Path

import pandas as pd
import pm4py

from src.analysis import attribute_extractor
from src.clustering import time_clusterer, activity_clusterer, resource_clusterer, instance_clusterer, \
    numerical_clusterer, custom_clusterer
from src.clustering.activity_clusterer import ActivityClusterer
from src.clustering.instance_clusterer import InstanceClusterer
from src.clustering.resource_clusterer import ResourceClusterer
from src.clustering.time_clusterer import TimeClusterer

logger = logging.getLogger(__name__)

ABSTRACTION_FUNCTIONS = None
FLAT_ABSTRACTION_FUNCTIONS = None
ABSTRACTION_OBJECTS = None # hält für jede Spalte ein Abstraktionsobjekt, das alle Informationen für die Abstrkationen der Saplte hält
COLUMN_ABSTRACTION_MAPPING = None # mapping Abstraktion auf Spalte

def general_abstraction(df, column, abstraction):
    df[column + '_abstracted'] = df[column].apply(lambda x: abstraction(x))
    return df

def rename_abstraction(df, target_column, source_column, abstraction, mask):
    if source_column not in df.columns or target_column not in df.columns:
        logger.warning("Cannot Apply abstraction because source or target column is not in dataframe")
        return df
    df.loc[mask, target_column] = df.loc[mask, source_column].apply(lambda x : abstraction(x))
    return df

def object_abstraction(df, target_column, source_column, abstraction_obj, mask):
    if not abstraction_obj.check_columns(df.columns):
        logger.error("Cannot Apply abstraction because source or target column is not in dataframe. Should be handled before")
        return df
    df.loc[mask, target_column] = df.loc[mask, source_column].apply(lambda x: abstraction_obj.apply_abstraction(x))
    return df


def get_abstractions():
    global ABSTRACTION_FUNCTIONS, FLAT_ABSTRACTION_FUNCTIONS, ABSTRACTION_OBJECTS, COLUMN_ABSTRACTION_MAPPING

    if FLAT_ABSTRACTION_FUNCTIONS is None:
        ABSTRACTION_FUNCTIONS, FLAT_ABSTRACTION_FUNCTIONS, ABSTRACTION_OBJECTS, COLUMN_ABSTRACTION_MAPPING = build_abstractions()
    return ABSTRACTION_FUNCTIONS, FLAT_ABSTRACTION_FUNCTIONS, ABSTRACTION_OBJECTS, COLUMN_ABSTRACTION_MAPPING


def reset_abstractions():
    global ABSTRACTION_FUNCTIONS, FLAT_ABSTRACTION_FUNCTIONS, ABSTRACTION_OBJECTS, COLUMN_ABSTRACTION_MAPPING
    ABSTRACTION_FUNCTIONS = None
    FLAT_ABSTRACTION_FUNCTIONS = None
    ABSTRACTION_OBJECTS = None
    COLUMN_ABSTRACTION_MAPPING = None

def build_abstractions():
    abstraction_functions = {}
    abstraction_objects = {}
    attributes = attribute_extractor.event_attribute_type_mapping
    logger.info(f"attribute_mapping: {attributes}")
    custom_columns = set()

    """
    # load custom abstractions
    custom_cluster = custom_clusterer.get_all(None)
    for col_name, clusterer in custom_cluster.items():
        custom_columns.add(col_name)
        abstraction_functions[f"custom{col_name}"] = clusterer
        logger.debug({f"custom{col_name}": time_clusterer.get_all(col_name)})
    """

    for col_name, attribute_type in attributes.items():
        if col_name not in custom_columns:
            match attribute_type:

                case attribute_extractor.ATTRIBUTE_TYPES.TIME:
                    # abstraction_functions[f"time_{col_name}"] = time_clusterer.get_all(col_name)
                    # Hier muss das Time_Cluster_Objekt erstellt werden
                    time_cluster = TimeClusterer(col_name, None)
                    abstraction_functions[f"time_{col_name}"] = time_cluster.get_all()
                    logger.debug({f"time_{col_name}" : time_cluster.get_all()})
                    abstraction_objects[col_name] = time_cluster

                case attribute_extractor.ATTRIBUTE_TYPES.ACTIVITY:
                    activity_cluster = ActivityClusterer(col_name, None)
                    abstraction_functions[f"activity_{col_name}"] = activity_cluster.get_all()
                    logger.debug({f"activity{col_name}" : activity_cluster.get_all()})
                    abstraction_objects[col_name] = activity_cluster

                case attribute_extractor.ATTRIBUTE_TYPES.RESOURCE:
                    resource_cluster = ResourceClusterer(col_name, None)
                    abstraction_functions[f"resource{col_name}"] = resource_cluster.get_all()
                    logger.debug({f"resource{col_name}" : resource_cluster.get_all()})
                    abstraction_objects[col_name] = resource_cluster

                case attribute_extractor.ATTRIBUTE_TYPES.NUMERICAL:
                    continue
                    abstraction_functions[f"numerical{col_name}"] = numerical_clusterer.get_all(col_name)
                    logger.debug({f"numerical_{col_name}": numerical_clusterer.get_all(col_name)})

                case _:
                    instance_cluster = InstanceClusterer(col_name, None)
                    abstraction_functions[f"misc{col_name}"] = instance_cluster.get_all()
                    logger.debug("Not supported yet")
                    logger.debug({f"misc{col_name}" : instance_cluster.get_all()})
                    abstraction_objects[col_name] = instance_cluster

    # flat_abstractions als mapping key: (col, obj?)
    flat_abstraction_functions = {k: v for group in abstraction_functions.values() for k, v in group.items()}
    column_abstraction_mapping = {k: v[1].target_col for group in abstraction_functions.values() for k, v in group.items()}
    logger.debug(f"Flat: {flat_abstraction_functions}")
    return abstraction_functions, flat_abstraction_functions, abstraction_objects, column_abstraction_mapping




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


