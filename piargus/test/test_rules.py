import unittest

from piargus import safetyrule as rule


class TestSafetyRule(unittest.TestCase):
    def test_rules(self):
        self.assertEqual("NK(3, 75)", rule.dominance(3, 75))
        self.assertEqual("NK(3, 75)", rule.dominance(n=3, k=75))
        self.assertEqual("NK(3, 75)", rule.dominance(k=75, n=3))
        self.assertEqual("P(15, 1)", rule.p(15))
        self.assertEqual("P(15, 3)", rule.p(15, n=3))
        self.assertEqual("ZERO(20)", rule.zero(20))
        self.assertEqual("FREQ(5, 20)", rule.frequency(5, 20))
        self.assertEqual("REQ(20, 30, 5)", rule.request(20, 30, 5))
        self.assertEqual("MIS(1)", rule.missing(True))
        self.assertEqual("WGT(0)", rule.weight(False))
        self.assertEqual("MAN(20)", rule.manual())

    def test_error(self):
        with self.assertRaises(ValueError):
            rule.dominance(n=-1, k=110)


if __name__ == '__main__':
    unittest.main()
