from preprocessing.stream_events import stream_cadets_events
from windowing.event_windows import sliding_event_windows
from graph.build_graph import build_provenance_graph
from graph.graph_metrics import extract_graph_metrics
from baseline.build_baseline_runner import generate_baseline
from detection.anomaly_score import compute_anomaly_score
from graph.visualize_pyvis import visualize_pyvis

from elve.event_normalizer import normalize
from elve.automaton_builder import AutomatonBuilder
from elve.runtime_automaton import RuntimeAutomaton
from elve.elve_engine import ELVEEngine

from evaluation.roc_evaluation import evaluate_system, plot_roc
from fusion.risk_fusion import fuse_scores

import math
import numpy as np
from collections import Counter, defaultdict


# =====================================================
# Utility
# =====================================================

def ema(prev, current, alpha=0.3):
    if prev is None:
        return current
    return alpha * current + (1 - alpha) * prev


def compute_adaptive_threshold(scores, percentile=97):
    return np.percentile(scores, percentile)


def entropy(seq):
    counts = Counter(seq)
    total = len(seq)
    return -sum((c/total) * math.log2(c/total) for c in counts.values())


# =====================================================
# Behavioral Module
# =====================================================

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


def generate_behavioral_baseline(json_path, num_windows=150):

    events = stream_cadets_events(json_path)
    windows = sliding_event_windows(events)

    vectors = []

    for _ in range(num_windows):
        vectors.append(behavioral_vector(next(windows)))

    baseline = {}

    for k in vectors[0]:
        values = [v[k] for v in vectors]
        mean = sum(values) / len(values)

        std = (
            sum((x - mean) ** 2 for x in values) / len(values)
        ) ** 0.5 + 1e-6

        baseline[k] = {"mean": mean, "std": std}

    return baseline


def behavioral_score(vector, baseline):

    score = 0.0

    for k, v in vector.items():

        mu = baseline[k]["mean"]
        std = baseline[k]["std"]

        score += abs(v - mu) / std

    return score


# =====================================================
# ELVE Baseline
# =====================================================

def generate_elve_baseline(json_path, num_windows=150):

    events = stream_cadets_events(json_path)
    windows = sliding_event_windows(events)

    builder = AutomatonBuilder()

    for _ in range(num_windows):

        window = next(windows)

        seq = [normalize(e["event_type"]) for e in window]

        builder.observe_sequence(seq)

    return builder.build(min_support=2)


# =====================================================
# Weight Optimization
# =====================================================

def optimize_weights(cfg_vals, beh_vals, elve_vals):

    cfg_var = np.var(cfg_vals)
    beh_var = np.var(beh_vals)
    elve_var = np.var(elve_vals)

    total = cfg_var + beh_var + elve_var + 1e-6

    w_cfg = 1 - (cfg_var / total)
    w_beh = 1 - (beh_var / total)
    w_elve = 1 - (elve_var / total)

    s = w_cfg + w_beh + w_elve

    return w_cfg/s, w_beh/s, w_elve/s


# =====================================================
# Correlation Boost
# =====================================================

def correlation_boost(cfg_norm, beh_norm, elve_norm):

    if cfg_norm > 0.7 and elve_norm > 0.6:
        return 0.15

    if elve_norm > 0.7 and beh_norm > 0.6:
        return 0.10

    return 0.0


# =====================================================
# MAIN
# =====================================================

JSON_PATH = r"C:\AVOID\darpa\ta1-cadets-e3-official-1.json"


