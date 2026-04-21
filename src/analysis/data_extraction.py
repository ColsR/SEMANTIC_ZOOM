import logging
from pathlib import Path

from src.analysis.privacy.k_anonymity import load_event_log

logger = logging.getLogger(__name__)

project_root = Path(__file__).parent.parent.parent

def get_occurring_entries(col_name):
    occurring_entries = set()
    file_path = project_root / 'data' / 'working_data' / 'volatile_working_xes.xes'
    log = load_event_log(str(file_path))
    for trace in log:
        for event in trace:
            if (entry := event.get(col_name)) is not None:
                occurring_entries.add(entry)
    logger.info(f"Occurring entries for column {col_name}: {occurring_entries}")
    return list(occurring_entries)

if __name__ == '__main__':
    print(get_occurring_entries("concept:name"))