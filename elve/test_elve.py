from automaton import ExecutionAutomaton
from verifier import ExecutionVerifier

# Normal execution
normal_trace = [
    "FILE_OPEN",
    "FILE_READ",
    "FILE_WRITE",
    "NETWORK_CONNECT",
    "FILE_WRITE",
    "EXIT"
]

# Exploit-like execution
attack_trace = [
    "FILE_OPEN",
    "FILE_READ",
    "MEM_ALLOC",
    "MEM_WRITE",
    "PRIV_ESC",
    "NETWORK_CONNECT",
    "EXIT"
]

automaton = ExecutionAutomaton()
verifier = ExecutionVerifier(automaton)

print("Normal:", verifier.verify(normal_trace))
print("Attack:", verifier.verify(attack_trace))