import pandas as pd


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
