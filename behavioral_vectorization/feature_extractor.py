import math
from collections import Counter

def entropy(seq):
    counts = Counter(seq)
    total = len(seq)
    return -sum((c/total) * math.log2(c/total) for c in counts.values())

def extract_features(window):
    total = len(window)
    counts = Counter(window)

    return {
        "entropy": entropy(window),
        "unique_events": len(counts),
        "file_ratio": sum(v for k,v in counts.items() if "FILE" in k) / total,
        "network_ratio": sum(v for k,v in counts.items() if "NETWORK" in k) / total,
        "process_ratio": sum(v for k,v in counts.items() if "PROCESS" in k) / total
    }
