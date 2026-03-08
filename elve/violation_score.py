# violation_scorer.py

SEVERITY = {
    "PRIV_ESC": 10,
    "MEM_ALLOC": 4,
    "PROCESS_SPAWN": 6,
    "NETWORK_CONNECT": 5,
}

def compute_violation_score(violations, total_events):
    raw_score = sum(SEVERITY.get(evt, 1) for evt in violations)
    return raw_score / (raw_score + total_events)