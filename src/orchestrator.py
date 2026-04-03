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
import copy
import json
import logging
from pathlib import Path

from src.clustering import general_clusterer, specific_clusterer
from src.clustering.general_clusterer import rename_abstraction, object_abstraction
from src.clustering.specific_clusterer import rename_exclusion
from src.utils.data_processing import simplifyLog, relativeTimestamps
from src.algo.global_ranking import global_ranking_of_eventdata
from src.utils.data_processing import rename_cols_for_d3csv, convert_timecols_to_string
import src.clustering.time_clusterer as time_clusterer

logger = logging.getLogger(__name__)

project_root = Path(__file__).resolve().parent.parent
FILEPATH =  project_root / "data" / "working_data"

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
    df_proc, _ = global_ranking_of_eventdata(df_proc)


    # TODO die masken müssen noch korrekt berechnet werden: über die Spalten: Standard als logische NOR Verkmüpfung, ggf. mal schauen wie man es mit dem Ranking macht. Ggf. muss man allen Abstraktionsmöglichkeiten noch ein Ranking mitgeben

    standard_mask = [True] * len(df_proc)
    for cluster_obj in abstractions:
        cluster_obj.set_mask(standard_mask)
    """
    for (column, abstraction_obj) in abstractions:
        abstraction_obj.set_mask(standard_mask)
    """
    # Specific Zooming
    # TODO pass as parameter not loaded from file
    ABSTRACTION_FUNCTIONS, FLAT_ABSTRACTION_FUNCTIONS, ABSTRACTION_OBJECTS, COLUMN_ABSTRACTION_MAPPING = general_clusterer.get_abstractions()  # build_abstractions
    """with open(f'{FILEPATH}/specific_zooms.json', 'r') as f:
        specific_zoomings = json.load(f)
        for specific_zooming in specific_zoomings:
            sp_target_column = specific_zooming['target_column']
            sp_source_column = specific_zooming['filter_column']
            sp_filter_attribute = specific_zooming['filter_attribute']
            sp_abstraction_function = specific_zooming['abstraction_function']
            logger.info(f"Processing {sp_target_column} -> {sp_source_column} for {sp_filter_attribute} with {sp_abstraction_function}")
            if (t_std_abstraction := FLAT_ABSTRACTION_FUNCTIONS.get(sp_abstraction_function)) is not None:
                _, std_abstraction = t_std_abstraction
                # TODO man könnte noch drüber nachdenken, ob man die Info auf welceh Spalte die Abstraktion ausgeführt werden soll nicht aus der json kommt, sondern aus der ursprünglichen Abstraktionsdefinition bzw. zumindest asserten und dann loggen wenn es nicht passt
                sp_abstraction = copy.deepcopy(std_abstraction)
                sp_mask = specific_clusterer.build_mask(df_proc, sp_source_column, sp_filter_attribute)
                sp_abstraction.set_mask(sp_mask)
                # ADD new abstraction.
                abstractions.append((sp_target_column,sp_abstraction))

    """
    # Apply abstractions
    """
    for (column, abstraction_obj) in abstractions:
        # Hier hat man dann das AbstrkationsObjekt auf Spalten Ebene, das man nutzt, um die Abstraktion anzuwenden
        logger.debug(f"Apply Abstraction {abstraction_obj} on column {column}")
        df_proc = rename_abstraction(df_proc, column, abstraction_obj.col_name, abstraction_obj.apply_abstraction, abstraction_obj.mask)
    """
    for cluster_obj in abstractions:
        if not cluster_obj.check_columns(df_proc.columns):
            logger.warning("Cannot Apply abstraction because source or target column is not in dataframe. Use default Abstraction")
            cluster_obj.set_abstractions(None)
        df_proc = object_abstraction(df_proc, cluster_obj.col_name, cluster_obj.col_name, cluster_obj, cluster_obj.mask)
    logger.debug(df_proc.head())
    #df_proc = rename_cols_for_d3csv(df_proc)
    logger.debug("nach renaming")
    logger.debug(df_proc.head())
    df_proc = convert_timecols_to_string(df_proc) # Convert Timedelta to string (JSON cannot handle Timedelta or Datetime)
    df_proc = df_proc.fillna("nan") # In case some values are NaN, replace them with "nan" string for JSON compatibility
    return df_proc

def process_log_for_d3js_exclusions(df, exclusions):
    """
    Pre-process the event log for visualization in d3.js.
    """
    df_proc = df.copy()
    # Process data
    df_proc = simplifyLog(df_proc)
    df_proc = relativeTimestamps(df_proc)

    # Apply abstractions
    for (column, filter_function) in exclusions:
        df_proc = rename_exclusion(df_proc, column, time_clusterer.abstract_time_to_month, filter_function)
    #print("AFTER")
    #print(df_proc)
    df_proc, _ = global_ranking_of_eventdata(df_proc)
    df_proc = rename_cols_for_d3csv(df_proc)
    df_proc = convert_timecols_to_string(df_proc) # Convert Timedelta to string (JSON cannot handle Timedelta or Datetime)
    df_proc = df_proc.fillna("nan") # In case some values are NaN, replace them with "nan" string for JSON compatibility
    return df_proc