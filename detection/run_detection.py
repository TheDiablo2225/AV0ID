from preprocessing.stream_events import stream_cadets_events
from windowing.event_windows import sliding_event_windows
from graph.build_graph import build_provenance_graph
from graph.graph_metrics import extract_graph_metrics
from baseline.build_baseline_runner import generate_baseline
from detection.anomaly_score import compute_anomaly_score
#from graph.visualize_graph import extract_high_risk_subgraph, visualize_graph
from graph.visualize_graph import extract_high_risk_subgraph, visualize_graph
from graph.visualize_pyvis import visualize_pyvis



JSON_PATH = r"C:\AVOID\darpa\ta1-cadets-e3-official-1.json"



def main():
    print("Building baseline...")
    baseline = generate_baseline(JSON_PATH, num_windows=150)

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

        score, reasons = compute_anomaly_score(metrics, baseline)

        print(f"\nWindow {i+1}")
        print(f"Anomaly score: {score:.2f}")

        if score > 3 * len(baseline):
            print("⚠️  ANOMALY DETECTED")
            for r in reasons:
                print("  -", r)

              # Visualize anomalous behavior
              # H = extract_high_risk_subgraph(G)
              #  visualize_graph(H, title=f"Anomalous Window {i+1}")

              # break  # visualize only first anomaly
                visualize_pyvis(G, output_file=f"anomaly_window_{i+1}.html")
                break


        else:
            print("✅ Normal behavior")


if __name__ == "__main__":
    main()
