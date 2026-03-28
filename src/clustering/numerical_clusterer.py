import math

import pandas as pd

from src.analysis import attribute_extractor
from src.clustering import instance_clusterer

splits = {}


def build_abstractions(df):
    for col_name in [key for key,value in attribute_extractor.event_attribute_type_mapping.items() if value == attribute_extractor.ATTRIBUTE_TYPES.NUMERICAL]:
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
    print(f"splits {splits}")
    return bounds


def build_splitting_function(col_name, num_classes):
    global splits
    col_splits = splits.get(col_name, {})
    bounds = col_splits.get(num_classes, [])

    return lambda x: apply_splitting(x, bounds)


def apply_splitting(number, splitting):
    for split in splitting:
        try:
            number = float(number)
            if split >= number:
                return split
        except ValueError:
            print("number not to float castable")
    raise ValueError(f"Number {number} is greater than all splits {splitting}")


def numerical_abstracted(number):
    return "*"

def get_all(col_name):
    return {
        "numerical_abstracted": (col_name, numerical_abstracted),
        f"numerical_2_classes{col_name}": (col_name, build_splitting_function(col_name, 2)),
        f"numerical_4_classes{col_name}": (col_name, build_splitting_function(col_name, 4)),
        f"numerical_4_classes{col_name}": (col_name, build_splitting_function(col_name, 8)),
        "numerical_not_abstracted": (col_name, instance_clusterer.abstract_instance),
    }


