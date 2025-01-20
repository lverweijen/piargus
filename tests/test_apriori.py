import io
from unittest import TestCase

from piargus import Apriori


class AprioriTest(TestCase):
    def test_to_hst(self):
        apriori = Apriori()

        apriori.set_status(['A', '3'], 'S')
        apriori.set_cost(['A', '3'], 5)
        apriori.set_protection_level(['A', '3'], 20)

        result = apriori.to_hst()
        expected = ("A,3,s\n"
                    "A,3,c,5\n"
                    "A,3,pl,20\n")
        self.assertEqual(expected, result)

    def test_from_hst(self):
        file = io.StringIO("A,3, S\n"
                           "A,3, C, 5\n"
                           "A,3, PL, 20\n")
        result = Apriori.from_hst(file)
        result_repr = repr(result)
        expected_repr = ("Apriori(["
                    "(['A', '3'], 's'),\n"
                    "(['A', '3'], 'c', 5),\n"
                    "(['A', '3'], 'pl', 20)])")
        self.assertEqual(expected_repr, result_repr)
