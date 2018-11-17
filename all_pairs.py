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
    sets = dict()
    for x, y in tuples:
        if x not in sets:
            sets[x] = []
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

def indexing(sets, overlap_threshold_func, similarity_threshold):
    logging.info("Building index with prefixes...")
    index = defaultdict(lambda: deque([]))
    for x in sets:
        t = overlap_threshold_func(len(sets[x]), similarity_threshold)
        prefix_size = len(sets[x]) - t + 1
        for j, y in enumerate(sets[x][:prefix_size]):
            index[y].append((x, j))
    for y in index:
        index[y] = sorted(list(index[y]))
    logging.info("Done building index, {} tokens.".format(len(index)))
    return index

def _all_pairs(sets, index, similarity_func, position_filter_func,
        similarity_threshold):
    pairs = set()
    for y in sorted(index.keys()):
        for ((x1, p1), (x2, p2)) in combinations(index[y], 2):
            if (x1, x2) in pairs:
                continue
            pairs.add((x1, x2))
            if not position_filter_func(sets[x1], sets[x2], p1, p2,
                    similarity_threshold):
                continue
            sim = similarity_func(sets[x1], sets[x2])
            if sim < similarity_threshold:
                continue
            yield (x1, x2, len(sets[x1]), len(sets[x2]), sim)

def all_pairs(sets, index, similarity_func, position_filter_func,
    similarity_threshold, out_file):
    logging.info("Find all pairs with similarities >= {}...".format(
        similarity_threshold))
    count = 0
    for x, y, size_x, size_y, sim in _all_pairs(sets, index,
            similarity_func, position_filter_func, similarity_threshold):
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
    index = indexing(sets, overlap_threshold_func, args.similarity_threshold)
    position_filter_func = position_filter_funcs[args.similarity_func]
    with open(args.output_pairs, "w") as f:
        all_pairs(sets, index, similarity_func, position_filter_func,
                args.similarity_threshold, f)
