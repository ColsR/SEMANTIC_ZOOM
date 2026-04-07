from src.clustering.abstract_abstraction import AbstractAbstraction
from src.clustering.abstract_clusterer import AbstractClusterer

class InstanceClusterer(AbstractClusterer):

    def __init__(self, col_name, abstraction):
        super().__init__(col_name)
        self.set_abstractions(abstraction)

    def build_abstractions(self, col_name):
        return {
            f'misc{col_name}_abstracted': (col_name, InstanceAbstraction(col_name, col_name, abstract_instance_complete)),
            f'misc{col_name}_not_abstracted': (col_name, InstanceAbstraction(col_name, col_name, abstract_instance)),
        }

    def set_abstractions(self, abstraction_function):
        sel_func = self.abstractions.get(abstraction_function)  # TODO!
        if sel_func is None:
            self.abstraction_object = InstanceAbstraction(self.col_name, self.col_name, abstract_instance_complete)
            return False
        else:
            self.abstraction_object = sel_func[1]
            return True


class InstanceAbstraction(AbstractAbstraction):
    def __init__(self, source_col, target_col, abstraction_function):
        super().__init__(source_col, target_col, abstraction_function)


def abstract_instance(event_attribute):
    return event_attribute

def abstract_instance_complete(event_attribute):
    return '*'
