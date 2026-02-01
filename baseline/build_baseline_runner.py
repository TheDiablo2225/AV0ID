from preprocessing.stream_events import stream_cadets_events
from windowing.event_windows import sliding_event_windows
from graph.build_graph import build_provenance_graph
from graph.graph_metrics import extract_graph_metrics
from baseline.build_baseline import build_baseline

def generate_baseline(json_path, num_windows=50):
    events = stream_cadets_events(json_path)
    windows = sliding_event_windows(events)

    metrics_list = []

    for i in range(num_windows):
        window = next(windows)
        G = build_provenance_graph(window)
        metrics = extract_graph_metrics(G)
        metrics_list.append(metrics)
        print(f"Processed baseline window {i+1}/{num_windows}")

    baseline = build_baseline(metrics_list)
    return baseline


if __name__ == "__main__":
    baseline = generate_baseline(
        r"C:\AVOID\darpa\ta1-cadets-e3-official-1.json",
        num_windows=150
    )

    print("\nBaseline summary:")
    for k, v in baseline.items():
        if k != "edge_type_freq":
            print(k, v)
