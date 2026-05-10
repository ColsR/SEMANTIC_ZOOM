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

import json
import logging
import os
import shutil
import sys
import tempfile
from pathlib import Path

from dotenv import load_dotenv
from flask import Blueprint, render_template, request, jsonify

import src.analysis.attribute_extractor as attribute_extractor
from src.algo.global_ranking import global_ranking_of_eventdata
from src.algo.super_graph import build_super_graph
from src.analysis.data_extraction import get_occurring_entries
from src.analysis.privacy import max_zoom
from src.analysis.privacy.privacy_checker import delete_trace, check_metrics, delete_trace2
from src.clustering import general_clusterer, numerical_clusterer
from src.clustering.specific_clusterer import CycleDetectedException
from src.orchestrator import process_log_for_d3js_abstractions
from src.utils.data_exporting import export_event_log_custom
from src.utils.data_importing import load_event_log_from_tempfile
from src.utils.data_processing import simplifyLog, relativeTimestamps

# App directory
project_root = Path(__file__).resolve().parent.parent
sys.path.append(str(project_root))
log_level = os.getenv("LOG_LEVEL", "INFO").upper()
logging.basicConfig(
    level=getattr(logging, log_level),
    force=True
)

logger = logging.getLogger(__name__)

bp = Blueprint("pages", __name__)

config = {}

def load_config():
    global config
    load_dotenv()
    config["K_EVENT"] = int(os.getenv("K_EVENT"))
    config["K_EDGE"] = int(os.getenv("K_EDGE"))
    config["K_TRACE"] = int(os.getenv("K_TRACE"))
    config["L_DIV"] = int(os.getenv("L_DIV"))

    config["DELETE_TRACES"] = os.getenv("DELETE_TRACES") == "True"
    config["ENFORCE_PRIVACY"] = os.getenv("ENFORCE_PRIVACY") == "True"
    config["SINGLE_EVENT_L_DIV"] = os.getenv("SINGLE_EVENT_L_DIV") == "True"
    config["FOlLOW_EVENT_L_DIV"] = os.getenv("FOLLOW_EVENT_L_DIV") == "True"

    config["DECOUPLE_TRACES"] = os.getenv("DECOUPLE_TRACES") == "True"

    config["EXPORT_ABSTRACTED_LOG"] = os.getenv("EXPORT_ABSTRACTED_LOG") == "True"

FILEPATH = project_root / 'data' / 'working_data'
# Import allowance fo file extensions
ALLOWED_EXTENSIONS = {'xes'}
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@bp.route("/")
def home():
    return render_template("pages/index.html")

