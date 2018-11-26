import unittest
import random
import numpy as np

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

    def test_identity_matrix(self):
        # Use all-pair to generate an lower-triangular identity matix
        nsets = 10
        population = list(range(100))
        sets = [set(population) - set(random.choices(population, k=10))
                for i in range(nsets)]
        coords = all_pairs(sets, similarity_threshold=0)
        arr = np.nan * np.empty((nsets, nsets))
        x, y, z = zip(*coords)
        arr[x, y] = z
        # Verify if arr is a lower-triangular matrix.
        for i in range(nsets):
            for j in range(nsets):
                if i > j:
                    self.assertFalse(np.isnan(arr[i, j]))
                else:
                    self.assertTrue(np.isnan(arr[i, j]))


if __name__ == "__main__":
    unittest.main()
