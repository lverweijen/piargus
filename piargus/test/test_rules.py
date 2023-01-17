import unittest

from piargus import safetyrule as rule


class TestSafetyRule(unittest.TestCase):
    def test_rules(self):
        self.assertEqual("NK(3, 75)", rule.dominance_rule(3, 75))
        self.assertEqual("NK(3, 75)", rule.dominance_rule(n=3, k=75))
        self.assertEqual("NK(3, 75)", rule.dominance_rule(k=75, n=3))
        self.assertEqual("P(15, 1)", rule.p_rule(15))
        self.assertEqual("P(15, 3)", rule.p_rule(15, n=3))
        self.assertEqual("ZERO(20)", rule.zero_rule(20))
        self.assertEqual("FREQ(5, 20)", rule.frequency_rule(5, 20))
        self.assertEqual("REQ(20, 30, 5)", rule.request_rule(20, 30, 5))
        self.assertEqual("MIS(1)", rule.missing_rule(True))
        self.assertEqual("WGT(0)", rule.weight_rule(False))
        self.assertEqual("MAN(20)", rule.manual_rule())

    def test_value_error(self):
        with self.assertRaises(ValueError):
            rule.dominance_rule(n=-1, k=110)

    def test_make_safety_rules(self):
        result = rule.make_safety_rule(
            {rule.dominance_rule(3, 75), rule.frequency_rule(5, 20)},
            {rule.p_rule(5), rule.frequency_rule(6, 15), rule.request_rule(2, 2, 9)},
        )
        expected = [
            'NK(3, 75)',
            'FREQ(5, 20)',
            'P(0, 0)',
            'P(0, 0)',
            'REQ(0, 0, 0)',
            'P(5, 1)',
            'FREQ(6, 15)',
            'REQ(2, 2, 9)'
        ]
        self.assertCountEqual(expected, result)

    def test_make_safety_rule_maximum(self):
        with self.assertRaises(ValueError):
            rule.make_safety_rule([rule.p_rule(2), rule.p_rule(3), rule.p_rule(4)], [])


if __name__ == '__main__':
    unittest.main()
