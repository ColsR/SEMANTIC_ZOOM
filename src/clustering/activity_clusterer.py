from src.clustering import instance_clusterer
from src.clustering.abstract_abstraction import AbstractAbstraction
from src.clustering.abstract_clusterer import AbstractClusterer


class ActivityClusterer(AbstractClusterer):

    def __init__(self, col_name, abstraction):
        super().__init__(col_name)
        self.set_abstractions(abstraction)

    def build_abstractions(self, col_name) -> dict:
        return {
            "activity_abstracted": (col_name, ActivityAbstraction(col_name, col_name, instance_clusterer.abstract_instance_complete)),
            "activity_bygroup": (col_name, ActivityAbstraction("org:group", col_name, instance_clusterer.abstract_instance)),
            "activity_not_abstracted": (col_name, ActivityAbstraction(col_name, col_name, instance_clusterer.abstract_instance)),
        }

    def set_abstractions(self, abstraction_function):
        sel_func = self.abstractions.get(abstraction_function)  # TODO!
        if sel_func is None:
            self.abstraction_object = ActivityAbstraction(self.col_name, self.col_name, instance_clusterer.abstract_instance_complete)
            return False
        else:
            self.abstraction_object = sel_func[1]
            return True


class ActivityAbstraction(AbstractAbstraction):
    def __init__(self, source_col, target_col, abstraction_function):
        super().__init__(source_col, target_col, abstraction_function)
