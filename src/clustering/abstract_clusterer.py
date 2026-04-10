from abc import ABC, abstractmethod


class AbstractClusterer(ABC):

    def __init__(self, col_name):
        self.col_name = col_name
        self.std_abstraction_object = None # selected default abstraction
        self.abstractions = self.build_abstractions(col_name)
        self.sp_abstraction_objects = [] # list with all specific zoom abstraction objects

    def set_mask(self, mask):
        self.std_abstraction_object.set_mask(mask)


    def check_columns(self, col_names):
        if self.std_abstraction_object.source_col not in col_names or self.std_abstraction_object.target_col not in col_names:
            return False
        return True

    def get_all(self):
        return self.abstractions

    """
    def apply_abstraction(self, value):
        # TODO die Logik wie in welcher Reihenfolge welche Abstraktionen ausgeführt werden ist egal
        raise NotImplementedError("The method apply_abstraction is not implemented in the clusterer, but should be implemented in the abstractions")
        # return self.abstraction_object.apply_abstraction(value)
    """

    def calculate_masks(self):
        # calculate the masks for all abstraction objects in this clusterer
        # the specific abstractions are ranked, so the abstraction object with the highest rank is applied and ot covered by a higher abstraction
        # if no specific abstraction is applied for an entry, the default abstraction (self.abstraction_object) is used by settig their mask True for this entry

        if len(self.sp_abstraction_objects) == 0:
            return
        self.sp_abstraction_objects.sort(key=lambda x: x.ranking)
        mask_len = len(self.std_abstraction_object.mask)
        for i in range(mask_len):
            set_mask = False
            for sp_abstraction in self.sp_abstraction_objects:
                if set_mask:
                    sp_abstraction.mask[i] = False
                elif sp_abstraction.mask[i]:
                    set_mask = True
            if set_mask:
                self.std_abstraction_object.mask[i] = False

    def add_specific_abstraction(self, abstraction):
        self.sp_abstraction_objects.append(abstraction)

    def reset_specific_abstractions(self):
        self.sp_abstraction_objects = []

    def set_abstraction(self, abstraction_function):
        sel_func = self.abstractions.get(abstraction_function)
        if sel_func is None:
            available_abstraction = list(self.abstractions.values())
            available_abstraction.sort(key=lambda x: x.ranking)
            self.std_abstraction_object = available_abstraction[0]
            return False
        else:
            self.std_abstraction_object = sel_func
            return True

    @abstractmethod
    def build_abstractions(self, col_name) -> dict:
        pass

