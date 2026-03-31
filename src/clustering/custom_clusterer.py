import json
from pathlib import Path

from src.clustering import instance_clusterer
from src.clustering.abstract_clusterer import AbstractClusterer
from src.clustering.instance_clusterer import InstanceClusterer


class CustomClusterer(AbstractClusterer):

    def __init__(self, col_name, reverse_map):
        super().__init__(col_name)
        self.reverse_map = reverse_map

    def apply_abstraction(self, value):
        return self.reverse_map.get(value, "*")


def load_custom_abstractions(config_path):
    with open(f"{config_path}/custom_abstractions.json", mode='r') as fp:
        custom_abstractions = json.load(fp)
        return custom_abstractions
        for custom_abstraction in custom_abstractions:
            col_name = custom_abstraction["col_name"]
            abstractions = custom_abstraction["abstractions"]
            print(col_name)
            print(abstractions)
            # man muss die entsprechende

def get_all(_):
    project_root = Path(__file__).resolve().parent.parent.parent
    FILEPATH = project_root / 'data' / 'working_data'
    custom_clusterer = dict()

    custom_abstractions = load_custom_abstractions(FILEPATH)
    for custom_abstraction in custom_abstractions:
        col_name = custom_abstraction["col_name"]
        abstr = custom_abstraction["abstractions"]
        clusterer_entries = dict()
        clusterer_entries[f"custom{col_name}_abstracted"] = (col_name, InstanceClusterer(col_name, instance_clusterer.abstract_instance_complete))
        for level, mappings in abstr.items():
            # Reverse Mapping from abstracted_ value -> [specific attributes] to specific_attribute -> abstracted_value
            reverse_map = {
                raw: group
                for group, values in mappings.items()
                for raw in values
            }
            clusterer_entries[f"custom{col_name}_{level}"] = (col_name, CustomClusterer(col_name, reverse_map))

        clusterer_entries[f"custom{col_name}_not_abstracted"] = (col_name, InstanceClusterer(col_name, instance_clusterer.abstract_instance))
        custom_clusterer[col_name] = clusterer_entries
    return custom_clusterer


if __name__ == "__main__":
    all_clusterer = get_all(None)
    specific_clusterer = all_clusterer.get("concept:name").get("customconcept:name_level1")
    print(all_clusterer)
    result = specific_clusterer.apply_abstraction("reinitiate request")
    print(result)
