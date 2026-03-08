import math
from collections import defaultdict
from .violation_score import compute_violation_score
from .temporal_smoothing import EMASmoother
from .explanation_engine import generate_explanation


class ELVEEngine:
    def __init__(self, automaton, threshold=0.4):
        self.automaton = automaton
        self.threshold = threshold
        self.smoother = EMASmoother(alpha=0.3)
        self.persistence_counter = 0

    def process_window(self, event_sequence):

        if len(event_sequence) < 2:
            return 0.0, "Normal", []

        violations = []
        rare_penalty = 0
        log_likelihood = 0
        transition_counts = defaultdict(int)

        total = len(event_sequence)

        # ==============================
        # Transition Evaluation Loop
        # ==============================

        for i in range(total - 1):
            s1 = event_sequence[i]
            s2 = event_sequence[i + 1]

            transition_counts[(s1, s2)] += 1

            # 1️⃣ Hard DFA violation
            if s1 not in self.automaton.allowed or \
               s2 not in self.automaton.allowed[s1]:
                violations.append(s2)

            # 2️⃣ Markov probability
            p = self.automaton.probabilities.get((s1, s2), 1e-6)
            log_likelihood += -math.log(p)

            # 3️⃣ Rare transition penalty
            if p < 0.01:
                rare_penalty += 1

        # ==============================
        # Persistence Tracking
        # ==============================

        if len(violations) > 0:
            self.persistence_counter += 1
        else:
            self.persistence_counter = 0

        persistence_score = min(self.persistence_counter / 5, 1.0)

        # ==============================
        # Entropy Deviation
        # ==============================

        entropy_score = self.compute_entropy_deviation(
            transition_counts,
            self.automaton.baseline_entropy
        )

        # ==============================
        # Sparsity Deviation
        # ==============================

        current_sparsity = len(transition_counts)
        baseline_sparsity = self.automaton.baseline_sparsity

        sparsity_score = abs(current_sparsity - baseline_sparsity) / \
                         (baseline_sparsity + 1)

        # ==============================
        # Component Scores
        # ==============================

        hard_violation_score = compute_violation_score(
            violations,
            total
        )

        rare_score = rare_penalty / total
        markov_score = log_likelihood / total

        # ==============================
        # Hybrid Risk Fusion (ELVE)
        # ==============================

        elve_risk = (
            0.25 * hard_violation_score +
            0.15 * rare_score +
            0.15 * entropy_score +
            0.25 * markov_score +
            0.10 * persistence_score +
            0.10 * sparsity_score
        )

        # Temporal smoothing
        smoothed_score = self.smoother.update(elve_risk)

        label = "Suspicious" if smoothed_score > self.threshold else "Normal"

        explanation = generate_explanation(violations)

        return smoothed_score, label, explanation

    # =====================================
    # Entropy Deviation Computation
    # =====================================

    def compute_entropy_deviation(self, transition_counts, baseline_entropy):

        state_probs = defaultdict(list)
        state_totals = defaultdict(int)

        for (s1, s2), count in transition_counts.items():
            state_totals[s1] += count

        for (s1, s2), count in transition_counts.items():
            state_probs[s1].append(count / state_totals[s1])

        deviation = 0

        for s1 in state_probs:
            probs = state_probs[s1]
            H = -sum(p * math.log2(p) for p in probs if p > 0)
            baseline_H = baseline_entropy.get(s1, 0)
            deviation += abs(H - baseline_H)

        return deviation