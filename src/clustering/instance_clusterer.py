def abstract_instance(event_attribute):
    return event_attribute

def abstract_instance_complete(event_attribute):
    return '*'

def get_all(col_name):
    return {
        f'misc{col_name}_abstracted' : (col_name, abstract_instance_complete),
        f'misc{col_name}_not_abstracted' : (col_name, abstract_instance),
    }