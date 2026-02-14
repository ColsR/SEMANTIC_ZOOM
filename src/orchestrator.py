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
from src.clustering.general_clusterer import rename_abstraction
from src.utils.data_processing import simplifyLog, relativeTimestamps
from src.algo.global_ranking import global_ranking_of_eventdata
from src.utils.data_processing import rename_cols_for_d3csv, convert_timecols_to_string

def process_log_for_d3js(df):
    """
    Pre-process the event log for visualization in d3.js.
    """
    df_proc = df.copy()
    # Process data
    df_proc = simplifyLog(df_proc)
    df_proc = relativeTimestamps(df_proc)
    df_proc, _ = global_ranking_of_eventdata(df_proc)
    df_proc = rename_cols_for_d3csv(df_proc)
    df_proc = convert_timecols_to_string(df_proc) # Convert Timedelta to string (JSON cannot handle Timedelta or Datetime)
    df_proc = df_proc.fillna("nan") # In case some values are NaN, replace them with "nan" string for JSON compatibility
    return df_proc

def process_log_for_d3js_abstractions(df, abstractions):
    """
    Pre-process the event log for visualization in d3.js.
    """
    df_proc = df.copy()
    # Process data
    df_proc = simplifyLog(df_proc)
    df_proc = relativeTimestamps(df_proc)

    # Apply abstractions
    for (column, abstraction_fct) in abstractions:
        df_proc = rename_abstraction(df_proc, column, abstraction_fct)

    df_proc, _ = global_ranking_of_eventdata(df_proc)
    df_proc = rename_cols_for_d3csv(df_proc)
    df_proc = convert_timecols_to_string(df_proc) # Convert Timedelta to string (JSON cannot handle Timedelta or Datetime)
    df_proc = df_proc.fillna("nan") # In case some values are NaN, replace them with "nan" string for JSON compatibility
    return df_proc