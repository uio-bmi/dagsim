import numpy as np
import numpy.random
from itertools import product
import random

BASE_SEQ_FN = "rep.txt"
AIRR_SIZE = 1000


def randint(*args, **kwargs):
    return np.random.randint(*args, **kwargs)


def binomial(*args, **kwargs):
    return np.random.binomial(*args, **kwargs)


def _get_olga_seq(protocol):
    for line in open(BASE_SEQ_FN):
        seq = line.strip()
        if len(seq) < 10:
            continue
        if protocol == 1 and not seq.startswith("CAS"):
            continue
        yield seq


def assign_protocol(disease):
    return numpy.random.binomial(1, 0.1 + 0.8 * disease)


def create_airr(disease, age, protocol):
    airr = []
    left = AIRR_SIZE
    for seq in _get_olga_seq(protocol):
        if left == 0:
            break
        if disease == 1:
            seq = seq[0:5] + _get_signal() + seq[8:len(seq)]
        clono_size = _get_clono_size(age, left)
        left -= clono_size
        airr.append((seq, clono_size))
    assert left == 0
    return airr


def _get_clono_size(age, max_left):
    return int(min(numpy.random.lognormal((120 - age) / 20, 1.5), max_left))


def _get_signal():
    return random.choice(["CAT", "CAR", "CAS", "DOG"])


def encode_kmers(airr):
    alphabet = "ARNDCQEGHILKMFPOSUTWYVBZXJ"
    # alphabet = "ACSTRDOG"
    k = 3
    kmers = sorted(list([''.join(x) for x in product(*[alphabet] * k)]))
    counts = dict([(kmer, 0) for kmer in kmers])
    for seq, _ in airr:
        for i in range(len(seq) - k + 1):
            sub = seq[i:i + k]
            counts[sub] += 1
    occ_vector = [counts[kmer] for kmer in kmers]
    return occ_vector
