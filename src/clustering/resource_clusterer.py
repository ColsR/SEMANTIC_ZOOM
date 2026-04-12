from src.clustering import instance_clusterer
from src.clustering.abstract_abstraction import AbstractAbstraction
from src.clustering.abstract_clusterer import AbstractClusterer


class ResourceClusterer(AbstractClusterer):

    def __init__(self, col_name):
        super().__init__(col_name)
        self.set_abstraction(None)

    def build_abstractions(self, col_name):
        return {
            'resource_abstracted': ResourceAbstraction(col_name, col_name, instance_clusterer.abstract_instance_complete, 0),
            'resource_not_abstracted': ResourceAbstraction(col_name, col_name, instance_clusterer.abstract_instance, 100)
        }


class ResourceAbstraction(AbstractAbstraction):
    def __init__(self, source_col, target_col, abstraction_function, ranking=1):
        super().__init__(source_col, target_col, abstraction_function, ranking)
