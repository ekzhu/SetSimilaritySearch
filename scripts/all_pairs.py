#!/usr/bin/env python3
import sys
import argparse
import logging
from collections import defaultdict

from SetSimilaritySearch import all_pairs
from SetSimilaritySearch.all_pairs import _similarity_funcs

def read_sets(set_filename, reversed=False):
    logging.debug("Reading set tuples from {} (reversed={})...".format(
        set_filename, reversed))
    with open(set_filename) as f:
        tuples = [line.strip().split() for line in f
                if not line.startswith("#")]
    # Make sure the tuples are (SetID, Token).
    if reversed:
        tuples = [(y, x) for x, y in tuples]
    else:
        tuples = [(x, y) for x, y in tuples]
    logging.debug("{} tuples read.".format(len(tuples)))
    logging.debug("Creating sets...")
    sets = defaultdict(list)
    for x, y in tuples:
        sets[x].append(y)
    logging.debug("{} sets created.".format(len(sets)))
    set_IDs = list(sets.keys())
    sets = [sets[x] for x in set_IDs]
    return set_IDs, sets

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Find all pairs of sets with "
        "similarities over a given threshold.")
    parser.add_argument("--input-sets", required=True,
            help="Input flattened set file with each line a (SetID Token) "
            "tuple.")
    parser.add_argument("--output-pairs", required=True,
            help="Output file with each line a "
            "(SetID_X, SetID_Y, Size_X, Size_Y, Similarity) tuple.")
    parser.add_argument("--similarity-func", choices=_similarity_funcs.keys(),
        default="jaccard")
    parser.add_argument("--similarity-threshold", type=float, default=0.5)
    parser.add_argument("--reversed-tuple", type=bool, default=False,
            help="Whether the input tuples are reversed i.e. (Token SetID).")
    args = parser.parse_args(sys.argv[1:])
    logging.basicConfig(level=logging.DEBUG, format="%(asctime)s: %(message)s")
    set_IDs, sets = read_sets(args.input_sets, args.reversed_tuple)
    with open(args.output_pairs, "w") as f:
        for x, y, sim in all_pairs(sets,
                similarity_func_name=args.similarity_func,
                similarity_threshold=args.similarity_threshold):
            f.write("{}, {}, {}, {}, {}\n".format(
                set_IDs[x], set_IDs[y], len(sets[x]), len(sets[y]), sim))
