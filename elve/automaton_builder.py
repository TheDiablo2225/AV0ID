# automaton_builder.py

from collections import defaultdict
import math

class AutomatonBuilder:
    def __init__(self):
        self.transition_counts = defaultdict(int)
        self.state_counts = defaultdict(int)

    def observe_sequence(self, sequence):
        for i in range(len(sequence) - 1):
            s1 = sequence[i]
            s2 = sequence[i+1]

            self.transition_counts[(s1, s2)] += 1
            self.state_counts[s1] += 1

    def build(self, min_support=2):
        allowed = defaultdict(set)
        probabilities = {}
        entropy_profile = {}

        # Build probabilities
        for (s1, s2), count in self.transition_counts.items():
            total = self.state_counts[s1]
            prob = count / total
            probabilities[(s1, s2)] = prob

            if count >= min_support:
                allowed[s1].add(s2)

        # Compute baseline transition entropy per state
        for s1 in self.state_counts:
            probs = [
                probabilities[(s1, s2)]
                for (a, s2) in probabilities
                if a == s1
            ]
            H = -sum(p * math.log2(p) for p in probs if p > 0)
            entropy_profile[s1] = H

        sparsity = len(self.transition_counts)

        return {
            "allowed": allowed,
            "probabilities": probabilities,
            "entropy": entropy_profile,
            "sparsity": sparsity
        }