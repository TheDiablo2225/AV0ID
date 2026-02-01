from pyvis.network import Network

HIGH_RISK_EVENTS = {
    "EVENT_EXECUTE",
    "EVENT_FORK",
    "EVENT_MODIFY_PROCESS",
    "EVENT_MODIFY_FILE_ATTRIBUTES",
    "EVENT_CONNECT"
}


def visualize_pyvis(G, output_file="anomaly_graph.html"):
    net = Network(
        height="750px",
        width="100%",
        directed=True,
        notebook=False
    )

    net.force_atlas_2based(
        gravity=-30,
        central_gravity=0.01,
        spring_length=120,
        spring_strength=0.08,
        damping=0.4
    )

    added_nodes = set()

    for u, v, data in G.edges(data=True):
        evt = data.get("event_type")

        if evt not in HIGH_RISK_EVENTS:
            continue

        u_id = u[:8]
        v_id = v[:8]

        if u_id not in added_nodes:
            net.add_node(
                u_id,
                label=u_id,
                color="#ff6666",
                title=f"UUID: {u}"
            )
            added_nodes.add(u_id)

        if v_id not in added_nodes:
            net.add_node(
                v_id,
                label=v_id,
                color="#ff9999",
                title=f"UUID: {v}"
            )
            added_nodes.add(v_id)

        net.add_edge(
            u_id,
            v_id,
            label=evt,
            title=evt,
            arrows="to"
        )

    # ✅ CRITICAL FIX: do NOT use net.show()
    net.write_html(output_file, open_browser=True)
    print(f"✅ Interactive graph written to {output_file}")
