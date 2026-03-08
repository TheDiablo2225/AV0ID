# explanation_engine.py

def generate_explanation(violations):
    explanation = []

    for evt in violations:
        if evt == "PRIV_ESC":
            explanation.append("Unexpected privilege escalation detected.")
        elif evt == "MEM_ALLOC":
            explanation.append("Suspicious memory allocation sequence.")
        elif evt == "PROCESS_SPAWN":
            explanation.append("Unexpected process creation pattern.")
        elif evt == "NETWORK_CONNECT":
            explanation.append("Unusual outbound network behavior.")

    return explanation