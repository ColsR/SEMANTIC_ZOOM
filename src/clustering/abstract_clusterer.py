import copy
from abc import ABC, abstractmethod

from src.clustering import specific_clusterer


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

    def apply_abstraction(self, df):
        # TODO die Logik wie in welcher Reihenfolge welche Abstraktionen ausgeführt werden ist egal
        # Masken neu berechnen, teilweise applien?
        # Abstractions ranken
        # Der Reihen nach Maske berechnen, setzen, applien, recalculate masks


        abstractions_to_apply = self.sp_abstraction_objects.copy()
        abstractions_to_apply.append(self.std_abstraction_object)
        """
        for abstraction_obj in abstractions_to_apply:
            df.loc[abstraction_obj.mask, abstraction_obj.target_col] = df.loc[abstraction_obj.mask, abstraction_obj.source_col].apply(lambda x: abstraction_obj.apply_abstraction(x))
        """

        abstractions_to_apply.sort(key=lambda x: x.ranking)
        df_unabstracted = copy.deepcopy(df)
        for abstraction_obj in abstractions_to_apply:
            if abstraction_obj.mask_filter_attribute is not None:
                sp_mask = specific_clusterer.build_mask(df, abstraction_obj.mask_source_col, abstraction_obj.mask_filter_attribute)
                abstraction_obj.set_mask(sp_mask)
            self.calculate_masks()
            df.loc[abstraction_obj.mask, abstraction_obj.target_col] = df_unabstracted.loc[abstraction_obj.mask, abstraction_obj.source_col].apply(lambda x: abstraction_obj.apply_abstraction(copy.deepcopy(x)))
        """
        for abstraction_obj in self.sp_abstraction_objects:
            df.loc[abstraction_obj.mask, abstraction_obj.target_col] = df.loc[abstraction_obj.mask, abstraction_obj.source_col].apply(lambda x: abstraction_obj.apply_abstraction(x))
        # default abstraction object
        df.loc[self.std_abstraction_object.mask, self.std_abstraction_object.target_col] = df.loc[self.std_abstraction_object.mask, self.std_abstraction_object.source_col].apply(lambda x: self.std_abstraction_object.apply_abstraction(x))
        """
        return df

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

    def get_l_div(self):
        colum_l_div_map = {}
        colum_l_div_map.update(self.std_abstraction_object.get_l_div_map())
        for sp_abstraction in self.sp_abstraction_objects:
            colum_l_div_map.update(sp_abstraction.get_l_div_map())
        return colum_l_div_map


    @abstractmethod
    def build_abstractions(self, col_name) -> dict:
        pass

