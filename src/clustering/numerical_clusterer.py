import logging
import math

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
            f"numerical{col_name}_abstracted": InstanceAbstraction(col_name, col_name, instance_clusterer.abstract_instance_complete, 0),
            f"numerical{col_name}_2_classes": NumericalAbstraction(col_name, col_name, self.col_splits.get(2, []), 1),
            f"numerical{col_name}_4_classes": NumericalAbstraction(col_name, col_name, self.col_splits.get(4, []), 2),
            f"numerical{col_name}_8_classes": NumericalAbstraction(col_name, col_name, self.col_splits.get(8, []), 3),
            f"numerical{col_name}_not_abstracted": InstanceAbstraction(col_name, col_name, instance_clusterer.abstract_instance, 100),
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
