import io
import unittest
import pandas as pd

from piargus import TreeHierarchy
from piargus.recode import recode, read_grc


class TestRecode(unittest.TestCase):
    def setUp(self):
        tree = TreeHierarchy(total_code="T")
        tree.create_node("1/11/111")
        tree.create_node("1/11/112")
        tree.create_node("1/11/113")
        tree.create_node("2/21/210")
        tree.create_node("3/32/320")
        self.hierarchy = tree

    def test_recode_mapping(self):
        data = pd.Series(["111", "112", "113", "112", "210", "320"])

        recoding = {
            "1": [slice("100", "199")],
            "23": [slice("200", "299"), slice("300", "399")],
        }

        result = recode(data, recoding)
        expected = pd.Series(["1", "1", "1", "1", "23", "23"])

        self.assertEqual(list(expected), list(result))

    def test_recode_tree_level(self):
        data = pd.Series(["111", "112", "113", "112", "210", "320"])

        results = [
            recode(data, 0, self.hierarchy),
            recode(data, 1, self.hierarchy),
            recode(data, 2, self.hierarchy),
            recode(data, 3, self.hierarchy),
        ]
        expecteds = [
            pd.Series(["T", "T", "T", "T", "T", "T"]),
            pd.Series(["1", "1", "1", "1", "2", "3"]),
            pd.Series(["11", "11", "11", "11", "21", "32"]),
            data,
        ]

        for res, exp in zip(results, expecteds):
            self.assertEqual(list(exp), list(res))

    def test_recode_tree_file_leafs(self):
        data = pd.Series(["111", "112", "113", "112", "210", "320"])
        leafs = ["21", "320", "1"]
        result = recode(data, leafs, hierarchy=self.hierarchy)
        expected = pd.Series(["1", "1", "1", "1", "21", "320"])

        self.assertEqual(list(expected), list(result))

    def test_read_grc1(self):
        filelike = io.StringIO()
        for line in ["<TREERECODE>", "21", "320", "1"]:
            filelike.write(line + "\n")
        filelike.seek(0)

        result = read_grc(filelike)
        expected = ['21', '320', '1']

        self.assertEqual(expected, result)

    def test_read_grc2(self):
        filelike = io.StringIO()
        for line in ["1: 100-199", "23: 200-299, 300-399"]:
            filelike.write(line + "\n")
        filelike.seek(0)

        result = read_grc(filelike)
        expected = {
            "1": [slice("100", "199")],
            "23": [slice("200", "299"), slice("300", "399")],
        }
        self.assertEqual(expected, result)


if __name__ == '__main__':
    unittest.main()
