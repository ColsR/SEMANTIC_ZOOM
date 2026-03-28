from src.clustering import instance_clusterer
from src.clustering.abstract_clusterer import AbstractClusterer


def abstract_resource_complete(resource):
    return '*'


class ResourceClusterer(AbstractClusterer):

    def __init__(self, col_name, abstraction):
        super().__init__(col_name)
        self.abstraction_function = abstraction

def get_all(col_name):
    return {
        'resource_abstracted' : (col_name, ResourceClusterer(col_name, instance_clusterer.abstract_instance_complete)),
        'resource_not_abstracted' : (col_name, ResourceClusterer( col_name, instance_clusterer.abstract_instance))
    }