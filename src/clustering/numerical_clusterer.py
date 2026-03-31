import logging
import math

import pandas as pd

from src.analysis import attribute_extractor
from src.clustering import instance_clusterer
from src.clustering.abstract_clusterer import AbstractClusterer
from src.clustering.instance_clusterer import InstanceClusterer

logger = logging.getLogger(__name__)

splits = {}


class NumericalClusterer(AbstractClusterer):

    def __init__(self, col_name, num_classes):
        super().__init__(col_name)
        global splits
        col_splits = splits.get(col_name, {})
        bounds = col_splits.get(num_classes, [])
        self.bounds = bounds

    def apply_abstraction(self, number):
        try:
            number = float(number)
        except ValueError:
            logger.debug("number not to float castable")
        for split in self.bounds: # TODO change to List?
            if split >= number:
                return split

        return None
        #print(f"Number {number} is greater than all splits {self.bounds}")


def build_abstractions(df):
    for col_name in [key for key,value in attribute_extractor.event_attribute_type_mapping.items() if value == attribute_extractor.ATTRIBUTE_TYPES.NUMERICAL and key in df.columns.values.tolist()]:
        get_splitting(df, col_name, 2)
        get_splitting(df, col_name, 4)
        get_splitting(df, col_name, 8)
        get_splitting(df, col_name, 16)

def get_splitting(df, col_name, num_classes):
    global splits
    series = df[col_name].dropna()
    if series.empty:
        raise ValueError(f"Column '{col_name}' contains no non-null values")

    if not pd.api.types.is_numeric_dtype(series):
        try:
            series = series.astype(float)
        except ValueError:
            raise TypeError(f"Column '{col_name}' must be numeric (int/float)")

    counts = series.value_counts().sort_index()
    cumulative = counts.cumsum()
    total = int(cumulative.iloc[-1])

    bounds = []
    for k in range(1, num_classes + 1):
        target_rank = math.ceil(k * total / num_classes)
        # Pick the first value whose cumulative count reaches target_rank.
        boundary_value = cumulative[cumulative >= target_rank].index[0]
        bounds.append(boundary_value)
    current_splits = splits.get(col_name, {})
    current_splits[num_classes] = bounds
    splits[col_name] = current_splits
    logger.debug(f"splits {splits}")
    return bounds

def get_all(col_name):
    return {
        f"numerical{col_name}_abstracted": (col_name, InstanceClusterer(col_name,instance_clusterer.abstract_instance_complete)),
        f"numerical{col_name}_2_classes": (col_name, NumericalClusterer(col_name, 2)),
        f"numerical{col_name}_4_classes": (col_name, NumericalClusterer(col_name, 4)),
        f"numerical{col_name}_8_classes": (col_name, NumericalClusterer(col_name, 8)),
        f"numerical{col_name}_not_abstracted": (col_name, InstanceClusterer(col_name, instance_clusterer.abstract_instance)),
    }


