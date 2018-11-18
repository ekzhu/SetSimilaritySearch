#!/usr/bin/env python3
import sys
import argparse
import logging
from collections import defaultdict
import csv

from SetSimilaritySearch import all_pairs, SearchIndex
from SetSimilaritySearch.utils import _similarity_funcs

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

def self_all_pairs(set_IDs, sets, similarity_func_name, similarity_threshold):
    count = 0
    logging.debug("Find pairs with similarity >= {}.".format(
        similarity_threshold))
    for x, y, sim in all_pairs(sets,
            similarity_func_name=similarity_func_name,
            similarity_threshold=similarity_threshold):
        yield (set_IDs[x], set_IDs[y], len(sets[x]), len(sets[y]), sim)
        count += 1
    logging.debug("Found {} pairs.".format(count))

def cross_collection_all_pairs(set_IDs_x, set_IDs_y, sets_x, sets_y,
        similarity_func_name, similarity_threshold):
    if len(sets_x) > len(sets_y):
        indexed_sets = sets_x
        indexed_set_IDs = set_IDs_x
        query_sets = sets_y
        query_set_IDs = set_IDs_y
    else:
        indexed_sets = sets_y
        indexed_set_IDs = set_IDs_y
        query_sets = sets_x
        query_set_IDs = set_IDs_x
    logging.debug("Building search index on {} sets.".format(len(indexed_sets)))
    index = SearchIndex(indexed_sets, similarity_func_name=similarity_func_name,
            similarity_threshold=similarity_threshold)
    logging.debug("Finished building search index.")
    logging.debug("Find pairs with similarity >= {}.".format(
        similarity_threshold))
    count = 0
    for set_ID, s in zip(query_set_IDs, query_sets):
        for i, sim in index.query(s):
            yield (set_ID, indexed_set_IDs[i], len(s), len(indexed_sets[i]), sim)
            count += 1
    logging.debug("Found {} pairs.".format(count))

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Find all pairs of sets with "
        "similarities over a given threshold.")
    parser.add_argument("--input-sets", required=True, nargs="+",
            help="Input flattened set files with each line a (SetID Token) "
            "tuple: 1 file for finding self all pairs (self-join); 2 files for "
            "finding cross-collection all pairs (join).")
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

    if len(args.input_sets) == 1:
        set_IDs, sets = read_sets(args.input_sets[0], args.reversed_tuple)
        pairs = self_all_pairs(set_IDs, sets, args.similarity_func,
                args.similarity_threshold)
    elif len(args.input_sets) == 2:
        set_IDs_x, sets_x = read_sets(args.input_sets[0], args.reversed_tuple)
        set_IDs_y, sets_y = read_sets(args.input_sets[1], args.reversed_tuple)
        pairs = cross_collection_all_pairs(set_IDs_x, set_IDs_y, sets_x,
                sets_y, args.similarity_func, args.similarity_threshold)
    else:
        raise ValueError("Number of input set files must be 1 or 2.")
    with open(args.output_pairs, "w") as f:
        writer = csv.writer(f)
        writer.writerow(["set_ID_x", "set_ID_y", "set_size_x", "set_size_y",
            "similarity"])
        writer.writerows(pairs)
