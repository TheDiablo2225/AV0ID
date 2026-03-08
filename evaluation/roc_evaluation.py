import numpy as np
import matplotlib.pyplot as plt
from sklearn.metrics import roc_curve, auc

from preprocessing.stream_events import stream_cadets_events
from windowing.event_windows import sliding_event_windows
from graph.build_graph import build_provenance_graph
from graph.graph_metrics import extract_graph_metrics
from detection.anomaly_score import compute_anomaly_score

from elve.event_normalizer import normalize
from elve.runtime_automaton import RuntimeAutomaton
from elve.elve_engine import ELVEEngine

from evaluation.attack_injection import inject_exploit


# =====================================================
# Behavioral logic (copied here to avoid circular import)
# =====================================================

from collections import Counter
import math


def entropy(seq):
    counts = Counter(seq)
    total = len(seq)
    return -sum((c/total) * math.log2(c/total) for c in counts.values())


def behavioral_vector(window):

    total = len(window)

    events = [e["event_type"] for e in window]
    cats = [e.get("category", "other") for e in window]

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


def behavioral_score(vector, baseline):

    score = 0.0

    for k, v in vector.items():
        mu = baseline[k]["mean"]
        std = baseline[k]["std"]
        score += abs(v - mu) / std

    return score


# =====================================================
# Evaluation
# =====================================================

def evaluate_system(json_path,
                    cfg_baseline,
                    beh_baseline,
                    elve_baseline,
                    fuse_function,
                    ranges):

    events = stream_cadets_events(json_path)
    windows = sliding_event_windows(events)

    # Skip training windows
    for _ in range(150):
        next(windows)

    elve_runtime = RuntimeAutomaton(elve_baseline)
    elve_engine = ELVEEngine(elve_runtime)

    scores = []
    labels = []

    for i in range(200):

        window = next(windows)

        # CFG
        G = build_provenance_graph(window)
        metrics = extract_graph_metrics(G)
        cfg_score, _ = compute_anomaly_score(metrics, cfg_baseline)

        # Behavioral
        beh_vec = behavioral_vector(window)
        beh_score = behavioral_score(beh_vec, beh_baseline)

       
        # Inject attack into the window itself
        if i % 2 == 0:
            window = inject_exploit(window)
            label = 1
        else:
            label = 0

        # Now compute ELVE sequence
        sequence = [normalize(e["event_type"]) for e in window]
        # ELVE
        elve_score, _, _ = elve_engine.process_window(sequence)

        # Fusion
        fused_score = fuse_function(
            cfg_score,
            beh_score,
            elve_score,
            ranges
        )

        scores.append(fused_score)
        labels.append(label)

    scores = np.array(scores)
    labels = np.array(labels)

    print("Normal mean score:", np.mean(scores[labels == 0]))
    print("Attack mean score:", np.mean(scores[labels == 1]))

    return scores, labels


# =====================================================
# ROC
# =====================================================

def plot_roc(scores, labels):

    fpr, tpr, thresholds = roc_curve(labels, scores)
    roc_auc = auc(fpr, tpr)

    plt.figure()
    plt.plot(fpr, tpr, label=f"AUC = {roc_auc:.3f}")
    plt.plot([0, 1], [0, 1], linestyle="--")

    plt.xlabel("False Positive Rate")
    plt.ylabel("True Positive Rate")
    plt.title("ROC Curve - AV0ID (CFG + Behavioral + ELVE)")
    plt.legend()
    plt.show()

    return roc_auc