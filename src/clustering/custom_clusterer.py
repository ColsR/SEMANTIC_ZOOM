import json

from src.clustering import instance_clusterer
from src.clustering.abstract_abstraction import AbstractAbstraction
from src.clustering.abstract_clusterer import AbstractClusterer
from src.clustering.instance_clusterer import InstanceAbstraction


class CustomClusterer(AbstractClusterer):

    def __init__(self, col_name, reverse_map):
        self.reverse_map = reverse_map
        super().__init__(col_name)
        self.set_abstraction(None)

    def build_abstractions(self, col_name):
        clusterer_entries = dict()
        clusterer_entries[f"{col_name}_abstracted"] = InstanceAbstraction(self.col_name, self.col_name, instance_clusterer.abstract_instance_complete, 0)
        for level, values in self.reverse_map.items():
            # Reverse Mapping from abstracted_ value -> [specific attributes] to specific_attribute -> abstracted_value
            ranking = values["ranking"]
            mappings = values["hierarchy"]
            reverse_map = {
                raw: group
                for group, values in mappings.items()
                for raw in values
            }
            clusterer_entries[f"{col_name}_{level}"] = CustomAbstraction(col_name, col_name, reverse_map, ranking)

        clusterer_entries[f"{col_name}_not_abstracted"] = InstanceAbstraction(col_name, col_name, instance_clusterer.abstract_instance, 100)
        return clusterer_entries


class CustomAbstraction(AbstractAbstraction):
    def __init__(self, source_col, target_col, abstraction_map, ranking=1):
        super().__init__(source_col, target_col, None, ranking)
        self.abstraction_map = abstraction_map

    def apply_abstraction(self, value):
        abstracted_value = self.abstraction_map.get(value, "*")
        self.l_div_map[abstracted_value].add(value)
        return abstracted_value

# UTILS
def load_custom_abstractions(config_path):
    with open(f"{config_path}/custom_abstractions.json", mode='r') as fp:
        custom_abstractions = json.load(fp)
        return custom_abstractions
