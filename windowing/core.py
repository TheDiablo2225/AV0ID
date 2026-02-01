from preprocessing.stream_events import stream_cadets_events
from windowing.event_windows import sliding_event_windows
from graph.build_graph import build_provenance_graph
from graph.graph_metrics import extract_graph_metrics

events = stream_cadets_events(
    r"C:\AVOID\darpa\ta1-cadets-e3-official-1.json"
)

windows = sliding_event_windows(events)

first_window = next(windows)
G = build_provenance_graph(first_window)

metrics = extract_graph_metrics(G)

for k, v in metrics.items():
    print(k, ":", v)
