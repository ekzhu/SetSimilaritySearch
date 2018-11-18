import logging
from collections import defaultdict, Counter
import numpy as np

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

_similarity_funcs = {
    "jaccard": _jaccard,
    "cosine": _cosine,
}

_overlap_threshold_funcs = {
    "jaccard": _jaccard_overlap_threshold_func,
    "cosine": _cosine_overlap_threshold_func,
}

_position_filter_funcs = {
    "jaccard": _jaccard_position_filter,
    "cosine": _cosine_position_filter,
}

def _frequency_order_transform(sets):
    """Transform tokens to integers according to global frequency order.
    This step replaces all original tokens in the sets with integers, and
    helps to speed up subsequent prefix filtering and similarity computation.
    See Section 4.3.2 in the paper "A Primitive Operator for Similarity Joins
    in Data Cleaning" by Chaudhuri et al..

    Args:
        sets (list): a list of sets, each entry is an iterable representing a
        set.

    Returns:
        sets (list): a list of sets, each entry is a sorted Numpy array with
        integer tokens replacing the tokens in the original set.
    """
    logging.debug("Applying frequency order transform on tokens...")
    counts = reversed(Counter(token for s in sets for token in s).most_common())
    order = dict((token, i) for i, (token, _) in enumerate(counts))
    sets = [np.sort([order[token] for token in s]) for s in sets]
    logging.debug("Done applying frequency order.")
    return sets


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
    similarity_func = _similarity_funcs[similarity_func_name]
    overlap_threshold_func = _overlap_threshold_funcs[similarity_func_name]
    position_filter_func = _position_filter_funcs[similarity_func_name]
    sets = _frequency_order_transform(sets)
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
            yield (x1, x2, sim)
            count += 1
        # Insert this prefix into index
        for j, token in enumerate(prefix):
            index[token].append((x1, j))
    logging.debug("{} pairs found.".format(count))

