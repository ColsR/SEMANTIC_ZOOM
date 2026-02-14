from pathlib import Path

import pandas as pd
import pm4py
from src.clustering import time_clusterer, activity_clusterer, ressource_clusterer

def general_abstraction(df, column, abstraction):
    df[column + '_abstracted'] = df[column].apply(lambda x: abstraction(x))
    return df

def rename_abstraction(df, column, abstraction):
    df[column] = df[column].apply(lambda x: abstraction(x))
    return df



ABSTRACTION_FUNCTIONS = {
    "time_month": ('time:timestamp', time_clusterer.abstract_time_to_month),
    "time_week": ('time:timestamp', time_clusterer.abstract_time_to_week),
    "time_day": ('time:timestamp', time_clusterer.abstract_time_to_day),
    "time_hour": ('time:timestamp', time_clusterer.abstract_time_to_hour),
    "time_minute": ('time:timestamp', time_clusterer.abstract_time_to_minute),
    "activity_abstracted": ('concept:name', activity_clusterer.abstract_activity),
    "activity_abstracted2": ('concept:name', activity_clusterer.abstract_activity2),
    "resource_abstracted": ('org:resource', ressource_clusterer.abstract_resource_complete)
}


def abstraction_1(df):
    print(df.columns)
    df = rename_abstraction(df, 'concept:name', activity_clusterer.abstract_activity2)
    print("abstracted activities")
    print(df)
    return rename_abstraction(df, 'time:timestamp', time_clusterer.abstract_time_to_week)

if __name__ == '__main__':
    project_root = Path(__file__).resolve().parent.parent.parent
    FILEPATH = project_root / 'data'
    df = pm4py.read_xes(str(FILEPATH / 'evaluation_data' / 'runningexample.xes'))
    df_abstracted = general_abstraction(df, 'time:timestamp', time_clusterer.abstract_time_to_day)
    df_abstracted = general_abstraction(df_abstracted, 'org:resource', ressource_clusterer.abstract_resource_complete)
    df_abstracted = general_abstraction(df_abstracted, 'concept:name', activity_clusterer.abstract_activity)
    df.to_csv(FILEPATH / 'abstracted_df.csv')
