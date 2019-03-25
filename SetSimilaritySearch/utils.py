import logging
from collections import Counter
import numpy as np

def _jaccard_overlap_threshold_func(x, t):
    return int(x * t)

_jaccard_overlap_index_threshold_func = _jaccard_overlap_threshold_func

def _cosine_overlap_threshold_func(x, t):
    return int(np.sqrt(x) * t)

_cosine_overlap_index_threshold_func = _cosine_overlap_threshold_func

def _containment_overlap_threshold_func(x, t):
    return int(x * t)

def _containment_overlap_index_threshold_func(x, t):
    return 1

def _containment_min_overlap_threshold_func(x, t):
    return int(x * t)

def _containment_min_overlap_index_threshold_func(x, t):
    return int(x * t)

def _jaccard_position_filter(s1, s2, p1, p2, t):
    l1, l2 = len(s1), len(s2)
    return float(min(l1-p1, l2-p2)) / float(max(l1, l2)) >= t

def _cosine_position_filter(s1, s2, p1, p2, t):
    l1, l2 = len(s1), len(s2)
    return float(min(l1-p1, l2-p2)) / np.sqrt(max(l1, l2)) >= t

def _containment_position_filter(s1, s2, p1, p2, t):
    l1, l2 = len(s1), len(s2)
    return float(min(l1-p1, l2-p2)) / float(l1) >= t

def _containment_min_position_filter(s1, s2, p1, p2, t):
    l1, l2 = len(s1), len(s2)
    return float(min(l1-p1, l2-p2)) / float(max(l1, l2)) >= t

def _jaccard(s1, s2):
    i = len(np.intersect1d(s1, s2, assume_unique=True))
    return float(i) / float(len(s1) + len(s2) - i)

def _cosine(s1, s2):
    i = len(np.intersect1d(s1, s2, assume_unique=True))
    return float(i) / np.sqrt(float(len(s1)*len(s2)))

def _containment(s1, s2):
    i = len(np.intersect1d(s1, s2, assume_unique=True))
    return float(i) / float(len(s1))

def _containment_min(s1, s2):
    i = len(np.intersect1d(s1, s2, assume_unique=True))
    return (float(i)) / (float(max(len(s1), len(s2))))

_similarity_funcs = {
    "jaccard": _jaccard,
    "cosine": _cosine,
    "containment": _containment,
    "containment_min": _containment_min,
}

_overlap_threshold_funcs = {
    "jaccard": _jaccard_overlap_threshold_func,
    "cosine": _cosine_overlap_threshold_func,
    "containment": _containment_overlap_threshold_func,
    "containment_min": _containment_min_overlap_threshold_func,
}

_overlap_index_threshold_funcs = {
    "jaccard": _jaccard_overlap_index_threshold_func,
    "cosine": _cosine_overlap_index_threshold_func,
    "containment": _containment_overlap_index_threshold_func,
    "containment_min": _containment_min_overlap_index_threshold_func,

}

_position_filter_funcs = {
    "jaccard": _jaccard_position_filter,
    "cosine": _cosine_position_filter,
    "containment": _containment_position_filter,
    "containment_min":  _containment_min_position_filter,
}

_symmetric_similarity_funcs = ["jaccard", "cosine", "containment_min"]
_asymmetric_similarity_funcs = ["containment"]

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
        order (dict): a dictionary that maps token to its integer representation
            in the frequency order.
    """
    logging.debug("Applying frequency order transform on tokens...")
    counts = reversed(Counter(token for s in sets for token in s).most_common())
    order = dict((token, i) for i, (token, _) in enumerate(counts))
    sets = [np.sort([order[token] for token in s]) for s in sets]
    logging.debug("Done applying frequency order.")
    return sets, order


