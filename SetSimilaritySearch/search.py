import logging
from collections import defaultdict, deque
import numpy as np

from SetSimilaritySearch.utils import _frequency_order_transform, \
        _similarity_funcs, _overlap_threshold_funcs, _position_filter_funcs, \
        _symmetric_similarity_funcs, _asymmetric_similarity_funcs, \
        _overlap_index_threshold_funcs

class SearchIndex(object):
    """This data structure supports set similarity search queries.
    The algorithm is a combination of the prefix filter and position filter
    techniques.

    Args:
        sets (list): a list of sets, each entry is an iterable representing a
            set.
        similarity_func_name (str): the name of the similarity function used;
            this function currently supports `"jaccard"`, `"cosine"`, and
            `"containment"`.
        similarity_threshold (float): the threshold used, must be a float
            between 0 and 1.0.
    """

    def __init__(self, sets, similarity_func_name="jaccard",
            similarity_threshold=0.5):
        if not isinstance(sets, list) or len(sets) == 0:
            raise ValueError("Input parameter sets must be a non-empty list.")
        if similarity_func_name not in _similarity_funcs:
            raise ValueError("Similarity function {} is not supported.".format(
                similarity_func_name))
        if similarity_threshold < 0 or similarity_threshold > 1.0:
            raise ValueError(
                    "Similarity threshold must be in the range [0, 1].")
        self.similarity_threshold = similarity_threshold
        self.similarity_func = _similarity_funcs[similarity_func_name]
        self.overlap_threshold_func = \
                _overlap_threshold_funcs[similarity_func_name]
        self.overlap_index_threshold_func = \
                _overlap_index_threshold_funcs[similarity_func_name]
        self.position_filter_func = _position_filter_funcs[similarity_func_name]
        logging.debug("Building SearchIndex on {} sets.".format(len(sets)))
        logging.debug("Start frequency transform.")
        self.sets, self.order = _frequency_order_transform(sets)
        logging.debug("Finish frequency transform, {} tokens in total.".format(
            len(self.order)))
        self.index = defaultdict(list)
        logging.debug("Start indexing sets.")
        for i, s in enumerate(self.sets):
            prefix = self._get_prefix_index(s)
            for j, token in enumerate(prefix):
                self.index[token].append((i, j))
        logging.debug("Finished indexing sets.")

    def _get_prefix_index(self, s):
        t = self.overlap_index_threshold_func(len(s), self.similarity_threshold)
        prefix_size = len(s) - t + 1
        return s[:prefix_size]

    def _get_prefix(self, s):
        t = self.overlap_threshold_func(len(s), self.similarity_threshold)
        prefix_size = len(s) - t + 1
        return s[:prefix_size]

    def query(self, s):
        """Query the search index for sets similar to the query set.

        Args:
            s (Iterable): the query set.

        Returns (list): a list of tuples `(index, similarity)` where the index
            is the index of the matching sets in the original list of sets.
        """
        s1 = np.sort([self.order[token] for token in s if token in self.order])
        logging.debug("{} original tokens and {} tokens after applying "
            "frequency order.".format(len(s), len(s1)))
        prefix = self._get_prefix(s1)
        candidates = set([i for p1, token in enumerate(prefix)
                for i, p2 in self.index[token]
                if self.position_filter_func(s1, self.sets[i], p1, p2,
                    self.similarity_threshold)])
        logging.debug("{} candidates found.".format(len(candidates)))
        results = deque([])
        for i in candidates:
            s2 = self.sets[i]
            sim = self.similarity_func(s1, s2)
            if sim < self.similarity_threshold:
                continue
            results.append((i, sim))
        logging.debug("{} verified sets found.".format(len(results)))
        return list(results)

