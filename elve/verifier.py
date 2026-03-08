# verifier.py

from severity import SEVERITY_WEIGHTS

class ExecutionVerifier:
    def __init__(self, automaton, threshold=0.2):
        self.automaton = automaton
        self.threshold = threshold

    def verify(self, trace):
        state = self.automaton.start_state
        violation_score = 0
        violations = []

        for event in trace:
            next_state = self.automaton.next_state(state, event)

            if next_state:
                state = next_state
            else:
                weight = SEVERITY_WEIGHTS.get(event, 1)
                violation_score += weight
                violations.append((state, event))

        anomaly_score = violation_score / (violation_score + len(trace))

        label = "Zero-Day Suspicious" if anomaly_score > self.threshold else "Normal"

        return anomaly_score, label, violations