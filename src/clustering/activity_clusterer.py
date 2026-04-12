from src.clustering import instance_clusterer
from src.clustering.abstract_abstraction import AbstractAbstraction
from src.clustering.abstract_clusterer import AbstractClusterer


class ActivityClusterer(AbstractClusterer):

    def __init__(self, col_name):
        super().__init__(col_name)
        self.set_abstraction(None)

    def build_abstractions(self, col_name) -> dict:
        return {
            "activity_abstracted": ActivityAbstraction(col_name, col_name, instance_clusterer.abstract_instance_complete, 0),
            "activity_bygroup": ActivityAbstraction("org:group", col_name, instance_clusterer.abstract_instance, 1),
            "activity_not_abstracted": ActivityAbstraction(col_name, col_name, instance_clusterer.abstract_instance, 100),
        }


class ActivityAbstraction(AbstractAbstraction):
    def __init__(self, source_col, target_col, abstraction_function, ranking=1):
        super().__init__(source_col, target_col, abstraction_function, ranking)
