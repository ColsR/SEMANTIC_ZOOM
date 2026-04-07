from abc import ABC


class AbstractAbstraction(ABC):

    def __init__(self, source_col, target_col, abstraction_function):
        self.source_col = source_col
        self.target_col = target_col
        self.abstraction_function = abstraction_function

    def apply_abstraction(self, value):
        return self.abstraction_function(value)