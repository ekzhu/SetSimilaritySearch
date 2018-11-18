import unittest

from SetSimilaritySearch import all_pairs

class TestAllPairs(unittest.TestCase):

    def test_jaccard(self):
        sets = [[1,2,3], [3,4,5], [2,3,4], [5,6,7]]
        correct_pairs = set([(1, 0, 0.2), (2, 0, 0.5), (2, 1, 0.5),
            (3, 1, 0.2)])
        pairs = list(all_pairs(sets, similarity_func_name='jaccard',
            similarity_threshold=0.1))
        for pair in pairs:
            self.assertTrue(pair in correct_pairs)
        self.assertEqual(len(pairs), len(correct_pairs))

if __name__ == "__main__":
    unittest.main()
