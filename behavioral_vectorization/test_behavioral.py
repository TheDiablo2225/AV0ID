# test_behavioral.py

# Simulated raw execution events (what logs usually look like)
raw_events = [
    "fork", "execve",
    "NtCreateFile", "NtReadFile", "NtWriteFile",
    "NtCreateFile", "NtReadFile",
    "socket", "connect",
    "NtWriteFile",
    "fork", "execve",
    "NtCreateFile", "NtWriteFile",
    "socket", "connect",
    "NtReadFile",
    "setuid",  # privilege escalation attempt
    "NtCreateFile", "NtWriteFile"
] * 5   # repeat to get enough events
