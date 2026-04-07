from pathlib import Path

import pandas as pd
import pm4py

from src.clustering import time_clusterer

def build_mask(df, filter_source_column, filter_attribute):
    filter_func = lambda x : x == filter_attribute
    mask = df[filter_source_column].apply(filter_func)
    return mask.tolist()
"""
def general_abstraction(df, column, abstraction, exclude_filter):
    df[column + '_abstracted'] = df[column].apply(lambda x: abstraction(x))
    return df


def general_exclusion(df, column, abstraction, exclude_filter=None):
    df[column + '_abstracted'] = df[column]

    if exclude_filter is not None:
        mask = ~df.apply(exclude_filter, axis=1)
    else:
        mask = [True] * len(df)

    df.loc[mask, column + '_abstracted'] = df.loc[mask, column].apply(abstraction)

    return df
"""
def rename_exclusion(df, column, abstraction, exclude_filter=None):
    if exclude_filter is not None:
        mask = ~df.apply(exclude_filter, axis=1)
    else:
        mask = [True] * len(df)

    df.loc[mask, column] = df.loc[mask, column].apply(abstraction)

    return df

def exclude_activity(activity, column = 'concept:name'):
    def filter_func(row):
        return row[column] == activity
    return filter_func

EXCLUDING_FUNCTIONS = {
    "activity_register_request_time_month": ('time:timestamp', exclude_activity("register request")),
    "examine casually_time_month": ('time:timestamp', exclude_activity("examine casually")),
}


if __name__ == '__main__':
    project_root = Path(__file__).resolve().parent.parent.parent
    FILEPATH = project_root / 'data'
    df = pm4py.read_xes(str(FILEPATH / 'evaluation_data' / 'runningexample.xes'))
    print(df)
    mask = build_mask(df, 'concept:name', 'register request')
    print(mask)