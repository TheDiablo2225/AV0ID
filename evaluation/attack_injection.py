def inject_exploit(window):
    """
    Injects a synthetic attack burst into the event window.
    Designed to affect CFG, Behavioral, and ELVE modules.
    """

    attack_events = []

    for i in range(20):
        attack_events.append({
            "event_type": "setuid",
            "category": "process",
            "pid": 9999
        })

    for i in range(30):
        attack_events.append({
            "event_type": "NETWORK_CONNECT",
            "category": "network",
            "pid": 9999
        })

    for i in range(30):
        attack_events.append({
            "event_type": "MEM_WRITE",
            "category": "memory",
            "pid": 9999
        })

    for i in range(20):
        attack_events.append({
            "event_type": "fork",
            "category": "process",
            "pid": 9999
        })

    return window + attack_events