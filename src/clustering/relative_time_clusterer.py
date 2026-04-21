import datetime
from enum import Enum

import pandas as pd

from src.clustering import instance_clusterer
from src.clustering.abstract_abstraction import AbstractAbstraction
from src.clustering.abstract_clusterer import AbstractClusterer


class RelativeTimeClusterer(AbstractClusterer):

    class RELATIVE_TIME_ABSTRACTIONS(Enum):
        MONTH = "MONTH"
        WEEK = "WEEK"
        DAY = "DAY"
        HOUR = "HOUR"
        MINUTE = "MINUTE"
        SECOND = "SECOND"

    def __init__(self, col_name):
        super().__init__(col_name)
        self.set_abstraction(None)

    def build_abstractions(self, col_name):
        return {
            f"relativetime{col_name}_abstracted": RelativeTimeAbstraction(col_name, col_name, abstract_time_complete, 0),
            f"relativetime{col_name}_week": RelativeTimeAbstraction(col_name, col_name, abstract_time_to_week, 1),
            f"relativetime{col_name}_day": RelativeTimeAbstraction(col_name, col_name, abstract_time_to_day, 2),
            f"relativetime{col_name}_hour": RelativeTimeAbstraction(col_name, col_name, abstract_time_to_hour, 3),
            f"relativetime{col_name}_minute": RelativeTimeAbstraction(col_name, col_name, abstract_time_to_minute, 4),
            f"relativetime{col_name}_not_abstracted": RelativeTimeAbstraction(col_name, col_name, instance_clusterer.abstract_instance, 100),
        }


class RelativeTimeAbstraction(AbstractAbstraction):
    def __init__(self, source_col, target_col, abstraction_function, ranking=1):
        super().__init__(source_col, target_col, abstraction_function, ranking)

    def apply_abstraction(self, value):
        # timestamps raise problems with json
        abstracted_value = self.abstraction_function(value)
        self.l_div_map[str(abstracted_value)].add(str(value))
        return abstracted_value


def abstract_time_complete(timedelta):
    return pd.Timedelta(0)

def abstract_time_to_week(td):
    weeks = td.days // 7
    return datetime.timedelta(weeks=weeks)

def abstract_time_to_day(timedelta):
    return datetime.timedelta(timedelta.days)

def abstract_time_to_hour(td):
    total_seconds = td.total_seconds()
    hours = int(total_seconds // 3600)
    return datetime.timedelta(hours=hours)

def abstract_time_to_minute(td):
    total_seconds = td.total_seconds()
    minutes = int(total_seconds // 60)
    return datetime.timedelta(minutes=minutes)
