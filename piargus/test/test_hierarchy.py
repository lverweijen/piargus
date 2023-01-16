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

    def test_item_manipulation(self):
        hierarchy = Hierarchy({
            "Zuid-Holland": ["Rotterdam", "Den Haag"],
            "Noord-Holland": ["Haarlem"]})

        hierarchy['Noord-Holland']["Amsterdam"] = True
        hierarchy['Zuid-Holland']["Den Haag"] = False
        hierarchy['Utrecht'] = True
        hierarchy['Utrecht']['Utrecht'] = True
        hierarchy['Noord-Holland'] = True

        expected = Hierarchy({'Zuid-Holland': ['Rotterdam'],
                              'Noord-Holland': ['Haarlem', 'Amsterdam'],
                              'Utrecht': ['Utrecht']})
        self.assertEqual(expected, hierarchy)

    def test_from_dataframe(self):
        df = pd.DataFrame([
            {"province": "Zuid-Holland", "city": "Rotterdam"},
            {"province": "Zuid-Holland", "city": "Den Haag"},
            {"province": "Noord-Holland", "city": "Haarlem"},
            {"province": "Noord-Holland", "city": "Amsterdam"},
            {"province": "Utrecht", "city": "Utrecht"},
        ])

        hierarchy = Hierarchy.from_dataframe(df)

        expected = Hierarchy({'Zuid-Holland': ['Rotterdam', 'Den Haag'],
                              'Noord-Holland': ['Haarlem', 'Amsterdam'],
                              'Utrecht': ['Utrecht']})
        self.assertEqual(expected, hierarchy)

    def test_to_dataframe(self):
        hierarchy = Hierarchy({'Zuid-Holland': ['Rotterdam', 'Den Haag'],
                               'Noord-Holland': ['Haarlem', 'Amsterdam'],
                               'Utrecht': ['Utrecht'],
                               "Zeeland": []})
        dataframe = hierarchy.to_dataframe(['province', 'city'])
        expected = pd.DataFrame([
            {"province": "Zuid-Holland", "city": "Rotterdam"},
            {"province": "Zuid-Holland", "city": "Den Haag"},
            {"province": "Noord-Holland", "city": "Haarlem"},
            {"province": "Noord-Holland", "city": "Amsterdam"},
            {"province": "Utrecht", "city": "Utrecht"},
            {"province": "Zeeland"},
        ])

        self.assertEqual(expected.to_dict('records'), dataframe.to_dict('records'))

    def test_codes(self):
        hierarchy = Hierarchy({
            "Zuid-Holland": ["Rotterdam", "Den Haag"],
            "Noord-Holland": ["Haarlem"]})

        result1 = list(hierarchy.codes(totals=False))
        result2 = list(hierarchy.codes(totals=True))
        expected1 = ['Rotterdam', 'Den Haag', 'Haarlem']
        expected2 = ['Zuid-Holland', 'Rotterdam', 'Den Haag', 'Noord-Holland', 'Haarlem']
        self.assertEqual(expected1, result1)
        self.assertEqual(expected2, result2)
