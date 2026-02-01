def normalize_event(event):
    EVENT_MAP = {
        "NtCreateFile": "FILE_OPEN",
        "NtReadFile": "FILE_READ",
        "NtWriteFile": "FILE_WRITE",
        "socket": "NETWORK_CONNECT",
        "connect": "NETWORK_CONNECT",
        "fork": "PROCESS_SPAWN",
        "execve": "PROCESS_EXEC",
        "setuid": "PRIV_ESC"
    }
    return EVENT_MAP.get(event, "OTHER")
