import io
import os
from unittest import TestCase
import pandas as pd

from piargus import Hierarchy


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
        self.assertEqual(expected.tree, result.tree)

    def test_item_manipulation(self):
        hierarchy = Hierarchy({
            "Zuid-Holland": ["Rotterdam", "Den Haag"],
            "Noord-Holland": ["Haarlem"]})

        hierarchy.tree.add_path(['Noord-Holland', "Amsterdam"])
        hierarchy.tree['Zuid-Holland'].remove("Den Haag")
        hierarchy.tree.add('Utrecht')
        hierarchy.tree.add_path(['Utrecht', 'Utrecht'])
        hierarchy.tree.add('Noord-Holland')

        expected = Hierarchy({'Zuid-Holland': ['Rotterdam'],
                              'Noord-Holland': ['Haarlem', 'Amsterdam'],
                              'Utrecht': ['Utrecht']})
        self.assertEqual(expected.tree, hierarchy.tree)

    def test_from_dataframe(self):
        df = pd.DataFrame([
            {"province": "Zuid-Holland", "city": "Rotterdam"},
            {"province": "Zuid-Holland", "city": "Den Haag"},
            {"province": "Noord-Holland", "city": "Haarlem"},
            {"province": "Noord-Holland", "city": "Amsterdam"},
            {"province": "Utrecht", "city": "Utrecht"},
        ])

        hierarchy = Hierarchy()
        for path in df.itertuples(index=False):
            hierarchy.tree.add_path(path)

        expected = Hierarchy({'Zuid-Holland': ['Rotterdam', 'Den Haag'],
                              'Noord-Holland': ['Haarlem', 'Amsterdam'],
                              'Utrecht': ['Utrecht']})
        self.assertEqual(expected.tree, hierarchy.tree)

    def test_to_dataframe(self):
        hierarchy = Hierarchy({'Zuid-Holland': ['Rotterdam', 'Den Haag'],
                               'Noord-Holland': ['Haarlem', 'Amsterdam'],
                               'Utrecht': ['Utrecht'],
                               "Zeeland": []})
        dataframe = pd.DataFrame(hierarchy.tree.iterate_paths(only_leaves=True),
                                 columns=["province", "city"])
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

        result1 = list(hierarchy.tree.iterate_codes(only_leaves=True))
        result2 = list(hierarchy.tree.iterate_codes(only_leaves=False))
        expected1 = ['Rotterdam', 'Den Haag', 'Haarlem']
        expected2 = ['Zuid-Holland', 'Rotterdam', 'Den Haag', 'Noord-Holland', 'Haarlem']
        self.assertEqual(expected1, result1)
        self.assertEqual(expected2, result2)
