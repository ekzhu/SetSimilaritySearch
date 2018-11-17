#!/usr/bin/env python3
import sys
import argparse
import logging
from collections import deque, Counter, defaultdict
from itertools import combinations
import numpy as np

def read_sets(set_filename, reversed=False):
    logging.info("Reading set tuples from {} (reversed={})...".format(
        set_filename, reversed))
    with open(set_filename) as f:
        tuples = [line.strip().split() for line in f
                if not line.startswith("#")]
    # Make sure the tuples are (SetID, Token).
    if reversed:
        tuples = [(y, x) for x, y in tuples]
    else:
        tuples = [(x, y) for x, y in tuples]
    logging.info("{} tuples read.".format(len(tuples)))
    logging.info("Creating sets...")
    sets = defaultdict(list)
    for x, y in tuples:
        sets[x].append(y)
    logging.info("{} sets created.".format(len(sets)))
    return sets

def frequency_order_transform(sets):
    logging.info("Applying frequency order transform on tokens...")
    counts = reversed(Counter(y for x in sets for y in sets[x]).most_common())
    order = dict((y, i) for i, (y, _) in enumerate(counts))
    for x in sets:
        sets[x] = [order[y] for y in sets[x]]
    logging.info("Done applying frequency order.")
    return sets

def use_numpy_array_and_sort(sets):
    logging.info("Using numpy array and sort sets...")
    for x in sets:
        sets[x] = np.array(sets[x])
        sets[x].sort()
    logging.info("Done using numpy array and sort sets.")
    return sets

def _all_pairs(sets, similarity_func, position_filter_func,
        similarity_threshold):
    index = defaultdict(list)
    for x1 in sorted(sets.keys(), key=lambda x: len(sets[x])):
        t = overlap_threshold_func(len(sets[x1]), similarity_threshold)
        prefix_size = len(sets[x1]) - t + 1
        prefix = sets[x1][:prefix_size]
        # Find candidates using tokens in the prefix.
        candidates = set([x2 for p1, token in enumerate(prefix)
                for x2, p2 in index[token]
                if position_filter_func(sets[x1], sets[x2], p1, p2,
                    similarity_threshold)])
        for x2 in candidates:
            sim = similarity_func(sets[x1], sets[x2])
            if sim < similarity_threshold:
                continue
            yield (x1, x2, len(sets[x1]), len(sets[x2]), sim)
        # Insert this set into index
        for j, token in enumerate(prefix):
            index[token].append((x1, j))

def all_pairs(sets, similarity_func, position_filter_func,
    similarity_threshold, out_file):
    logging.info("Find all pairs with similarities >= {}...".format(
        similarity_threshold))
    count = 0
    for x, y, size_x, size_y, sim in _all_pairs(sets, similarity_func,
            position_filter_func, similarity_threshold):
        out_file.write("{}, {}, {}, {}, {}\n".format(
            x, y, size_x, size_y, sim))
        count += 1
    logging.info("{} pairs computed, output to {}.".format(
        count, out_filename))

_jaccard_overlap_threshold_func = lambda x, t: int(x * t)

_cosine_overlap_threshold_func = lambda x, t: int(np.sqrt(x) * t)

def _jaccard_position_filter(s1, s2, p1, p2, t):
    l1, l2 = len(s1), len(s2)
    return float(min(l1-p1, l2-p2)) / float(max(l1, l2)) >= t

def _cosine_position_filter(s1, s2, p1, p2, t):
    l1, l2 = len(s1), len(s2)
    return float(min(l1-p1, l2-p2)) / np.sqrt(max(l1, l2)) >= t

def _jaccard(s1, s2):
    i = len(np.intersect1d(s1, s2, assume_unique=True))
    return float(i) / float(len(s1) + len(s2) - i)

def _cosine(s1, s2):
    i = len(np.intersect1d(s1, s2, assume_unique=True))
    return float(i) / np.sqrt(float(len(s1)*len(s2)))

similarity_funcs = {
    "jaccard": _jaccard,
    "cosine": _cosine,
}

overlap_threshold_funcs = {
    "jaccard": _jaccard_overlap_threshold_func,
    "cosine": _cosine_overlap_threshold_func,
}

position_filter_funcs = {
    "jaccard": _jaccard_position_filter,
    "cosine": _cosine_position_filter,
}

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Find all pairs of sets with "
        "similarities over a given threshold.")
    parser.add_argument("--input-sets", required=True,
            help="Input flattened set file with each line a (SetID Token) "
            "tuple.")
    parser.add_argument("--output-pairs", required=True,
            help="Output file with each line a "
            "(SetID_X, SetID_Y, Size_X, Size_Y, Similarity) tuple.")
    parser.add_argument("--similarity-func", choices=similarity_funcs.keys(),
        default="jaccard")
    parser.add_argument("--similarity-threshold", type=float, default=0.5)
    parser.add_argument("--reversed-tuple", type=bool, default=False,
            help="Whether the input tuples are reversed i.e. (Token SetID).")
    args = parser.parse_args(sys.argv[1:])
    logging.basicConfig(level=logging.INFO,
            format="%(asctime)s: %(message)s")
    sets = read_sets(args.input_sets, args.reversed_tuple)
    sets = frequency_order_transform(sets)
    sets = use_numpy_array_and_sort(sets)
    similarity_func = similarity_funcs[args.similarity_func]
    overlap_threshold_func = overlap_threshold_funcs[args.similarity_func]
    position_filter_func = position_filter_funcs[args.similarity_func]
    with open(args.output_pairs, "w") as f:
        all_pairs(sets, similarity_func, position_filter_func,
                args.similarity_threshold, f)
