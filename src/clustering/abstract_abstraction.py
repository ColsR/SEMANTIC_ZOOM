from abc import ABC


class AbstractAbstraction(ABC):

    def __init__(self, source_col, target_col, abstraction_function, ranking=1):
        self.source_col = source_col
        self.target_col = target_col
        self.abstraction_function = abstraction_function
        self.ranking = ranking
        self.mask = None

    def apply_abstraction(self, value):
        return self.abstraction_function(value)

    def set_mask(self, mask):
        self.mask =  mask