@bp.route('/api/upload_data', methods=['POST'])
def upload_data():
    load_config()
    if 'file' not in request.files:
        return jsonify({'error': 'No file uploaded'}), 400

    file = request.files['file']
    filename = file.filename

    if filename == '':
        return jsonify({'error': 'No file selected'}), 400

    if not allowed_file(filename):
        return jsonify({'error': 'Invalid file type. Only {ALLOWED_EXTENSIONS} allowed.'}), 400

    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".xes") as tmp:
            file.save(tmp)
            tmp_path = tmp.name
        shutil.copy(tmp_path, f"{FILEPATH}/persistent_log.xes")

        # preprocess for injecting the artificial attributes (relative_timestamp, ranked_activities)
        # then the attribute extractor see these attributes too
        general_clusterer.reset_abstractions()
        df = load_event_log_from_tempfile(tmp_path)
        df = simplifyLog(df)
        df = relativeTimestamps(df)
        df, _ = global_ranking_of_eventdata(df)
        export_event_log_custom(df, tmp_path)
        max_zoom.init_max_zoom_df(load_event_log_from_tempfile(tmp_path))

        attribute_extractor.reset_attribute_mapping()
        attribute_extractor.extract_attributes(tmp_path)
        attribute_extractor.extract_attribute_type_mapping()
        attribute_extractor.write_to_file()

        logger.info(f"Extracted trace attributes: {attribute_extractor.trace_attributes}")
        logger.info(f"Extracted event attributes: {attribute_extractor.event_attributes}")

        numerical_clusterer.build_abstractions(df)
        general_clusterer.get_abstractions() # build_abstractions
        # Clean up temporary file
        os.remove(tmp_path)
        return jsonify({'success': 'OK'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bp.route("/api/abstracted_data", methods=['POST'])
def get_abstracted_data():
    global config
    data = request.get_json()
    requested_abstractions = data.get("abstractions")
    requested_sp_zooms = data.get("specific_zooms")
    logger.info(f"requested abstractions: {requested_abstractions}")

    ABSTRACTIONS_OBJECTS, COlUMN_ABSTRACTION_MAPPING = general_clusterer.get_abstractions() # build_abstractions
    for cluster_obj in ABSTRACTIONS_OBJECTS.values():
        cluster_obj.reset_specific_abstractions() # build requested specific abstractions everytime new

    requested_cluster = []
    for requested_abstraction in requested_abstractions:
        col_name = COlUMN_ABSTRACTION_MAPPING[requested_abstraction]
        if col_name is None:
            logger.warning("requested abstraction does not have a corresponding column in the log, skipping")
            continue
        cluster_obj = ABSTRACTIONS_OBJECTS[col_name]
        cluster_obj.set_abstraction(requested_abstraction)
        requested_cluster.append(cluster_obj)

    # Load the non-abstracted log from the temporary file created during upload
    df = load_event_log_from_tempfile(f"{FILEPATH}/persistent_log.xes")
    logger.debug("Loaded persistent log ")
    logger.debug(len(df))
    logger.debug(df.head())

    # apply abstractions
    try:
        df = process_log_for_d3js_abstractions(df, requested_cluster, requested_sp_zooms)
    except CycleDetectedException as e:
        return jsonify({
            "error": {
                "code": "CYCLE_DETECTED_IN_ABSTRACTION_DEPENDENCIES",
                "message": "A cycle was detected in the abstraction dependencies."
            }
        }), 400
    logger.info("Processed log for d3js with abstractions")
    max_zoom.export_max_zoom_df() # write the current max_zoom_df to the disk

    # export the abstracted log to a csv and a xes file
    df_copy =df.copy()
    if config.get("EXPORT_ABSTRACTED_LOG", False):
        try:
            export_event_log_custom(df_copy, f"{FILEPATH}/volatile_working_xes.xes")
        except Exception as e:
            logger.error(f"Error exporting event log: {e}")
            raise RuntimeError(f"Error exporting event log: {e}")


    # Check Privacy:
    xes_path = f"{FILEPATH}/max_zoom.xes"
    if config.get("ENFORCE_PRIVACY", False):
        logger.debug("Enforcing privacy on working XES")

        if config.get("DELETE_TRACES", False):
            logger.debug("Deleting traces to enforce privacy")
            #TODO will not work
            df = delete_trace2(df,f"{FILEPATH}/max_zoom.xes", f"{FILEPATH}/persistent_log.xes", config.get("K_TRACE", -1), config.get("K_EVENT", -1), config.get("K_EDGE", -1), config.get("L_DIV", 1), config.get("SINGLE_EVENT_L_DIV", False), config.get("FOlLOW_EVENT_L_DIV", False))
        else:
            logger.debug("Check Privacy without deleting")
            privacy_matched =  check_metrics(xes_path, config.get("K_TRACE", -1), config.get("K_EVENT", -1), config.get("K_EDGE", -1), config.get("L_DIV", -1), config.get("SINGLE_EVENT_L_DIV", False), config.get("FOlLOW_EVENT_L_DIV", False))
            if not privacy_matched:
                logger.info("Privacy Metrics not satisfied, don't return event-log to the FrontEnd")
                return jsonify({
                    "error": {
                        "code": "PRIVACY_REQUIREMENTS_NOT_SATISFIED",
                        "message": "Privacy requirements not satisfied"
                    }
                }), 400

    # Build the super nodes and super edges
    if config.get("DECOUPLE_TRACES", True):
        super_df = build_super_graph(df)
        data = super_df.to_dict(orient='records')
    else:
        data = df.to_dict(orient='records')
    return jsonify(data)

@bp.route("/api/available_abstractions")
def get_available_abstractions():
    ABSTRACTIONS_OBJECTS, COlUMN_ABSTRACTION_MAPPING = general_clusterer.get_abstractions() # build_abstractions
    logger.info(f"Available abstractions {COlUMN_ABSTRACTION_MAPPING}")
    abstraction_keys = {attr :  list(ABSTRACTIONS_OBJECTS[attr].abstractions.keys()) for attr in ABSTRACTIONS_OBJECTS.keys()}
    return jsonify(abstraction_keys)

@bp.route("/api/available_abstractions/<col_name>")
def get_available_abstractions_for_column(col_name):
    ABSTRACTIONS_OBJECTS, COlUMN_ABSTRACTION_MAPPING = general_clusterer.get_abstractions() # build_abstractions
    logger.info(f"Available abstractions {COlUMN_ABSTRACTION_MAPPING}")
    if (clusterer := ABSTRACTIONS_OBJECTS.get(col_name)) is not None:
        abstraction_keys = clusterer.abstractions.keys()
        logger.debug(abstraction_keys)
        return jsonify(list(abstraction_keys))
    else:
        logger.warning(f"No abstraction found for column: {col_name}")
        return jsonify([])


@bp.route("/api/attributes")
def get_available_attributes():
    with open(f"{FILEPATH}/attributes.json", mode='r') as fp:
        attributes = json.load(fp)
        return jsonify(attributes)

@bp.route("/api/attribute_types")
def get_attribute_types():
    return jsonify([attr_types for attr_types in attribute_extractor.ATTRIBUTE_TYPES])


@bp.route("/api/attribute_types", methods=['POST'])
def post_attribute_types():
    data = request.get_json()
    changing_attribute = data["attribute"]
    new_attribute_type = data["type"]
    logger.info(f"Changing attribute types for {changing_attribute} to {new_attribute_type}")
    attribute_extractor.update_attribute(changing_attribute, new_attribute_type)
    # initialize clusterer again, because clusterer may change for an attribute
    general_clusterer.reset_abstractions()
    df = load_event_log_from_tempfile(f"{FILEPATH}/persistent_log.xes")
    numerical_clusterer.build_abstractions(df)
    general_clusterer.get_abstractions()
    return jsonify({"success": "OK"})

@bp.route("/api/occurring_entries/<col_name>", methods=['GET'])
def get_occurring_entries_for_column(col_name):
    occurring_entries = get_occurring_entries(col_name)
    return jsonify(occurring_entries)
