from src.clustering import instance_clusterer
from src.clustering.time_clusterer import get_all


def abstract_activity(activity):
    match activity:
        case 'register request': return 'register request'
        case 'examine casually': return 'examine'
        case 'examine thoroughly': return 'examine'
        case 'check ticket': return 'check'
        case 'check': return 'check'
        case 'decide': return 'decision enforcing'
        case 'reinitiate request': return 'decision enforcing'
        case 'reject request': return 'decision enforcing'
        case 'pay compensation': return 'pay compensation'
        case _:
            return activity


def abstract_activity2(activity):
    match activity:
        case 'register request': return 'checking'
        case 'examine casually': return 'checking'
        case 'examine thoroughly': return 'checking'
        case 'check ticket': return 'checking'
        case 'check': return 'checking'
        case 'decide': return 'decision'
        case 'reinitiate request': return 'decision'
        case 'reject request': return 'decision'
        case 'pay compensation': return 'decision'
        case _:
            return activity

def get_all(col_name):
    return {
        "activity_abstracted": (col_name, instance_clusterer.abstract_instance_complete),
        "activity_not_abstracted": (col_name, instance_clusterer.abstract_instance),
    }
