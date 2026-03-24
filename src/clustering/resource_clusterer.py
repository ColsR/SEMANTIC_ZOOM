from src.clustering import instance_clusterer


def abstract_resource_complete(resource):
    return '*'


def get_all(col_name):
    return {
        'resource_abstracted' : (col_name, instance_clusterer.abstract_instance_complete),
        'resource_not_abstracted' : (col_name, instance_clusterer.abstract_instance)
    }