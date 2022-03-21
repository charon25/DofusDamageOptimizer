import unittest

from knapsack import _dp_knapsack


class TestDamages(unittest.TestCase):
    
    def test_empty_knapsack(self):
        weights = []
        values = []
        W = 1

        indexes, max_value = _dp_knapsack(weights, values, W)

        self.assertEqual(max_value, 0)
        self.assertEqual(indexes, [])

    def test_trivial_knapsack(self):
        weights = [1]
        values = [2]
        W = 1

        indexes, max_value = _dp_knapsack(weights, values, W)

        self.assertEqual(max_value, 2)
        self.assertEqual(indexes, [0])

    def test_knapsack_5_items(self):
        weights = [2, 7, 12, 9, 5]
        values = [1, 3, 7, 10, 2]
        W = 15

        indexes, max_value = _dp_knapsack(weights, values, W)

        self.assertEqual(max_value, 12)
        self.assertEqual(indexes, [3, 4])

    def test_knapsack_15_items(self):
        weights = [34, 9, 7, 37, 25, 4, 24, 40, 1, 31, 33, 14, 15, 30, 20]
        values = [2, 11, 5, 12, 11, 7, 14, 3, 18, 14, 13, 18, 19, 15, 16]
        W = 100

        indexes, max_value = _dp_knapsack(weights, values, W)

        self.assertEqual(max_value, 109)
        self.assertEqual(indexes, [1, 2, 5, 8, 11, 12, 13, 14])

if __name__ == '__main__':
    unittest.main()
