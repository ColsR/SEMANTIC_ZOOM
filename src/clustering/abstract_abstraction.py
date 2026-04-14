from abc import ABC
from collections import defaultdict


class AbstractAbstraction(ABC):

    def __init__(self, source_col, target_col, abstraction_function, ranking=1):
        self.source_col = source_col
        self.target_col = target_col
        self.abstraction_function = abstraction_function
        self.ranking = ranking
        self.mask = None
        self.mask_source_col = None
        self.mask_filter_attribute = None
        self.l_div_map = defaultdict(set)

    def apply_abstraction(self, value):
        abstracted_value = self.abstraction_function(value)
        self.l_div_map[abstracted_value].add(value)
        return abstracted_value

    def set_mask(self, mask):
        self.mask =  mask

    def set_mask_source_column(self, mask_source_column):
        self.mask_source_col = mask_source_column

    def set_mask_filter_attribute(self, mask_filter_attribute):
        self.mask_filter_attribute = mask_filter_attribute

    def get_l_div_map(self):
        # list instead of set for json serialization, maybe put in serializer
        return {key : list(values) for key, values in self.l_div_map.items()}