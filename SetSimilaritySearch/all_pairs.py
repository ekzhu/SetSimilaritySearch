import logging
from collections import defaultdict
import numpy as np

from SetSimilaritySearch.utils import _frequency_order_transform, \
        _similarity_funcs, _overlap_threshold_funcs, _position_filter_funcs, \
        _symmetric_similarity_funcs

def all_pairs(sets, similarity_func_name="jaccard",
        similarity_threshold=0.5):
    """Find all pairs of sets with similarity greater than a threshold.
    This is an implementation of the All-Pair-Binary algorithm in the paper
    "Scaling Up All Pairs Similarity Search" by Bayardo et al., with
    position filter enhancement.

    Args:
        sets (list): a list of sets, each entry is an iterable representing a
            set.
        similarity_func_name (str): the name of the similarity function used;
            this function currently supports `"jaccard"` and `"cosine"`.
        similarity_threshold (float): the threshold used, must be a float
            between 0 and 1.0.

    Returns:
        pairs (Iterator[tuple]): an iterator of tuples `(x, y, similarity)`
            where `x` and `y` are the indices of sets in the input list `sets`.
    """
    if not isinstance(sets, list) or len(sets) == 0:
        raise ValueError("Input parameter sets must be a non-empty list.")
    if similarity_func_name not in _similarity_funcs:
        raise ValueError("Similarity function {} is not supported.".format(
            similarity_func_name))
    if similarity_threshold < 0 or similarity_threshold > 1.0:
        raise ValueError("Similarity threshold must be in the range [0, 1].")
    if similarity_func_name not in _symmetric_similarity_funcs:
        raise ValueError("The similarity function must be symmetric "
        "({})".format(", ".join(_symmetric_similarity_funcs)))
    similarity_func = _similarity_funcs[similarity_func_name]
    overlap_threshold_func = _overlap_threshold_funcs[similarity_func_name]
    position_filter_func = _position_filter_funcs[similarity_func_name]
    sets, _ = _frequency_order_transform(sets)
    index = defaultdict(list)
    logging.debug("Find all pairs with similarities >= {}...".format(
        similarity_threshold))
    count = 0
    for x1 in np.argsort([len(s) for s in sets]):
        s1 = sets[x1]
        t = overlap_threshold_func(len(s1), similarity_threshold)
        prefix_size = len(s1) - t + 1
        prefix = s1[:prefix_size]
        # Find candidates using tokens in the prefix.
        candidates = set([x2 for p1, token in enumerate(prefix)
                for x2, p2 in index[token]
                if position_filter_func(s1, sets[x2], p1, p2,
                    similarity_threshold)])
        for x2 in candidates:
            s2 = sets[x2]
            sim = similarity_func(s1, s2)
            if sim < similarity_threshold:
                continue
            # Output reverse-ordered set index pair (larger first).
            yield tuple(sorted([x1, x2], reverse=True) + [sim,])
            count += 1
        # Insert this prefix into index.
        for j, token in enumerate(prefix):
            index[token].append((x1, j))
    logging.debug("{} pairs found.".format(count))

