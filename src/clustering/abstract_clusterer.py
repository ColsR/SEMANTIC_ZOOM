from abc import ABC


class AbstractClusterer(ABC):


    def __init__(self, col_name):
        self.col_name = col_name
        self.abstraction_function = None
        self.mask = None

    def apply_abstraction(self, value):
        return self.abstraction_function(value)

    def set_mask(self, mask):
        self.mask = mask