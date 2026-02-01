import numpy as np
from collections import defaultdict

def build_baseline(metrics_list):
    baseline = {}

    # scalar metrics
    scalar_keys = [
        "avg_degree", "max_degree", "degree_std",
        "avg_fanout", "max_fanout",
        "density", "num_components"
    ]

    for key in scalar_keys:
        values = [m[key] for m in metrics_list]
        baseline[key] = {
            "mean": np.mean(values),
            "std": np.std(values),
            "min": np.min(values),
            "max": np.max(values)
        }

    # edge type frequencies
    edge_freqs = defaultdict(list)
    for m in metrics_list:
        for evt, freq in m["edge_type_freq"].items():
            edge_freqs[evt].append(freq)

    baseline["edge_type_freq"] = {
        evt: {
            "mean": np.mean(freqs),
            "std": np.std(freqs)
        }
        for evt, freqs in edge_freqs.items()
    }

    return baseline
