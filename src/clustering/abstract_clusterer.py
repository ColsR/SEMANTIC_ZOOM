from abc import ABC, abstractmethod


class AbstractClusterer(ABC):

    def __init__(self, col_name):
        self.col_name = col_name
        self.abstraction_object = None # selected default abstraction
        self.abstractions = self.build_abstractions(col_name)
        self.mask = None
        self.abstraction_objects = [] # list with all setted abstraction obejcts (probably include the default) with their mask

    def set_mask(self, mask):
        self.mask = mask

    def check_columns(self, col_names):
        """
        for key, value in self.abstractions.items():
            abstraction = value[1]
        """
        if self.abstraction_object.source_col not in col_names or self.abstraction_object.target_col not in col_names:
            return False
        return True

    def get_all(self):
        return self.abstractions

    def apply_abstraction(self, value):
        # TODO die Logik wie in welcher Reihenfolge welche Abstraktionen ausgeführt werden
        return self.abstraction_object.apply_abstraction(value)

    def calculate_masks(self):
        #TODO
        raise NotImplementedError

    def set_abstraction(self, abstraction_function):
        sel_func = self.abstractions.get(abstraction_function)  # TODO!
        if sel_func is None:
            available_abstraction = list(self.abstractions.values())
            available_abstraction.sort(key=lambda x: x[1].ranking)
            self.abstraction_object = available_abstraction[0][1]
            return False
        else:
            self.abstraction_object = sel_func[1]
            return True

    @abstractmethod
    def build_abstractions(self, col_name) -> dict:
        pass

