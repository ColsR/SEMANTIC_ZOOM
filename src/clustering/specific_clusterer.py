from pathlib import Path

import pandas as pd
import pm4py

from src.clustering import time_clusterer

def build_mask(df, filter_source_column, filter_attribute):
    filter_func = lambda x : x == filter_attribute
    mask = df[filter_source_column].apply(filter_func)
    return mask.tolist()

