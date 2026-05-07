from enum import Enum

import pandas as pd

from src.clustering import instance_clusterer
from src.clustering.abstract_abstraction import AbstractAbstraction
from src.clustering.abstract_clusterer import AbstractClusterer


class TimeClusterer(AbstractClusterer):

    class TIME_ABSTRACTIONS(Enum):
        MONTH = "MONTH"
        DAY = "DAY"
        HOUR = "HOUR"
        MINUTE = "MINUTE"
        SECOND = "SECOND"

    def __init__(self, col_name):
        super().__init__(col_name)
        self.set_abstraction(None)

    def build_abstractions(self, col_name):
        return {
            f"time{col_name}_abstracted": TimeAbstraction(col_name, col_name, abstract_time_complete, 0),
            f"time{col_name}_year": TimeAbstraction(col_name, col_name,  abstract_time_to_year, 1),
            f"time{col_name}_month": TimeAbstraction(col_name, col_name, abstract_time_to_month, 2),
            f"time{col_name}_day": TimeAbstraction(col_name, col_name, abstract_time_to_day, 4),
            f"time{col_name}_hour": TimeAbstraction(col_name, col_name, abstract_time_to_hour, 5),
            f"time{col_name}_minute": TimeAbstraction(col_name, col_name, abstract_time_to_minute, 6),
            f"time{col_name}_not_abstracted": TimeAbstraction(col_name, col_name, instance_clusterer.abstract_instance, 100),
        }


class TimeAbstraction(AbstractAbstraction):
    def __init__(self, source_col, target_col, abstraction_function, ranking=1):
        super().__init__(source_col, target_col, abstraction_function, ranking)

    def apply_abstraction(self, value):
        # timestamps raise problems with json
        abstracted_value = self.abstraction_function(value)
        self.l_div_map[str(abstracted_value)].add(str(value))
        return abstracted_value


def abstract_time_complete(timestamp):
    return pd.Timestamp(0, tz="UTC")

def abstract_time_to_year(timestamp):
    return timestamp.replace(month=1, day=1, hour=0, minute=0, second=0, microsecond=0)

def abstract_time_to_month(timestamp):
    return timestamp.replace(day=1, hour=0, minute=0, second=0, microsecond=0)

def abstract_time_to_day(timestamp):
    return timestamp.normalize()

def abstract_time_to_hour(timestamp):
    return timestamp.replace(minute=0, second=0, microsecond=0)

def abstract_time_to_minute(timestamp):
    return timestamp.replace(second=0, microsecond=0)

def abstract_time_to_second(timestamp):
    return timestamp.replace(microsecond=0)
