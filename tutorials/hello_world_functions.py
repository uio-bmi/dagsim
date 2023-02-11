from random import choices


def simulate_sequence(seq_len, p_head):
    return "".join(choices(["H", "T"], [p_head, 1 - p_head], k=seq_len))
