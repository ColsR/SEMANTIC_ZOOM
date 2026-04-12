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
import logging
from pathlib import Path

from src.algo.global_ranking import global_ranking_of_eventdata
from src.clustering import general_clusterer, specific_clusterer
from src.clustering.general_clusterer import cluster_abstraction
from src.utils.data_processing import rename_cols_for_d3csv, convert_timecols_to_string
from src.utils.data_processing import simplifyLog, relativeTimestamps

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

def process_log_for_d3js_abstractions(df, requested_clusters, sp_zooms):
    """
    Pre-process the event log for visualization in d3.js.
    """
    df_proc = df.copy()
    # Process data
    df_proc = simplifyLog(df_proc)
    df_proc = relativeTimestamps(df_proc)
    df_proc, _ = global_ranking_of_eventdata(df_proc)


    # Mask for standard abstraction: abstract every entry
    standard_mask = [True] * len(df_proc)
    for cluster_obj in requested_clusters:
        cluster_obj.set_mask(list(standard_mask.copy()))

    # Specific Zooming - build abstraction object and set information for building their mask, but not build at this moment
    ABSTRACTION_FUNCTIONS, FLAT_ABSTRACTION_FUNCTIONS, ABSTRACTION_OBJECTS, COLUMN_ABSTRACTION_MAPPING = general_clusterer.get_abstractions()  # build_abstractions
    for specific_zooming in sp_zooms:
        sp_target_column = specific_zooming['target_column']
        sp_source_column = specific_zooming['filter_column']
        sp_filter_attribute = specific_zooming['filter_attribute']
        sp_abstraction_function = specific_zooming['abstraction_function']

        clusterer = ABSTRACTION_OBJECTS.get(sp_target_column)
        if clusterer is None:
            logger.warning(f"Cannot find clusterer for column {sp_target_column} in COLUMN_ABSTRACTION_MAPPING. Continue")
            continue
        sp_abstraction = copy.deepcopy(clusterer.abstractions.get(sp_abstraction_function))
        if sp_abstraction is None:
            logger.warning(f"Cannot find abstraction function {sp_abstraction_function} for column {sp_target_column} in clusterer. Continue")
            continue

        sp_abstraction.set_mask_source_column(sp_source_column)
        sp_abstraction.set_mask_filter_attribute(sp_filter_attribute)
        # ADD new abstraction.
        clusterer.add_specific_abstraction(sp_abstraction)


    # Dependency detection and get order for applying the cluster
    cluster_order = specific_clusterer.build_dependency_graph(requested_clusters)

    # build masks for specific abstractions and apply the clusterer
    for cluster_aggr in cluster_order:
        for cluster_obj, abstraction_list in cluster_aggr.items():
            for abstraction in abstraction_list:
                if abstraction.mask_filter_attribute is not None:
                    sp_mask = specific_clusterer.build_mask(df_proc, abstraction.mask_source_col, abstraction.mask_filter_attribute)
                    abstraction.set_mask(sp_mask)
            if not cluster_obj.check_columns(df_proc.columns):
                logger.warning("Cannot Apply abstraction because source or target column is not in dataframe. Use default Abstraction")
                cluster_obj.set_abstraction(None)
            cluster_obj.calculate_masks()
            df_proc = cluster_abstraction(df_proc, cluster_obj)

    logger.debug(df_proc.head())
    #df_proc = rename_cols_for_d3csv(df_proc)
    logger.debug("nach renaming")
    logger.debug(df_proc.head())
    df_proc = convert_timecols_to_string(df_proc) # Convert Timedelta to string (JSON cannot handle Timedelta or Datetime)
    df_proc = df_proc.fillna("nan") # In case some values are NaN, replace them with "nan" string for JSON compatibility
    return df_proc
