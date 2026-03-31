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

import csv
import json
import shutil
import sys
import io
import os
import pandas as pd
import tempfile
from flask import Blueprint, render_template, request, jsonify
from pathlib import Path
import logging

from src.algo.super_graph import build_super_graph
# from src.analysis.attribute_extractor import AttributeExtractor
import src.analysis.attribute_extractor as attribute_extractor
from src.clustering import general_clusterer, numerical_clusterer
from src.clustering.specific_clusterer import EXCLUDING_FUNCTIONS
from src.utils.data_exporting import export_event_log, export_event_log_custom
from src.utils.data_importing import load_event_log_from_tempfile
from src.orchestrator import process_log_for_d3js, process_log_for_d3js_abstractions, process_log_for_d3js_exclusions

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


FILEPATH = project_root / 'data' / 'working_data'
# Import allowance fo file extensions
ALLOWED_EXTENSIONS = {'csv', 'xes'}
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@bp.route("/")
def home():
    return render_template("pages/index.html")

@bp.route('/api/get_data')
def get_data():
    data_path = project_root / 'data' / 'example_data' / 'data-runningexample.csv'
    with data_path.open(newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        data = list(reader)
    return jsonify(data)

@bp.route('/api/upload_data', methods=['POST'])
def upload_data():
    if 'file' not in request.files:
        return jsonify({'error': 'No file uploaded'}), 400

    file = request.files['file']
    filename = file.filename
    ext = filename.rsplit('.', 1)[1].lower()

    if filename == '':
        return jsonify({'error': 'No file selected'}), 400

    if not allowed_file(filename):
        return jsonify({'error': 'Invalid file type. Only {ALLOWED_EXTENSIONS} allowed.'}), 400

    try:
        if ext == 'csv':
            stream = io.StringIO(file.stream.read().decode("utf-8"), newline=None)
            reader = csv.DictReader(stream)
            data = list(reader)
        elif ext == 'xes':
            #file.save(f"{FILEPATH}/working_xes.xes")
            with tempfile.NamedTemporaryFile(delete=False, suffix=".xes") as tmp:
                file.save(tmp)
                tmp_path = tmp.name
            shutil.copy(tmp_path, f"{FILEPATH}/persistent_log.xes")
            # attribute_extractor = AttributeExtractor(tmp_path)
            general_clusterer.reset_abstractions()
            attribute_extractor.extract_attributes(tmp_path)
            attribute_extractor.extract_attribute_type_mapping()
            attribute_extractor.write_to_file()
            logger.info(f"Extracted trace attributes: {attribute_extractor.trace_attributes}")
            logger.info(f"Extracted event attributes: {attribute_extractor.event_attributes}")
            df = load_event_log_from_tempfile(f"{FILEPATH}/persistent_log.xes")
            numerical_clusterer.build_abstractions(df)
            general_clusterer.get_abstractions() # build_abstractions
            # Clean up temporary file
            os.remove(tmp_path)
        else:
            return jsonify({'error': 'Unsupported file type'}), 400
        return jsonify({'success': 'OK'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bp.route("/api/abstracted_data", methods=['POST'])
def get_abstracted_data():
    data = request.get_json()
    requested_abstractions = data.get("abstractions")
    logger.info(f"requested abstractions: {requested_abstractions}")
    # print(f"FLAT Abstractions loading from {general_clusterer.get_abstractions()}") # build_abstractions
    ABSTRACTION_FUNCTIONS, FLAT_ABSTRACTION_FUNCTIONS = general_clusterer.get_abstractions() # build_abstractions
    abstractions = [FLAT_ABSTRACTION_FUNCTIONS[abstraction] for abstraction in requested_abstractions if abstraction in FLAT_ABSTRACTION_FUNCTIONS.keys()]
    logger.info(f"abstractions: {abstractions}")
    requested_exclusions = data.get("exclusions")
    logger.info(f"requested exclusions: {requested_exclusions}")
    exclusions = [EXCLUDING_FUNCTIONS[exclusion] for exclusion in requested_exclusions if
                    exclusion in EXCLUDING_FUNCTIONS]

    # Load the non-abstracted log from the temporary file created during upload
    df = load_event_log_from_tempfile(f"{FILEPATH}/persistent_log.xes")
    logger.debug("Loaded persistent log ")
    logger.debug(len(df))
    logger.debug(df.head())
    if len(exclusions) > 0:
        logger.debug("exclusion branch")
        df = process_log_for_d3js_exclusions(df, exclusions)
    else:
        logger.debug(f"abstractions branch with {abstractions}")
        df = process_log_for_d3js_abstractions(df, abstractions)
    logger.info("Processed log for d3js with abstractions")
    df.head()
    # export the abstracted log to a csv and a xes file
    df_copy =df.copy()
    df_copy.to_csv(f"{FILEPATH}/volatile_working_csv.csv", index=False)
    try:
        export_event_log_custom(df_copy, f"{FILEPATH}/volatile_working_xes.xes")

        # Testing
        #attribute_extractor = AttributeExtractor(f"{FILEPATH}/volatile_working_xes.xes")
        """"
        attribute_extractor.extract_attributes(f"{FILEPATH}/volatile_working_xes.xes")
        attribute_extractor.extract_attribute_type_mapping()
        attribute_extractor.write_to_file()
        print(f"Extracted trace attributes testing: {attribute_extractor.trace_attributes}")
        print(f"Extracted event attributes testing: {attribute_extractor.event_attributes}")
        """
        general_clusterer.get_abstractions() # build_abstractions

    except Exception as e:
        logger.error(f"Error exporting event log: {e}")

    # Build the super nodes and super edges
    super_df = build_super_graph(df)
    data = super_df.to_dict(orient='records')
    return jsonify(data)

@bp.route("/api/available_abstractions")
def get_available_abstractions():
    ABSTRACTION_FUNCTIONS, FLAT_ABSTRACTION_FUNCTIONS = general_clusterer.get_abstractions() # build_abstractions
    logger.info(f"Available abstractions {ABSTRACTION_FUNCTIONS}")
    abstraction_keys = {attr : list(ABSTRACTION_FUNCTIONS[attr].keys()) for attr in ABSTRACTION_FUNCTIONS.keys()}
    return jsonify(abstraction_keys)

@bp.route("/api/available_exclusions")
def get_available_exclusions():
    return jsonify(list(EXCLUDING_FUNCTIONS.keys()))

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
    general_clusterer.reset_abstractions()
    df = load_event_log_from_tempfile(f"{FILEPATH}/persistent_log.xes")
    numerical_clusterer.build_abstractions(df)
    general_clusterer.get_abstractions()
    return jsonify({"success": "OK"})


