'''
SEAMLESS_ZOOM — A technique for seamless zooming between process models and process instances.
Copyright (C) 2025  Christoffer Rubensson

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU Affero General Public License as
published by the Free Software Foundation, either version 3 of the
License, or any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU Affero General Public License for more details.

You should have received a copy of the GNU Affero General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.

Website: https://hu-berlin.de/rubensson
E-Mail: {firstname.lastname}@hu-berlin.de
'''

# Data processing and transformation methods

import numpy as np
import math
import pandas as pd
import pm4py


def relativeTimestamps(df):
    '''adds relative timestamps to dataframe (log).
    '''
    starttimes_dict = df.groupby("case:concept:name")["time:timestamp"].min().to_dict()
    df["time:timestamp:casestart"] = df["case:concept:name"].map(starttimes_dict)
    df["time:timestamp:relative"] = df["time:timestamp"] - df["time:timestamp:casestart"]
    df["time:relative:seconds"] = df["time:timestamp:relative"].apply(lambda t: t.total_seconds()).astype(int)
    df['time:relative:seconds:log'] = np.log(df['time:relative:seconds'] + 1)

    return df


def timestamp_to_seconds(df):
    print("converting timestamps to seconds...")
    df["time_timestamp_seconds"] = df["time:timestamp:relative"].apply(lambda t: t.total_seconds()).astype(int)
    print("conversion complete.")
    return df

def simplifyLog(df, lifecycle_activities=False,
                filter_cases = 0, filter_variants_k = 0,
                filter_variants_per = 0,
                act_col='concept:name', case_col='case:concept:name',
                time_col='time:timestamp', lifecycle_col='lifecycle:transition', res_col='org:resource'):
    '''simplifies a log by keeping only necessary attributes.
    '''
    # keep following columns
    keep_columns = [case_col, act_col, time_col, res_col]

    # CHECK ATTRIBUTES
    # check if resource attribute is in the log
    if res_col not in df.columns:
        if 'org:group' in df.columns:
            res_col = 'org:group'
        else:
            keep_columns.remove(res_col)
    # create new activities with transitions, if applicable
    if (lifecycle_activities == True and
        lifecycle_col in df.columns):
        if len(df[lifecycle_col].unique()) > 1:
            df[act_col] = df[act_col] + '-' + df[lifecycle_col]
        else:
            print('Message: No transition-activity were be created. Only one type of lifecycle transition in log.')
    else:
        print('Message: No transition-activity were be created. No transition column.')

    # LOG FILTERING
    # keep only k amount cases in the log
    total_num_variants = len(pm4py.get_variants(df))
    if filter_cases > 0:
        case_list = df[case_col].unique()[0:filter_cases]
        df = pm4py.filter_event_attribute_values(df, case_col, case_list, level="case", retain=True).copy()
    elif filter_variants_k > 0:
        df = pm4py.filter_variants_top_k(df, filter_variants_k).copy()
    elif filter_variants_per > 0:
        filter_variants_k = math.ceil(filter_variants_per*total_num_variants)
        df = pm4py.filter_variants_top_k(df, filter_variants_k).copy()

    # keep only certain columns
    df = df.filter(keep_columns)
    return df

def create_quantile_dict_from_grouped_dataframe(
    df: pd.DataFrame, colgroup:str, colquantile:str, quantile=.1) -> dict:
    return df.groupby(colgroup)[colquantile].quantile(quantile).to_dict()

def create_quantile_dataframe_from_dataframe(
    df:pd.DataFrame, colgroup:str,
    colquantile:str, quantiles=[.0, .1, .25, .5, .75, .9, 1.]) -> pd.DataFrame:
    df_quantile = pd.DataFrame(df[colgroup].unique().tolist())
    df_quantile = df_quantile.rename(columns={0: colgroup})
    for quantile in quantiles:
        quantile_dict = create_quantile_dict_from_grouped_dataframe(df, colgroup, colquantile, quantile)
        newcolname = "q_"+str(quantile)
        df_quantile[newcolname] = df_quantile[colgroup].map(quantile_dict)
    return df_quantile

def create_dict_from_integer(num_keys: int):
    return {i: None for i in range(1, num_keys + 1)}

def filter_tuplekeys_by_prefix(dictionary: dict, word: str, type="prefix"):
    """Filter a dictionary with tuple keys starting with a certain string."""
    pos = 0
    if type == "prefix":
        None
    elif type == "suffix":
        pos = 1
    else:
        raise ValueError("Type must be either 'prefix' or 'suffix'.")
    filtered_dictionary = {key: v for key, v in dictionary.items() if key[pos].startswith(word)}
    return filtered_dictionary

def sort_dict_by_values(dictionary: dict, reverse=False):
    """Sorts a dictionary based on its values."""
    new_dictionary = dict(sorted(dictionary.items(), key=lambda item: item[1], reverse=reverse))
    return new_dictionary

def switch_item_key_in_dictionary(dictionary: dict):
    """Switches items with keys in a dictionary. Also works when items are lists."""
    switched_dictionary = {}
    for key in dictionary:
        if type(dictionary[key]) is list:
            for i in range(0, len(dictionary[key])):
                switched_dictionary[dictionary[key][i]] = key
        else:
            switched_dictionary[dictionary[key]] = key
    return switched_dictionary

def rename_cols_for_d3csv(
        df, time_col = 'time:timestamp',
        reltime_col = 'time:relative:seconds', case_col = 'case:concept:name',
        act_col = 'concept:name', resources_col = 'org:resource', time_abstacted_col = 'time:timestamp_abstracted'):
    """Creates a dataframe with new column names for D3.js."""

    print(df.columns)
    if 'concept:name:ranked' in df.columns:
        act_col = 'concept:name:ranked'

    if resources_col not in df.columns:
        resources_col = 'org:group'

    columns_newnames = {
        time_col: 'timestamps',
        reltime_col: 'timestamp_relative_seconds',
        case_col: 'case',
        act_col: 'activity',
        resources_col: 'resources',
        time_abstacted_col: 'time_abstracted'
    }
    return df.rename(columns = columns_newnames)

def convert_timecols_to_string(df):
    """
    Finds all columns in a DataFrame that are of datetime or timedelta type and converts them to string type.
    """
    df_str = df.copy()
    convert_columns = []
    for col in df_str.columns:
        if pd.api.types.is_datetime64_any_dtype(df_str[col]):
            df_str[col] = df_str[col].dt.strftime('%Y-%m-%dT%H:%M:%S')
            convert_columns.append(col)
        elif pd.api.types.is_timedelta64_dtype(df_str[col]):
            df_str[col] = df_str[col].dt.total_seconds().astype(str)
            convert_columns.append(col)
    #df_str[convert_columns] = df_str[convert_columns].astype(str)
    print("Converted columns to string:", convert_columns)
    return df_str