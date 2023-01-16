import unittest

from piargus import rules


class TestSafetyRule(unittest.TestCase):
    def test_rules(self):
        self.assertEqual("NK(3, 75)", rules.dominance(3, 75))
        self.assertEqual("NK(3, 75)", rules.dominance(n=3, k=75))
        self.assertEqual("NK(3, 75)", rules.dominance(k=75, n=3))
        self.assertEqual("P(15, 1)", rules.p(15))
        self.assertEqual("P(15, 3)", rules.p(15, n=3))
        self.assertEqual("ZERO(20)", rules.zero(20))
        self.assertEqual("FREQ(5, 20)", rules.frequency(5, 20))
        self.assertEqual("REQ(20, 30, 5)", rules.request(20, 30, 5))
        self.assertEqual("MIS(1)", rules.missing(True))
        self.assertEqual("WGT(0)", rules.weight(False))
        self.assertEqual("MAN(20)", rules.manual())

    def test_error(self):
        with self.assertRaises(ValueError):
            rules.dominance(n=-1, k=110)


if __name__ == '__main__':
    unittest.main()
