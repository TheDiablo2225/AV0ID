import math
from collections import Counter

def entropy(seq):
    counts = Counter(seq)
    total = len(seq)
    return -sum((c/total) * math.log2(c/total) for c in counts.values())

def behavioral_vector(window):
    total = len(window)

    events = [e["event_type"] for e in window]
    cats   = [e["category"] for e in window]

    evt_counts = Counter(events)
    cat_counts = Counter(cats)

    return {
        "entropy": entropy(events),
        "unique_ratio": len(evt_counts) / total,
        "file_ratio": cat_counts.get("file", 0) / total,
        "network_ratio": cat_counts.get("network", 0) / total,
        "memory_ratio": cat_counts.get("memory", 0) / total,
        "process_rate": evt_counts.get("fork", 0) / total,
        "privilege_rate": evt_counts.get("setuid", 0) / total,
        "burstiness": max(evt_counts.values()) / total
    }
