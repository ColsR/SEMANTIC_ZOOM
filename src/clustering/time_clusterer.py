from enum import Enum

import pandas as pd

from src.clustering import instance_clusterer
from src.clustering.abstract_abstraction import AbstractAbstraction
from src.clustering.abstract_clusterer import AbstractClusterer
from src.clustering.instance_clusterer import InstanceClusterer


class TimeClusterer(AbstractClusterer):

    class TIME_ABSTRACTIONS(Enum):
        MONTH = "MONTH"
        WEEK = "WEEK"
        DAY = "DAY"
        HOUR = "HOUR"
        MINUTE = "MINUTE"
        SECOND = "SECOND"

    def __init__(self, col_name, abstraction):
        super().__init__(col_name)
        self.set_abstractions(abstraction)

    def build_abstractions(self, col_name):
        return {
            "time_abstracted": (col_name, TimeAbstraction(col_name, col_name, abstract_time_complete)),
            "time_year": (col_name,TimeAbstraction(col_name, col_name,  abstract_time_to_year)),
            "time_month": (col_name,TimeAbstraction(col_name, col_name, abstract_time_to_month)),
            "time_week": (col_name,TimeAbstraction(col_name, col_name, abstract_time_to_week)),
            "time_day": (col_name,TimeAbstraction(col_name, col_name, abstract_time_to_day)),
            "time_hour": (col_name,TimeAbstraction(col_name, col_name, abstract_time_to_hour)),
            "time_minute": (col_name,TimeAbstraction(col_name, col_name, abstract_time_to_minute)),
            "time_not_abstracted": (col_name,TimeAbstraction(col_name, col_name, instance_clusterer.abstract_instance)),
        }

    def set_abstractions(self, abstraction_function):
        sel_func = self.abstractions.get(abstraction_function)
        if sel_func is None:
            self.abstraction_object = TimeAbstraction(self.col_name, self.col_name, abstract_time_complete)
            return False
        else:
            self.abstraction_object = sel_func[1]
            return True


class TimeAbstraction(AbstractAbstraction):
    def __init__(self, source_col, target_col, abstraction_function):
        super().__init__(source_col, target_col, abstraction_function)


def abstract_time_complete(timestamp):
    return pd.Timestamp(0)

def abstract_time_to_year(timestamp):
    return timestamp.replace(month=1, day=1, hour=0, minute=0, second=0, microsecond=0)

def abstract_time_to_month(timestamp):
    return timestamp.replace(day=1, hour=0, minute=0, second=0, microsecond=0)

def abstract_time_to_week(timestamp):
    timestamp = timestamp.normalize()
    return timestamp - pd.to_timedelta(timestamp.weekday(), unit='d')

def abstract_time_to_day(timestamp):
    return timestamp.normalize()

def abstract_time_to_hour(timestamp):
    return timestamp.replace(minute=0, second=0, microsecond=0)

def abstract_time_to_minute(timestamp):
    return timestamp.replace(second=0, microsecond=0)

def abstract_time_to_second(timestamp):
    return timestamp.replace(microsecond=0)
