import unittest

from SetSimilaritySearch import SearchIndex

class TestSearchIndex(unittest.TestCase):

    def test_jaccard(self):
        sets = [[1,2,3], [3,4,5], [2,3,4], [5,6,7]]
        index = SearchIndex(sets, similarity_func_name="jaccard",
                similarity_threshold=0.1)
        results = index.query([3,5,4])
        correct_results = set([(1, 1.0), (0, 0.2), (2, 0.5), (3, 0.2)])
        self.assertEqual(set(results), correct_results)

if __name__ == "__main__":
    unittest.main()
