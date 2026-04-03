from abc import ABC, abstractmethod


class AbstractClusterer(ABC):


    def __init__(self, col_name):
        self.col_name = col_name
        self.abstraction_object = None
        self.abstractions = self.build_abstractions(col_name)
        self.mask = None

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

    @abstractmethod
    def build_abstractions(self, col_name) -> dict:
        pass

    @abstractmethod
    def set_abstractions(self, abstraction_function) -> bool:
        pass