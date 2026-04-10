from src.clustering.abstract_abstraction import AbstractAbstraction
from src.clustering.abstract_clusterer import AbstractClusterer

class InstanceClusterer(AbstractClusterer):

    def __init__(self, col_name):
        super().__init__(col_name)
        self.set_abstraction(None)

    def build_abstractions(self, col_name):
        return {
            f'misc{col_name}_abstracted': InstanceAbstraction(col_name, col_name, abstract_instance_complete, 0),
            f'misc{col_name}_not_abstracted': InstanceAbstraction(col_name, col_name, abstract_instance, 100),
        }


    """
    def set_abstractions(self, abstraction_function):
        sel_func = self.abstractions.get(abstraction_function)  # TODO!
        if sel_func is None:
            self.abstraction_object = InstanceAbstraction(self.col_name, self.col_name, abstract_instance_complete, 0)
            return False
        else:
            self.abstraction_object = sel_func[1]
            return True
    """

class InstanceAbstraction(AbstractAbstraction):
    def __init__(self, source_col, target_col, abstraction_function, ranking=1):
        super().__init__(source_col, target_col, abstraction_function, ranking)


def abstract_instance(event_attribute):
    return event_attribute

def abstract_instance_complete(event_attribute):
    return '*'
