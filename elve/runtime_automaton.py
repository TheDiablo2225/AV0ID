import math
class RuntimeAutomaton:
    def __init__(self, baseline):
        self.allowed = baseline["allowed"]
        self.probabilities = baseline["probabilities"]
        self.baseline_entropy = baseline["entropy"]
        self.baseline_sparsity = baseline["sparsity"]

    def evaluate_sequence(self, sequence):
        violations = []
        rare_penalty = 0
        log_likelihood = 0
        transition_counts = {}

        for i in range(len(sequence) - 1):
            s1 = sequence[i]
            s2 = sequence[i+1]

            transition_counts[(s1, s2)] = transition_counts.get((s1, s2), 0) + 1

            # Hard violation
            if s1 not in self.allowed or s2 not in self.allowed[s1]:
                violations.append(s2)

            # Markov probability
            p = self.probabilities.get((s1, s2), 1e-6)
            log_likelihood += -math.log(p)

            # Rare transition penalty
            if p < 0.01:
                rare_penalty += 1

        return violations, rare_penalty, log_likelihood, transition_counts