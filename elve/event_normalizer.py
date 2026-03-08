# event_normalizer.py

ABSTRACTION_MAP = {
    "EVENT_OPEN": "FILE_OPEN",
    "EVENT_READ": "FILE_READ",
    "EVENT_WRITE": "FILE_WRITE",
    "EVENT_EXECUTE": "PROCESS_SPAWN",
    "EVENT_CONNECT": "NETWORK_CONNECT",
    "EVENT_MODIFY_PROCESS": "PRIV_ESC",
    "EVENT_MEMORY_ALLOC": "MEM_ALLOC",
}

def normalize(event_type):
    return ABSTRACTION_MAP.get(event_type, "UNKNOWN")