import networkx as nx

def build_provenance_graph(event_window):
    """
    Build a provenance graph from a list of CADETS events.
    """
    G = nx.MultiDiGraph()

    for event in event_window:
        subj = event["subject"]
        obj = event["object"]
        evt = event["event_type"]
        ts = event["time"]

        if subj is None or obj is None:
            continue

        # Add nodes
        G.add_node(subj)
        G.add_node(obj)

        # Add directed edge with attributes
        G.add_edge(
            subj,
            obj,
            event_type=evt,
            timestamp=ts
        )

    return G
