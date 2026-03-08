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
        height="800px",
        width="100%",
        directed=True,
        bgcolor="#1e1e2f",              # Dark background
        font_color="white",
        notebook=False
    )

    # 🔥 Improved physics (cleaner clustering)
    net.force_atlas_2based(
        gravity=-50,
        central_gravity=0.015,
        spring_length=150,
        spring_strength=0.05,
        damping=0.6
    )

    net.set_options("""
    var options = {
      "nodes": {
        "borderWidth": 2,
        "shadow": true,
        "font": {
          "size": 14
        }
      },
      "edges": {
        "color": {
          "inherit": false
        },
        "smooth": {
          "type": "dynamic"
        },
        "arrows": {
          "to": {
            "enabled": true,
            "scaleFactor": 0.7
          }
        }
      },
      "interaction": {
        "hover": true,
        "tooltipDelay": 200,
        "navigationButtons": true,
        "keyboard": true
      },
      "physics": {
        "stabilization": {
          "iterations": 200
        }
      }
    }
    """)

    added_nodes = set()

    for u, v, data in G.edges(data=True):
        evt = data.get("event_type")

        if evt not in HIGH_RISK_EVENTS:
            continue

        u_id = u[:8]
        v_id = v[:8]

        # 🟠 Node Styling by Role (simple heuristic)
        def get_node_style(node_id):
            if "proc" in node_id.lower():
                return ("dot", "#ff4d4d")     # Process = red
            elif "file" in node_id.lower():
                return ("box", "#4da6ff")     # File = blue
            elif "net" in node_id.lower():
                return ("triangle", "#ffa64d") # Network = orange
            else:
                return ("dot", "#cccccc")     # Default = gray

        if u_id not in added_nodes:
            shape, color = get_node_style(u)
            net.add_node(
                u_id,
                label=u_id,
                shape=shape,
                color=color,
                size=20,
                title=f"""
                <b>UUID:</b> {u}<br>
                <b>Role:</b> Source<br>
                """
            )
            added_nodes.add(u_id)

        if v_id not in added_nodes:
            shape, color = get_node_style(v)
            net.add_node(
                v_id,
                label=v_id,
                shape=shape,
                color=color,
                size=20,
                title=f"""
                <b>UUID:</b> {v}<br>
                <b>Role:</b> Target<br>
                """
            )
            added_nodes.add(v_id)

        # 🔥 Edge styling based on severity
        edge_color = "#ff0000" if evt in HIGH_RISK_EVENTS else "#aaaaaa"

        net.add_edge(
            u_id,
            v_id,
            label=evt,
            title=f"<b>Event:</b> {evt}",
            color=edge_color,
            width=2
        )

    net.write_html(output_file, open_browser=True)
    print(f"🔥 Interactive graph written to {output_file}")
