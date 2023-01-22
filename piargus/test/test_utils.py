import unittest

import piargus as pa
from piargus.utils import join_rules_with_holding


class TestUtils(unittest.TestCase):
    def test_join_rules_with_holding(self):
        result = join_rules_with_holding(
            {pa.dominance_rule(3, 75), pa.frequency_rule(5, 20)},
            {pa.p_rule(5), pa.frequency_rule(6, 15), pa.request_rule(2, 2, 9)},
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
            join_rules_with_holding([pa.p_rule(2), pa.p_rule(3), pa.p_rule(4)], [])


if __name__ == '__main__':
    unittest.main()
