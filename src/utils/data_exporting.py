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

# Load and preprocess event data
# app/backend/data_loader.py
import pandas as pd
import pm4py
from pathlib import Path

def export_event_log(df, filename: str, foldername="processed_event_data") -> pd.DataFrame:
    """Exports a DataFrame to an XES file in the specified folder."""
    if filename.endswith(".xes"):
        data_path = Path(__file__).parent.parent.parent / "data" / foldername / filename
        pm4py.write_xes(df, data_path)
    else:
        raise ValueError("'Filename' must be an .xes file and\n\
                         be in the folder 'data/processed_event_data'.")
    return print("export complete.")

def export_event_log_custom(df, file_path):

    """Exports a DataFrame to an specified XES file"""
    if file_path.endswith(".xes"):
        df["timestamps"] = pd.to_datetime(df["timestamps"])
        # TODO remove this probably later because these columns will not be present anymore
        df.drop(columns=["time:timestamp:casestart", "time:timestamp:relative", "timestamp_relative_seconds", "time:relative:seconds:log", "ranks", "activity"], inplace=True, errors="ignore")
        #df.rename(columns={"timestamps": "time:timestamp"}, inplace=True)
        df = df.rename(columns={"timestamps": "time:timestamp"})
        print("Exporting event log...")
        print(df)
        log = pm4py.convert_to_event_log(
            df,
            case_id_key="case",
            activity_key="concept:name",
            timestamp_key="time:timestamp"
        )
        pm4py.write_xes(log, file_path)
    else:
        raise ValueError("'Filename' must be an .xes file and\n\
                         be in the folder 'data/processed_event_data'.")
    return print("export complete.")