def main():

    print("Building baselines...")

    cfg_baseline = generate_baseline(JSON_PATH, num_windows=150)

    beh_baseline = generate_behavioral_baseline(JSON_PATH, num_windows=150)

    elve_baseline = generate_elve_baseline(JSON_PATH, num_windows=150)

    elve_runtime = RuntimeAutomaton(elve_baseline)
    elve_engine = ELVEEngine(elve_runtime)

    print("Calibrating weights & thresholds...")

    events = stream_cadets_events(JSON_PATH)
    windows = sliding_event_windows(events)

    for _ in range(150):
        next(windows)

    cfg_vals, beh_vals, elve_vals = [], [], []

    fused_scores = []

    for _ in range(100):

        window = next(windows)

        G = build_provenance_graph(window)
        metrics = extract_graph_metrics(G)

        cfg_score, _ = compute_anomaly_score(metrics, cfg_baseline)

        beh_vec = behavioral_vector(window)
        beh_score = behavioral_score(beh_vec, beh_baseline)

        pid_groups = defaultdict(list)

        for e in window:

            pid = e.get("pid", "unknown")

            pid_groups[pid].append(normalize(e["event_type"]))

        pid_scores = []

        for pid, seq in pid_groups.items():

            if len(seq) >= 2:

                score, _, _ = elve_engine.process_window(seq)

                pid_scores.append(score)

        elve_score = max(pid_scores) if pid_scores else 0

        cfg_vals.append(cfg_score)
        beh_vals.append(beh_score)
        elve_vals.append(elve_score)

    w_cfg, w_beh, w_elve = optimize_weights(cfg_vals, beh_vals, elve_vals)

    cfg_max = max(cfg_vals)
    beh_max = max(beh_vals)
    elve_max = max(elve_vals)

    ranges = {
    "cfg_max": cfg_max,
    "beh_max": beh_max,
    "elve_max": elve_max    
    }

    for i in range(len(cfg_vals)):

        cfg_norm = cfg_vals[i] / (cfg_max + 1e-6)
        beh_norm = beh_vals[i] / (beh_max + 1e-6)
        elve_norm = elve_vals[i] / (elve_max + 1e-6)

        fused = (
            w_cfg * cfg_norm +
            w_beh * beh_norm +
            w_elve * elve_norm +
            correlation_boost(cfg_norm, beh_norm, elve_norm)
        )

        fused_scores.append(fused)

    FUSION_THRESHOLD = compute_adaptive_threshold(fused_scores, 97)

    print(f"Optimized Weights → CFG:{w_cfg:.2f}, BEH:{w_beh:.2f}, ELVE:{w_elve:.2f}")
    print(f"Adaptive Threshold: {FUSION_THRESHOLD:.3f}")

    # =====================================================
    # ROC Evaluation (RUN ONCE)
    # =====================================================

    print("\nRunning ROC evaluation...")

    scores, labels = evaluate_system(
        JSON_PATH,
        cfg_baseline,
        beh_baseline,
        elve_baseline,
        fuse_scores,
        ranges
    )

    auc_value = plot_roc(scores, labels)

    print("AUC:", auc_value)

    # =====================================================
    # Detection Phase
    # =====================================================

    print("\n--- Detection Phase ---")

    ema_score = None
    consecutive_anomalies = 0

    CONSECUTIVE_THRESHOLD = 3

    events = stream_cadets_events(JSON_PATH)
    windows = sliding_event_windows(events)

    for _ in range(150):
        next(windows)

    for i in range(10):

        window = next(windows)

        G = build_provenance_graph(window)
        metrics = extract_graph_metrics(G)

        cfg_score, _ = compute_anomaly_score(metrics, cfg_baseline)

        beh_vec = behavioral_vector(window)
        beh_score = behavioral_score(beh_vec, beh_baseline)

        pid_groups = defaultdict(list)

        for e in window:

            pid = e.get("pid", "unknown")

            pid_groups[pid].append(normalize(e["event_type"]))

        pid_scores = []

        for pid, seq in pid_groups.items():

            if len(seq) >= 2:

                score, _, _ = elve_engine.process_window(seq)

                pid_scores.append(score)

        elve_score = max(pid_scores) if pid_scores else 0

        cfg_norm = cfg_score / (cfg_max + 1e-6)
        beh_norm = beh_score / (beh_max + 1e-6)
        elve_norm = elve_score / (elve_max + 1e-6)

        fused = (
            w_cfg * cfg_norm +
            w_beh * beh_norm +
            w_elve * elve_norm +
            correlation_boost(cfg_norm, beh_norm, elve_norm)
        )

        ema_score = ema(ema_score, fused)

        print(f"\nWindow {150+i+1}")
        print(f"CFG:{cfg_score:.2f} BEH:{beh_score:.2f} ELVE:{elve_score:.3f}")
        print(f"Fused:{fused:.3f} EMA:{ema_score:.3f}")

        if ema_score > FUSION_THRESHOLD:
            consecutive_anomalies += 1
        else:
            consecutive_anomalies = 0

        if ema_score > FUSION_THRESHOLD or consecutive_anomalies >= CONSECUTIVE_THRESHOLD:

            print("\n⚠️ ZERO-DAY ANOMALY DETECTED")

            visualize_pyvis(G, output_file=f"anomaly_window_{i+1}.html")

            break

        else:

            print("Normal behavior")


if __name__ == "__main__":
    main()