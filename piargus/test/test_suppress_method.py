import unittest

from piargus import ghmiter, modular, optimal, network, rounding, tabular_adjustment


class TestSuppressMethod(unittest.TestCase):
    def test_repr(self):
        self.assertEqual("SuppressMethod('GH', [0, 1])", repr(ghmiter()))

    def test_str(self):
        self.assertEqual("GH(<table>, 0, 1)", str(ghmiter()))
        self.assertEqual("MOD(<table>, 5, 1, 1, 1)", str(modular()))
        self.assertEqual("OPT(<table>, 0)", str(optimal()))
        self.assertEqual("NET(<table>)", str(network()))
        self.assertEqual("RND(<table>, 5, 0, 10, 0, 3)", str(rounding(5)))
        self.assertEqual("CTA(<table>)", str(tabular_adjustment()))


if __name__ == '__main__':
    unittest.main()
