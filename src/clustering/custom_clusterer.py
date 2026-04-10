import json
from pathlib import Path

from src.clustering import instance_clusterer
from src.clustering.abstract_abstraction import AbstractAbstraction
from src.clustering.abstract_clusterer import AbstractClusterer
from src.clustering.instance_clusterer import InstanceClusterer, InstanceAbstraction


class CustomClusterer(AbstractClusterer):

    def __init__(self, col_name, reverse_map):
        self.reverse_map = reverse_map
        super().__init__(col_name)
        self.set_abstraction(None)

    def build_abstractions(self, col_name):
        clusterer_entries = dict()
        clusterer_entries[f"custom{col_name}_abstracted"] = (col_name, InstanceAbstraction(self.col_name, self.col_name, instance_clusterer.abstract_instance_complete, 0))
        for level, mappings in self.reverse_map.items():
            # Reverse Mapping from abstracted_ value -> [specific attributes] to specific_attribute -> abstracted_value
            reverse_map = {
                raw: group
                for group, values in mappings.items()
                for raw in values
            }
            clusterer_entries[f"custom{col_name}_{level}"] = (col_name, CustomAbstraction(col_name, col_name, reverse_map))

        clusterer_entries[f"custom{col_name}_not_abstracted"] = (col_name, InstanceAbstraction(col_name, col_name, instance_clusterer.abstract_instance, 100))
        return clusterer_entries

    """
    def set_abstractions(self, abstraction_function):
        sel_func = self.abstractions.get(abstraction_function)
        if sel_func is None:
            self.abstraction_object = InstanceAbstraction(self.col_name, self.col_name, instance_clusterer.abstract_instance_complete, 0)
            return False
        else:
            self.abstraction_object = sel_func[1]
            return True
    """

class CustomAbstraction(AbstractAbstraction):
    def __init__(self, source_col, target_col, abstraction_map, ranking=1):
        super().__init__(source_col, target_col, None, ranking)
        self.abstraction_map = abstraction_map

    def apply_abstraction(self, value):
        return self.abstraction_map.get(value, "*")

# UTILS
def load_custom_abstractions(config_path):
    with open(f"{config_path}/custom_abstractions.json", mode='r') as fp:
        custom_abstractions = json.load(fp)
        return custom_abstractions
