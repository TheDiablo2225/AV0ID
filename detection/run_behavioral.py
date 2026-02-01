from preprocessing.stream_events import stream_cadets_events
from windowing.event_windows import sliding_event_windows
from graph.build_graph import build_provenance_graph
from graph.graph_metrics import extract_graph_metrics
from baseline.build_baseline_runner import generate_baseline
from detection.anomaly_score import compute_anomaly_score
#from graph.visualize_graph import extract_high_risk_subgraph, visualize_graph
from graph.visualize_graph import extract_high_risk_subgraph, visualize_graph
from graph.visualize_pyvis import visualize_pyvis
import math
from collections import Counter

def ema(prev, current, alpha=0.3):
    if prev is None:
        return current
    return alpha * current + (1 - alpha) * prev


def entropy(seq):
    counts = Counter(seq)
    total = len(seq)
    return -sum((c/total) * math.log2(c/total) for c in counts.values())

def behavioral_vector(window):
    total = len(window)

    events = [e["event_type"] for e in window]
    cats   = [e.get("category", "other") for e in window]

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
        window = next(windows)
        vec = behavioral_vector(window)
        vectors.append(vec)

    baseline = {}
    for k in vectors[0]:
        values = [v[k] for v in vectors]
        baseline[k] = {
            "mean": sum(values) / len(values),
            "std": (sum((x - sum(values)/len(values))**2 for x in values) / len(values))**0.5 + 1e-6
        }

    return baseline

def behavioral_score(vector, baseline):
    score = 0.0
    for k, v in vector.items():
        mu = baseline[k]["mean"]
        std = baseline[k]["std"] + 1e-6
        score += abs(v - mu) / std
    return score


JSON_PATH = r"C:\AVOID\darpa\ta1-cadets-e3-official-1.json"



def main():

    ema_score = None
    consecutive_anomalies = 0

    EMA_THRESHOLD = 20          # tune later
    CONSECUTIVE_THRESHOLD = 3   # standard IDS practice

    print("Building baseline...")
    cfg_baseline = generate_baseline(JSON_PATH, num_windows=150)
    behavioral_baseline = generate_behavioral_baseline(JSON_PATH, num_windows=150)

    print("\n--- Detection Phase ---")

    events = stream_cadets_events(JSON_PATH)
    windows = sliding_event_windows(events)

    # Skip baseline windows
    for _ in range(150):
        next(windows)

    for i in range(5):  # test first 5 detection windows
        window = next(windows)
        G = build_provenance_graph(window)
        metrics = extract_graph_metrics(G)
        cfg_score, reasons = compute_anomaly_score(metrics, cfg_baseline)

        beh_vec = behavioral_vector(window)
        beh_score = behavioral_score(beh_vec, behavioral_baseline)

        print("Behavior Vector:")
        for k, v in beh_vec.items():
            print(f"  {k}: {v:.4f}")



        print(f"\nWindow {i+1}")
        print(f"CFG score: {cfg_score:.2f}")
        print(f"Behavioral score: {beh_score:.2f}")

        final_score = 0.6 * cfg_score + 0.4 * beh_score
        ema_score = ema(ema_score, final_score)

        print(f"Final score: {final_score:.2f}")
        print(f"EMA score: {ema_score:.2f}")

        if final_score > 3 * len(cfg_baseline):
            consecutive_anomalies += 1
        else:
            consecutive_anomalies = 0

        if ema_score > EMA_THRESHOLD or consecutive_anomalies >= CONSECUTIVE_THRESHOLD:
            print("⚠️  TEMPORALLY CONFIRMED ANOMALY")
            print(f"Consecutive anomalies: {consecutive_anomalies}")

            visualize_pyvis(G, output_file=f"anomaly_window_{i+1}.html")
            break
        else:
            print("✅ Normal behavior (temporally stable)")

              # Visualize anomalous behavior
              # H = extract_high_risk_subgraph(G)
              #  visualize_graph(H, title=f"Anomalous Window {i+1}")

              # break  # visualize only first anomaly


if __name__ == "__main__":
    main()
