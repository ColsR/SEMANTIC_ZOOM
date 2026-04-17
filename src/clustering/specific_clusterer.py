import copy
import logging
from collections import defaultdict

import matplotlib.pyplot as plt
import networkx as nx
import pandas as pd

logger = logging.getLogger(__name__)

def build_mask(df, filter_source_column, filter_attribute):
    filter_func = lambda x : str(x) == filter_attribute
    if isinstance(df[filter_source_column][0], pd.Timestamp):
        filter_value = pd.to_datetime(filter_attribute, utc=True)
        df_copy = copy.deepcopy(df)
        mask = pd.to_datetime(df_copy[filter_source_column], utc=True) == filter_value
        return mask.tolist()
    mask = df[filter_source_column].apply(filter_func)
    return mask.tolist()


def build_dependency_graph(abstractions):
    G = nx.DiGraph()
    all_abstractions = []
    cluster_requested = defaultdict(list)
    for clusterer in abstractions:
        default_source = clusterer.std_abstraction_object.source_col
        default_target = clusterer.std_abstraction_object.target_col
        G.add_node(clusterer.std_abstraction_object)
        all_abstractions.append((clusterer.std_abstraction_object, default_source, default_target))
        cluster_requested[clusterer].append(clusterer.std_abstraction_object)
        for sp_abstraction in clusterer.sp_abstraction_objects:
            sp_source = sp_abstraction.mask_source_col
            if sp_source is None:
                logger.error("Specific abstraction does not have a mask source column, cannot add edge to graph")
                continue
            sp_target = sp_abstraction.target_col
            all_abstractions.append((sp_abstraction, sp_source, sp_target))
            G.add_node(sp_abstraction)
            cluster_requested[clusterer].append(sp_abstraction)
    for abstraction in all_abstractions:
        for other_abstraction in all_abstractions:
            if abstraction == other_abstraction:
                continue
            abstraction_obj,abstraction_source, abstraction_target = abstraction
            other_obj, other_source, other_target = other_abstraction
            if abstraction_target == other_source:
                G.add_edge(abstraction_obj, other_obj)


    pos = nx.spring_layout(G)

    nx.draw(
        G,
        pos,
        with_labels=True,
        node_color="lightblue",
        node_size=2000,
        font_size=10,
        arrows=True
    )

    plt.show()

    if not nx.is_directed_acyclic_graph(G):
        logger.warning("The graph is not directed acyclic")
    layers = get_execution_layers(G)
    order = [item for sublist in layers for item in sublist]

    cluster_order = []
    temp_clusters = defaultdict(list) # für jedes Cluster speichern welche seiner Abstraktionen schon besucht wurde
    for abs in order:
        keys_to_remove =[]
        for key, value in cluster_requested.items():
            if not value:
                cluster_order.append({key : temp_clusters[key]})
                keys_to_remove.append(key)
            if abs in value:
                value.remove(abs)
                temp_clusters[key].append(abs)
                if not value:
                    cluster_order.append({key: temp_clusters[key]})
                    keys_to_remove.append(key)
        for key in keys_to_remove:
            del cluster_requested[key]
    print(cluster_order)
    return cluster_order




def get_execution_layers(G):
    layers = []
    G = G.copy()

    while G.nodes:
        # alle ohne eingehende Kanten
        ready = [n for n in G.nodes if G.in_degree(n) == 0]

        if not ready:
            resolved = False
            # check for intra Cluster cycle
            cycles = list(nx.simple_cycles(G))
            for cycle in cycles:
               if is_intra_cluster_cycle(cycle):
                   logger.debug(f"Cycle detected but it is an intra cluster cycle: {cycle}")
                   layers.append(cycle)
                   G.remove_nodes_from(cycle)
                   resolved = True
                   break
            if not resolved:
                raise ValueError("Cycle detected")
            continue

        # back in std case
        layers.append(ready)
        G.remove_nodes_from(ready)

    return layers

def is_intra_cluster_cycle(cycle):
    cols = set()

    for node in cycle:
        cols.add(node.source_col)
        cols.add(node.target_col)

    return len(cols) == 1




# Für die Abstrkationen wird ein Abhängigkeitsgraph gebaut: wenn eine Abstrkation als Source-Column die Target-Cloumn einer anderen Abstrkaiton hat, besteht eine Abhägnigkeit
# Topologisches Sortieren erzeugt eine Reihenfolge der Abstraktionen -> Zyklen werden erkannt und eine Exception geworfen
# Anschließend wird über die geordnete Liste der abstrkationen gegangen und geschaut, wann ein Cluster-Obejkt all seine Abstraktionen ausgeführt werden kann
# Als Ergebis wird eine geordnete Liste mit Maps von Cluster-Objekten auf deren Abstrkaitonsobjekte ausgegeben
# Somit können dann pro Cluster-Objekt die Abstraktionen bzw. deren Masken aus den bereits abstrahierten Source-Masken-Spalten erstellt werden, die Masken im Cluster berechnet werden und die Abstraktion angewandt werden