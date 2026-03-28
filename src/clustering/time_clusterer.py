from enum import Enum

import pandas as pd

from src.clustering import instance_clusterer
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
        self.abstraction_function = abstraction






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

def get_all(col_name):
    return {
            "time_month": (col_name, TimeClusterer(col_name, abstract_time_to_month)),
            "time_week": (col_name, TimeClusterer(col_name, abstract_time_to_week)),
            "time_day": (col_name, TimeClusterer(col_name, abstract_time_to_day)),
            "time_hour": (col_name, TimeClusterer(col_name, abstract_time_to_hour)),
            "time_minute": (col_name, TimeClusterer(col_name,abstract_time_to_minute)),
            "time_not_abstracted": (col_name, InstanceClusterer(col_name, instance_clusterer.abstract_instance)),
        }
