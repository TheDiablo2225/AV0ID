def z_score(value, mean, std):
    if std == 0:
        return 0.0
    return abs(value - mean) / std


def compute_anomaly_score(metrics, baseline):
    score = 0.0
    explanations = []

    # Scalar metrics
    for key in baseline:
        if key == "edge_type_freq":
            continue

        b = baseline[key]
        z = z_score(metrics[key], b["mean"], b["std"])
        score += z

        if z > 3:
            explanations.append(
                f"{key} deviates significantly (z={z:.2f})"
            )

    # Edge type frequency deviation
    for evt, freq in metrics["edge_type_freq"].items():
        if evt in baseline["edge_type_freq"]:
            b = baseline["edge_type_freq"][evt]
            z = z_score(freq, b["mean"], b["std"])
            score += z

            if z > 3:
                explanations.append(
                    f"Edge type {evt} abnormal (z={z:.2f})"
                )

    return score, explanations
