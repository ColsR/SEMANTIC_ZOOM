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
import shutil
import sys
import io
import os
import pandas as pd
import tempfile
from flask import Blueprint, render_template, request, jsonify
from pathlib import Path

from src.algo.super_graph import build_super_graph
from src.clustering.general_clusterer import ABSTRACTION_FUNCTIONS
from src.utils.data_exporting import export_event_log, export_event_log_custom
from src.utils.data_importing import load_event_log_from_tempfile
from src.orchestrator import process_log_for_d3js, process_log_for_d3js_abstractions

# App directory
project_root = Path(__file__).resolve().parent.parent
sys.path.append(str(project_root))

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
            shutil.copy(tmp_path, f"{FILEPATH}/working_xes.xes")
            df = load_event_log_from_tempfile(tmp_path)
            df = process_log_for_d3js(df)
            data = df.to_dict(orient='records')
            # Clean up temporary file
            os.remove(tmp_path)
        else:
            return jsonify({'error': 'Unsupported file type'}), 400
        return jsonify(data)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bp.route("/api/abstracted_data", methods=['POST'])
def get_abstracted_data():
    data = request.get_json()
    requested_abstractions = data["abstractions"]
    abstractions = [ABSTRACTION_FUNCTIONS[abstraction] for abstraction in requested_abstractions if abstraction in ABSTRACTION_FUNCTIONS]

    # Load the non-abstracted log from the temporary file created during upload
    df = load_event_log_from_tempfile(f"{FILEPATH}/working_xes.xes")

    df = process_log_for_d3js_abstractions(df, abstractions)

    # export the abstracted log to a csv and a xes file
    df_copy =df.copy()
    df_copy.to_csv(f"{FILEPATH}/volatile_working_csv.csv", index=False)
    try:
        export_event_log_custom(df_copy, f"{FILEPATH}/volatile_working_xes.xes")
    except Exception as e:
        print(f"Error exporting event log: {e}")

    # Build the super nodes and super edges
    super_df = build_super_graph(df)
    data = super_df.to_dict(orient='records')
    return jsonify(data)

@bp.route("/api/available_abstractions")
def get_available_abstractions():
    return jsonify(list(ABSTRACTION_FUNCTIONS.keys()))

