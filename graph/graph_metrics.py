import numpy as np
import networkx as nx
from collections import Counter

def extract_graph_metrics(G):
    metrics = {}

    # Degree statistics
    degrees = [deg for _, deg in G.degree()]
    metrics["avg_degree"] = np.mean(degrees)
    metrics["max_degree"] = np.max(degrees)
    metrics["degree_std"] = np.std(degrees)

    # Fan-out (out-degree = how aggressively a process acts)
    out_degrees = [deg for _, deg in G.out_degree()]
    metrics["avg_fanout"] = np.mean(out_degrees)
    metrics["max_fanout"] = np.max(out_degrees)

    # Edge type distribution
    edge_types = [
        data["event_type"]
        for _, _, data in G.edges(data=True)
    ]
    edge_type_counts = Counter(edge_types)
    total_edges = sum(edge_type_counts.values())

    metrics["edge_type_freq"] = {
        k: v / total_edges for k, v in edge_type_counts.items()
    }

    # Graph density (how connected execution is)
    # metrics["density"] = nx.density(G)
    simple_G = nx.DiGraph(G)
    metrics["density"] = nx.density(simple_G)


    # Connected components (structure fragmentation)
    metrics["num_components"] = nx.number_weakly_connected_components(G)

    return metrics
