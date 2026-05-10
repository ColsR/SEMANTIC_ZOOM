from pathlib import Path

import pandas as pd

from src.utils.data_exporting import export_event_log_custom

max_zoom_df = None

project_root = Path(__file__).resolve().parent.parent.parent.parent
FILEPATH = project_root / 'data' / 'working_data'

def init_max_zoom_df(df):
    global max_zoom_df
    max_zoom_df = df.copy()
    for column in max_zoom_df.columns:
        max_zoom_df[f"rank_{column}"] = -1



def get_max_zoom_df():
    global max_zoom_df
    return max_zoom_df

def filter_by_cases(cases_to_delete):
    global max_zoom_df
    max_zoom_df = max_zoom_df[
        ~max_zoom_df["case:concept:name"].isin(cases_to_delete)
    ]



def export_max_zoom_df():
    global max_zoom_df
    df_to_export = max_zoom_df.copy()
    cols_to_drop = [col for col in df_to_export.columns if "rank_" in col]
    df_to_export = df_to_export.drop(columns=cols_to_drop)
    export_event_log_custom(df_to_export,f'{FILEPATH}/max_zoom.xes')