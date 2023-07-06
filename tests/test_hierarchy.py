import io
import os
from unittest import TestCase
import pandas as pd

from piargus import Hierarchy, HierarchyNode


class TestHierarchy(TestCase):
    def test_to_hrc(self):
        hierarchy = Hierarchy({
            "Zuid-Holland": ["Rotterdam", "Den Haag"],
            "Noord-Holland": ["Haarlem"]})

        result = hierarchy.to_hrc().replace(os.linesep, "<CR>")
        expected = ("Zuid-Holland<CR>"
                    "@Rotterdam<CR>"
                    "@Den Haag<CR>"
                    "Noord-Holland<CR>"
                    "@Haarlem<CR>")
        self.assertEqual(expected, result)

    def test_from_hrc(self):
        hrc_text = ("Zuid-Holland<CR>"
                    "@Rotterdam<CR>"
                    "@Den Haag<CR>"
                    "@@Schilderswijk<CR>"
                    "Noord-Holland<CR>"
                    "@Haarlem<CR>")
        hrc_file = io.StringIO(hrc_text.replace("<CR>", "\n"))
        result = Hierarchy.from_hrc(hrc_file)
        expected = Hierarchy({
            "Zuid-Holland": {"Rotterdam": (),
                             "Den Haag": ["Schilderswijk"]},
            "Noord-Holland": ["Haarlem"]})
        self.assertEqual(expected.root, result.root)

    def test_item_manipulation(self):
        hierarchy = Hierarchy({
            "Zuid-Holland": ["Rotterdam", "Den Haag"],
            "Noord-Holland": ["Haarlem"]})

        utrecht_provincie = HierarchyNode("Utrecht")
        utrecht_stad = HierarchyNode("Utrecht")

        hierarchy.get_node('Noord-Holland').children += tuple([HierarchyNode("Amsterdam")])
        hierarchy.get_node("Zuid-Holland/Den Haag").parent = None
        hierarchy.root.children += tuple([utrecht_provincie])
        hierarchy.get_node("Utrecht").children = [utrecht_stad]

        expected = Hierarchy({'Zuid-Holland': ['Rotterdam'],
                              'Noord-Holland': ['Haarlem', 'Amsterdam'],
                              'Utrecht': ['Utrecht']})
        self.assertEqual(expected, hierarchy)

    def test_from_rows(self):
        df = pd.DataFrame([
            {"province": "Zuid-Holland", "city": "Rotterdam"},
            {"province": "Zuid-Holland", "city": "Den Haag"},
            {"province": "Noord-Holland", "city": "Haarlem"},
            {"province": "Noord-Holland", "city": "Amsterdam"},
            {"province": "Utrecht", "city": "Utrecht"},
        ])

        result = Hierarchy.from_rows(df)
        expected = Hierarchy({'Zuid-Holland': ['Rotterdam', 'Den Haag'],
                              'Noord-Holland': ['Haarlem', 'Amsterdam'],
                              'Utrecht': ['Utrecht']})
        self.assertEqual(expected, result)

    def test_to_rows(self):
        hierarchy = Hierarchy({'Zuid-Holland': ['Rotterdam', 'Den Haag'],
                               'Noord-Holland': ['Haarlem', 'Amsterdam'],
                               'Utrecht': ['Utrecht'],
                               "Zeeland": []})
        dataframe = pd.DataFrame(hierarchy.to_rows(), columns=["province", "city"])
        expected = pd.DataFrame([
            {"province": "Zuid-Holland", "city": "Rotterdam"},
            {"province": "Zuid-Holland", "city": "Den Haag"},
            {"province": "Noord-Holland", "city": "Haarlem"},
            {"province": "Noord-Holland", "city": "Amsterdam"},
            {"province": "Utrecht", "city": "Utrecht"},
            {"province": "Zeeland", "city": pd.NA},
        ])

        self.assertEqual(expected.to_dict('records'), dataframe.to_dict('records'))

    def test_codes(self):
        hierarchy = Hierarchy({
            "Zuid-Holland": ["Rotterdam", "Den Haag"],
            "Noord-Holland": ["Haarlem"]})

        result1 = [d.code for d in hierarchy.root.leaves]
        result2 = [d.code for d in hierarchy.root.descendants]
        expected1 = ['Rotterdam', 'Den Haag', 'Haarlem']
        expected2 = ['Zuid-Holland', 'Rotterdam', 'Den Haag', 'Noord-Holland', 'Haarlem']
        self.assertEqual(expected1, result1)
        self.assertEqual(expected2, result2)
        self.assertEqual(13, hierarchy.column_length())
