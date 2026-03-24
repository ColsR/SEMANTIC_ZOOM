import pandas as pd

from src.clustering import instance_clusterer


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
            "time_month": (col_name, abstract_time_to_month),
            "time_week": (col_name, abstract_time_to_week),
            "time_day": (col_name, abstract_time_to_day),
            "time_hour": (col_name, abstract_time_to_hour),
            "time_minute": (col_name, abstract_time_to_minute),
            "time_not_abstracted": (col_name, instance_clusterer.abstract_instance),
        }
