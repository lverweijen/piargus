import io
from unittest import TestCase

from piargus import BatchWriter, MetaData


class TestBatchWriter(TestCase):
    def test_writer(self):
        file = io.StringIO()
        writer = BatchWriter(file)
        writer.logbook('log.txt')
        writer.version_info('version.txt')
        writer.open_microdata('microdata.csv')
        writer.open_tabledata('table.csv')
        writer.open_metadata('metadata.rda')
        writer.specify_table(["sbi", "gk"], "income")
        writer.safety_rule({"NK(3, 70)"})
        writer.apriori("apriori.hst", 55, ignore_error=True, expand_trivial=False)
        writer.read_microdata()
        writer.read_table()
        writer.suppress("GH", 1)
        writer.write_table(1, 2, {"AS": True}, "table_clean.csv")
        file.seek(0)
        result = file.readlines()

        expected = [
            '<LOGBOOK>\t"log.txt"\n',
            '<VERSIONINFO>\t"version.txt"\n',
            '<OPENMICRODATA>\t"microdata.csv"\n',
            '<OPENTABLEDATA>\t"table.csv"\n',
            '<OPENMETADATA>\t"metadata.rda"\n',
            '<SPECIFYTABLE>\t"sbi""gk"|"income"||\n',
            '<SAFETYRULE>\tNK(3, 70)\n',
            '<APRIORI>\t"apriori.hst", 55, ",", 1, 0\n',
            '<READMICRODATA>\n',
            '<READTABLE>\n',
            '<SUPPRESS>\tGH(1)\n',
            '<WRITETABLE>\t(1, 2, AS+, "table_clean.csv")\n',
        ]
        self.assertEqual(expected, result)
