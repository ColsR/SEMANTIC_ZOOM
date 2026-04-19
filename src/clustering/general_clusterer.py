import logging
from pathlib import Path

from src.analysis import attribute_extractor
from src.clustering import custom_clusterer
from src.clustering.activity_clusterer import ActivityClusterer
from src.clustering.custom_clusterer import CustomClusterer
from src.clustering.instance_clusterer import InstanceClusterer
from src.clustering.numerical_clusterer import NumericalClusterer
from src.clustering.relative_time_clusterer import RelativeTimeClusterer
from src.clustering.resource_clusterer import ResourceClusterer
from src.clustering.time_clusterer import TimeClusterer

logger = logging.getLogger(__name__)

ABSTRACTION_FUNCTIONS = None
FLAT_ABSTRACTION_FUNCTIONS = None
ABSTRACTION_OBJECTS = None # mapping column name to clusterer object
COLUMN_ABSTRACTION_MAPPING = None # mapping abstraction name to target column of this abstraction


def get_abstractions():
    global ABSTRACTION_FUNCTIONS, FLAT_ABSTRACTION_FUNCTIONS, ABSTRACTION_OBJECTS, COLUMN_ABSTRACTION_MAPPING

    if FLAT_ABSTRACTION_FUNCTIONS is None:
        ABSTRACTION_FUNCTIONS, FLAT_ABSTRACTION_FUNCTIONS, ABSTRACTION_OBJECTS, COLUMN_ABSTRACTION_MAPPING = build_abstractions()
    return ABSTRACTION_FUNCTIONS, FLAT_ABSTRACTION_FUNCTIONS, ABSTRACTION_OBJECTS, COLUMN_ABSTRACTION_MAPPING


def reset_abstractions():
    global ABSTRACTION_FUNCTIONS, FLAT_ABSTRACTION_FUNCTIONS, ABSTRACTION_OBJECTS, COLUMN_ABSTRACTION_MAPPING
    ABSTRACTION_FUNCTIONS = None
    FLAT_ABSTRACTION_FUNCTIONS = None
    ABSTRACTION_OBJECTS = None
    COLUMN_ABSTRACTION_MAPPING = None

def build_abstractions():
    abstraction_functions = {}
    abstraction_objects = {}
    attributes = attribute_extractor.event_attribute_type_mapping
    logger.info(f"attribute_mapping: {attributes}")
    custom_columns = set()

    # load custom abstractions
    project_root = Path(__file__).resolve().parent.parent.parent
    FILEPATH = project_root / 'data' / 'working_data'
    custom_abstractions = custom_clusterer.load_custom_abstractions(FILEPATH)
    for custom_abstraction in custom_abstractions:
        col_name = custom_abstraction["col_name"]
        abstraction_map = custom_abstraction["abstractions"]
        custom_cluster = CustomClusterer(col_name, abstraction_map)
        abstraction_functions[f"custom{col_name}"] = custom_cluster.get_all()
        abstraction_objects[col_name] = custom_cluster
        custom_columns.add(col_name)

    for col_name, attribute_type in attributes.items():
        if col_name not in custom_columns:
            match attribute_type:

                case attribute_extractor.ATTRIBUTE_TYPES.TIME:
                    time_cluster = TimeClusterer(col_name)
                    abstraction_functions[f"time{col_name}"] = time_cluster.get_all()
                    logger.debug({f"time{col_name}" : time_cluster.get_all()})
                    abstraction_objects[col_name] = time_cluster

                case attribute_extractor.ATTRIBUTE_TYPES.RELATIVE_TIME:
                    time_cluster = RelativeTimeClusterer(col_name)
                    abstraction_functions[f"relativetime{col_name}"] = time_cluster.get_all()
                    logger.debug({f"relativetime{col_name}": time_cluster.get_all()})
                    abstraction_objects[col_name] = time_cluster

                case attribute_extractor.ATTRIBUTE_TYPES.ACTIVITY:
                    activity_cluster = ActivityClusterer(col_name)
                    abstraction_functions[f"activity_{col_name}"] = activity_cluster.get_all()
                    logger.debug({f"activity{col_name}" : activity_cluster.get_all()})
                    abstraction_objects[col_name] = activity_cluster

                case attribute_extractor.ATTRIBUTE_TYPES.RESOURCE:
                    resource_cluster = ResourceClusterer(col_name)
                    abstraction_functions[f"resource{col_name}"] = resource_cluster.get_all()
                    logger.debug({f"resource{col_name}" : resource_cluster.get_all()})
                    abstraction_objects[col_name] = resource_cluster

                case attribute_extractor.ATTRIBUTE_TYPES.NUMERICAL:
                    numerical_cluster = NumericalClusterer(col_name)
                    abstraction_functions[f"numerical{col_name}"] = numerical_cluster.get_all()
                    logger.debug({f"numerical_{col_name}": numerical_cluster.get_all()})
                    abstraction_objects[col_name] = numerical_cluster

                case _:
                    instance_cluster = InstanceClusterer(col_name)
                    abstraction_functions[f"misc{col_name}"] = instance_cluster.get_all()
                    logger.debug("Not supported yet")
                    logger.debug({f"misc{col_name}" : instance_cluster.get_all()})
                    abstraction_objects[col_name] = instance_cluster

    # flat_abstractions als mapping key: (col, obj?)
    flat_abstraction_functions = {k: v for group in abstraction_functions.values() for k, v in group.items()}
    column_abstraction_mapping = {k: v.target_col for group in abstraction_functions.values() for k, v in group.items()}
    logger.debug(f"Flat: {flat_abstraction_functions}")
    return abstraction_functions, flat_abstraction_functions, abstraction_objects, column_abstraction_mapping
