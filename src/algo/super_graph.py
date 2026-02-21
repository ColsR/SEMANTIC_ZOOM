import pandas
import pandas as pd
from bidict import bidict

def event_to_tuple(event: pandas.Series):
    return tuple(str(attribute) for attribute in event)

def build_super_graph(df: pandas.DataFrame):
    df.head()
    columns = df.columns.tolist()
    # check for all events if there is already an existing super event with the same event information otherwise create one
    # construct the edges between the edges -> via an own (technical) case
    super_nodes = bidict()
    super_edges = []
    super_node_index = 0
    for case in df["case"].unique().tolist():
        prev_cluster = None
        current_cluster = None
        end_event = True
        trace = df[df["case"] == case].iloc[::-1]
        for index, event in trace.iterrows():
            event_tuple = event_to_tuple(event.drop("case"))
            if event_tuple in super_nodes.values():
                current_cluster = super_nodes.inv[event_tuple]
            else:
                super_nodes.update({super_node_index: event_tuple})
                current_cluster = super_node_index
                super_node_index += 1
            if end_event:
                # for the last event of a trace we do not want to create an edge to a previous cluster, since there is no previous cluster
                end_event = False
            else:
                edge = (current_cluster, prev_cluster)
                if edge not in super_edges:
                    super_edges.append(edge)
            prev_cluster = current_cluster
    print(super_nodes)
    print(super_edges)

    # Build the pandas Dataframe
    columns.remove("case")
    rows = []
    case_id = 0

    for source, target in super_edges:
        for node in (source, target):
            event_tuple = super_nodes[node]
            row_dict = dict(zip(columns, event_tuple))
            row_dict["case"] = case_id
            rows.append(row_dict)

        case_id += 1

    super_dataframe = pd.DataFrame(rows, columns=["case"] + columns)
    return super_dataframe


