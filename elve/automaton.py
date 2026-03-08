class ExecutionAutomaton:
    def __init__(self):
        self.start_state = "S0"
        self.transitions = self._build_transitions()

    def _build_transitions(self):
        return {
            ("S0", "FILE_OPEN"): "S1",
            ("S1", "FILE_READ"): "S2",
            ("S2", "FILE_WRITE"): "S2",
            ("S2", "NETWORK_CONNECT"): "S3",
            ("S3", "FILE_WRITE"): "S3",
            ("S2", "EXIT"): "S4",
            ("S3", "EXIT"): "S4"
        }

    def next_state(self, current_state, event):
        return self.transitions.get((current_state, event))