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
import logging

import pandas as pd
# Ranking algorithms for event data
import pm4py
from src.utils.data_processing import create_dict_from_integer, filter_tuplekeys_by_prefix, sort_dict_by_values, switch_item_key_in_dictionary

logger = logging.getLogger(__name__)

def global_ranking_of_eventdata(
        df, method = "df_realtime_mean", 
        indexswitch=True, rank_col="ranks",
        act_col="concept:name", actrank_col="concept:name:ranked",
        reltime_col="time:relative:seconds"):
    """Defines a global rank for event data."""
    global_rank_dict = {}
    
    if method == "df_realtime_mean":
        global_rank_dict = global_ranking_method_df_relativetime(
            df, agg_func="mean", act_col=act_col, reltime_col=reltime_col)
    elif method == "df_frequency":
        global_rank_dict = global_ranking_method_df_frequency(df)
    else:
        raise ValueError(
            "Method must be: 'df_realtime_mean' or 'df_frequency'")
    
    # switch the keys and values of the dictionary
    if indexswitch == True:
        global_rank_dict = switch_item_key_in_dictionary(global_rank_dict).copy()

    # add new ranking columns to dataframe
    df_withranks = df.copy()
    df_withranks[rank_col] = df_withranks[act_col].map(global_rank_dict)
    df_withranks[actrank_col] = df_withranks[rank_col].astype(str) + "_" + df_withranks[act_col]
    return df_withranks, global_rank_dict

def global_ranking_method_df_relativetime(
        df, agg_func="mean", act_col="concept:name", reltime_col="time:relative:seconds",
        annotation=False):
    """
    Method that derives the global ranks of event data based on the 
    activites' relative timestamps.
    """

    ## SORT LISTS
    # list all activites based on their aggregated relative times (e.g., mean)
    activity_group = df.groupby(act_col)[reltime_col].agg(agg_func).sort_values(ascending=True)
    activity_group_list = activity_group.keys().to_list()

    # calculate footprint matrix
    footprints = pm4py.discover_footprints(df)

    # divide activites into sets
    start_activities = set(footprints["start_activities"])
    end_activities = set(footprints["end_activities"]) - start_activities
    all_activities = set(footprints["activities"])
    int_activities = all_activities - start_activities - end_activities

    # error check for missing activities
    missing_activities = all_activities - set(activity_group_list)
    if missing_activities:
        logger.warning("Warning: The following activities were expected but missing:", missing_activities)

    # Sort activities based on their type and timestamp
    start_act_sorted = [a for a in activity_group_list if a in start_activities]
    int_act_sorted = [a for a in activity_group_list if a in int_activities]
    end_act_sorted = [a for a in activity_group_list if a in end_activities]
    missing_act_sorted = [a for a in activity_group_list if a not in start_activities and a not in int_activities and a not in end_activities]

    # add annotations about the activity type, if applicable
    start_annotation = "_s_" if annotation else ""
    int_annotation = "_i_" if annotation else ""
    end_annotation = "_e_" if annotation else ""
    nan_annotation = "_nan_" if annotation else ""

    ## CREATE RANKINGS
    # assign ranks to activities
    rank_dict = dict()
    current_index = 1

    for activity in start_act_sorted:
        rank_dict[current_index] = start_annotation + activity
        current_index += 1
    for activity in int_act_sorted:
        rank_dict[current_index] = int_annotation + activity
        current_index += 1
    for activity in end_act_sorted:
        rank_dict[current_index] = end_annotation + activity
        current_index += 1
    for activity in missing_act_sorted:
        rank_dict[current_index] = nan_annotation + activity
        current_index += 1
    
    return rank_dict

def global_ranking_method_df_frequency(df):
    """Method that derives the global ranks of event data based on the 
    activities likely directly follows relations."""
    # calculate footprint matrix
    footprints = pm4py.discover_footprints(df)

    # derive lists of activites
    start_activities = []
    for activity in footprints["start_activities"]:
        start_activities.append(activity)
    activities = []
    for activity in footprints["activities"]:
        if activity not in start_activities:
            activities.append(activity)

    # create rankings without items
    rank_len = len(start_activities) + len(activities)
    rank_dict = create_dict_from_integer(rank_len)

    # add all start activities
    for activity in start_activities:
        rank = check_next_empty_item(rank_dict)
        rank_dict[rank] = activity

    # rank the rest of the activities based on the frequency of directly follows relations
    for rank in rank_dict.keys():
        current_activity = rank_dict[rank]
        dfrelations_dict = sort_dict_by_values(filter_tuplekeys_by_prefix(
            footprints["dfg"],current_activity, type="prefix"), reverse=True)
        dfrelations = dfrelations_dict.keys()
        for dfrelation in dfrelations:
            next_activity = dfrelation[1]
            if next_activity in activities:
                next_rank = check_next_empty_item(rank_dict)
                rank_dict[next_rank] = next_activity
                activities.remove(next_activity)
    return rank_dict

def check_next_empty_item(dictionary: dict):
    """Return the key of the next empty key in a dictionary."""
    for key in dictionary.keys():
        if dictionary[key] is None:
            return key

def delete_columns(df: pd.DataFrame):
    df.drop(columns=["time:timestamp:casestart", "timestamp_relative_seconds", "time:relative:seconds:log", "ranks",
                     "activity", "time:timestamp:relative"], inplace=True, errors="ignore")
    return df