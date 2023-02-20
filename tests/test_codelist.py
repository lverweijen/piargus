import os
from unittest import TestCase

from piargus import CodeList


class TestCodeList(TestCase):
    def test_to_cdl(self):
        codelist = CodeList({
            501: "Brielle",
            530: "Hellevoetsluis",
            614: "Westvoorne"})

        result = codelist.to_cdl().replace(os.linesep, "<CR>")
        expected = ('501,Brielle<CR>'
                    '530,Hellevoetsluis<CR>'
                    '614,Westvoorne<CR>')
        self.assertEqual(expected, result)

    def test_repr(self):
        codelist = CodeList({
            501: "Brielle",
            530: "Hellevoetsluis",
            614: "Westvoorne"})

        expected = "CodeList({'501': 'Brielle', '530': 'Hellevoetsluis', '614': 'Westvoorne'})"
        self.assertEqual(expected, repr(codelist))
