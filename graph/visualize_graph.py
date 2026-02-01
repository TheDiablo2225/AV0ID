import networkx as nx
import matplotlib.pyplot as plt

HIGH_RISK_EVENTS = {
    "EVENT_EXECUTE",
    "EVENT_FORK",
    "EVENT_MODIFY_PROCESS",
    "EVENT_MODIFY_FILE_ATTRIBUTES",
    "EVENT_CONNECT"
}


def extract_high_risk_subgraph(G):
    H = nx.DiGraph()

    for u, v, data in G.edges(data=True):
        if data.get("event_type") in HIGH_RISK_EVENTS:
            H.add_edge(
                u[:8],  # shorten UUID for readability
                v[:8],
                event=data["event_type"]
            )

    return H


def visualize_graph(G, title="Provenance Subgraph"):
    if G.number_of_edges() == 0:
        print("No high-risk events to visualize.")
        return

    plt.figure(figsize=(12, 10))
    pos = nx.spring_layout(G, seed=42)

    nx.draw(
        G,
        pos,
        with_labels=True,
        node_size=1200,
        node_color="lightcoral",
        font_size=8,
        arrows=True
    )

    edge_labels = nx.get_edge_attributes(G, "event")
    nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels, font_size=7)

    plt.title(title)
    plt.show()
