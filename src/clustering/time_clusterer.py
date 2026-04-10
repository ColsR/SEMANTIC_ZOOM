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

    def __init__(self, col_name):
        super().__init__(col_name)
        self.set_abstraction(None)

    def build_abstractions(self, col_name):
        return {
            "time_abstracted": TimeAbstraction(col_name, col_name, abstract_time_complete, 0),
            "time_year": TimeAbstraction(col_name, col_name,  abstract_time_to_year, 1),
            "time_month": TimeAbstraction(col_name, col_name, abstract_time_to_month, 2),
            "time_week": TimeAbstraction(col_name, col_name, abstract_time_to_week, 3),
            "time_day": TimeAbstraction(col_name, col_name, abstract_time_to_day, 4),
            "time_hour": TimeAbstraction(col_name, col_name, abstract_time_to_hour, 5),
            "time_minute": TimeAbstraction(col_name, col_name, abstract_time_to_minute, 6),
            "time_not_abstracted": TimeAbstraction(col_name, col_name, instance_clusterer.abstract_instance, 100),
        }

    """
    def set_abstractions(self, abstraction_function):
        sel_func = self.abstractions.get(abstraction_function)
        if sel_func is None:
            self.abstraction_object = TimeAbstraction(self.col_name, self.col_name, abstract_time_complete, 0)
            return False
        else:
            self.abstraction_object = sel_func[1]
            return True
    """

class TimeAbstraction(AbstractAbstraction):
    def __init__(self, source_col, target_col, abstraction_function, ranking=1):
        super().__init__(source_col, target_col, abstraction_function, ranking)


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
