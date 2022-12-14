import os
from unittest import TestCase

from hierarchy import Hierarchy


class TestHierarchy(TestCase):
    def test_to_hcr(self):
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
