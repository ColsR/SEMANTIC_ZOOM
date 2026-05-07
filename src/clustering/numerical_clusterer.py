import copy
import logging
import math
from contextlib import nullcontext
from math import sqrt

import pandas as pd

from src.analysis import attribute_extractor
from src.clustering import instance_clusterer
from src.clustering.abstract_abstraction import AbstractAbstraction
from src.clustering.abstract_clusterer import AbstractClusterer
from src.clustering.instance_clusterer import InstanceAbstraction

logger = logging.getLogger(__name__)

splits = {}

class NumericalClusterer(AbstractClusterer):
    # müsste in sich die Splits für die Spalte speichern. Dafür muss bei Instanziierung aber eben auch das df vorliegen
    def __init__(self, col_name):
        global splits
        self.col_splits = splits.get(col_name, {})
        super().__init__(col_name)
        self.set_abstraction(None)

    def build_abstractions(self, col_name):
        return {
            f"{col_name}_abstracted": InstanceAbstraction(col_name, col_name, instance_clusterer.abstract_instance_complete, 0),
            f"{col_name}_2_classes": NumericalAbstraction(col_name, col_name, self.col_splits.get(2, []), 1),
            f"{col_name}_4_classes": NumericalAbstraction(col_name, col_name, self.col_splits.get(4, []), 2),
            f"{col_name}_8_classes": NumericalAbstraction(col_name, col_name, self.col_splits.get(8, []), 3),
            f"{col_name}_not_abstracted": InstanceAbstraction(col_name, col_name, instance_clusterer.abstract_instance, 100),
        }


class NumericalAbstraction(AbstractAbstraction):
    def __init__(self, source_col, target_col, bounds, ranking=1):
        super().__init__(source_col, target_col, None, ranking)
        self.bounds = bounds

    def apply_abstraction(self, number):
        try:
            number = float(number)
        except ValueError:
            logger.debug("number not to float castable")
        for split in self.bounds:  # TODO change to List?
            if split >= number:
                self.l_div_map[split].add(number)
                return split
        return None


def build_abstractions(df):
    for col_name in [key for key,value in attribute_extractor.event_attribute_type_mapping.items() if value == attribute_extractor.ATTRIBUTE_TYPES.NUMERICAL and key in df.columns.values.tolist()]:
        get_splitting(df, col_name, 16)

def get_splitting(df, col_name, num_classes):
    global splits
    
    # num_classes is power of 2
    if not (num_classes > 0 and (num_classes & (num_classes - 1)) == 0):
        raise ValueError(f"num_classes has to be a power of 2, num_classes: {num_classes}")
    
    series = df[col_name].dropna()
    if series.empty:
        raise ValueError(f"Column '{col_name}' contains no non-null values")

    if not pd.api.types.is_numeric_dtype(series):
        try:
            series = series.astype(float)
        except ValueError:
            raise TypeError(f"Column '{col_name}' must be numeric (int/float)")

    current_splits = splits.get(col_name, {})
    
    # recursive
    if num_classes == 2:
        # base
        bounds = _split_range(series, 2)
        current_splits[num_classes] = bounds
    else:
        # recursive call
        prev_num_classes = num_classes // 2
        if prev_num_classes not in current_splits:
            # if previous split not already computed, compute it recursively
            prev_bounds = get_splitting(df, col_name, prev_num_classes)
            current_splits[prev_num_classes] = prev_bounds
        else:
            # use previous split
            prev_bounds = current_splits[prev_num_classes]

        bounds = _split_hierarchical(series, prev_bounds)

    # update global splits
    current_splits[num_classes] = bounds
    if col_name not in splits.keys():
        splits[col_name] = current_splits
    splits[col_name].update(current_splits)
    logger.debug(f"splits {splits}")
    return bounds


def _split_range(series, num_classes):
    counts = series.value_counts().sort_index()
    cumulative = counts.cumsum()
    total = int(cumulative.iloc[-1])
    
    bounds = []
    for k in range(1, num_classes + 1):
        target_rank = math.ceil(k * total / num_classes)
        # Pick the first value whose cumulative count reaches target_rank.
        boundary_value = cumulative[cumulative >= target_rank].index[0]
        # if the split is the highest value of the series, try to use the second highest value as splitter
        if boundary_value == max(counts.index) and not bounds and len(counts.index) > 1:
            new_bound = counts.index[-2]
            #if new_bound != min(counts.index):
                # if the second highest value is not the lower bound use it as splitter
            boundary_value = new_bound

        if not bounds or boundary_value != bounds[-1]:
            bounds.append(boundary_value)
    
    return bounds


def _split_hierarchical(series, prev_bounds):
    new_bounds = []

    prev_bounds_sorted = sorted(prev_bounds)
    ranges = []
    prev_upper = float('-inf')
    
    for bound in prev_bounds_sorted:
        ranges.append((prev_upper, bound))
        prev_upper = bound
    
    # split every range in two sub-ranges
    # get sub-series fpr the given bounds
    for lower, upper in ranges:
        if lower == float('-inf'):
            range_series = series[series <= upper]
        else:
            range_series = series[(series > lower) & (series <= upper)]
        
        if not range_series.empty:
            # split the sub-series into two classes and add the new bounds to the list
            sub_bounds = _split_range(range_series, 2)
            new_bounds.extend(sub_bounds)

    new_bounds = sorted(list(set(new_bounds)))
    
    return new_bounds


