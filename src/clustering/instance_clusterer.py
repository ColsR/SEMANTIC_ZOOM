from src.clustering.abstract_clusterer import AbstractClusterer


def abstract_instance(event_attribute):
    return event_attribute

def abstract_instance_complete(event_attribute):
    return '*'


class InstanceClusterer(AbstractClusterer):

    def __init__(self, col_name, abstraction):
        super().__init__(col_name)
        self.abstraction_function = abstraction


def get_all(col_name):
    return {
        f'misc{col_name}_abstracted' : (col_name, InstanceClusterer(col_name, abstract_instance_complete)),
        f'misc{col_name}_not_abstracted' : (col_name, InstanceClusterer(col_name, abstract_instance)),
    }