from pathlib import Path

from .inputdata import InputData
from .metadata import MetaData
from .table import Table

DEFAULT_STATUS_MARKERS = {
    "SAFE": "S",
    "UNSAFE": "U",
    "PROTECT": "P",
}


class TableData(InputData, Table):
    def __init__(self, dataset, explanatory, response, shadow=None, cost=None, labda=None,
                 total_codes='Total', frequency=None, top_contributors=None,
                 lower_protection_level=None, upper_protection_level=None,
                 status_indicator=None, status_markers=None, **kwargs):
        """
        A TableData instance contains data which has already been aggregated.

        It can be used for tables that are unprotected or partially protected.
        If it's already partially protected, this can be indicated by `status_indicator`.
        """

        Table.__init__(self, explanatory=explanatory, response=response, shadow=shadow, cost=cost, labda=labda)
        InputData.__init__(self, dataset, **kwargs)

        if isinstance(total_codes, str):
            total_code = total_codes
            total_codes = {self.response: total_code}
            for col in self.explanatory:
                total_codes[col] = total_code
        if status_markers is None:
            status_markers = DEFAULT_STATUS_MARKERS
        if top_contributors is None:
            top_contributors = []

        self.total_codes = total_codes
        self.lower_protection_level = lower_protection_level
        self.upper_protection_level = upper_protection_level
        self.frequency = frequency
        self.top_contributors = top_contributors
        self.status_indicator = status_indicator
        self.status_markers = status_markers

    def generate_metadata(self) -> MetaData:
        metadata = super().generate_metadata()
        for col in self.dataset.columns:
            metacol = metadata[col]

            if col in {self.response, self.shadow, self.cost, self.lower_protection_level, self.upper_protection_level}:
                metacol['NUMERIC'] = True
            if col in self.hierarchies:
                metacol["RECODABLE"] = True
                metacol.set_hierarchy(self.hierarchies[col])
            if col in self.codelists:
                metacol["RECODABLE"] = True
                metacol.set_codelist(self.codelists[col])

            total_code = self.total_codes.get(col)
            if total_code:
                metacol['TOTCODE'] = total_code

            if col in self.explanatory:
                metacol["RECODABLE"] = True
            elif col in self.top_contributors:
                metacol["MAXSCORE"] = True
            elif col == self.lower_protection_level:
                metacol['LOWERPL'] = True
            elif col == self.upper_protection_level:
                metacol['UPPERPL'] = True
            elif col == self.frequency:
                metacol['FREQUENCY'] = True
            elif col == self.status_indicator:
                metacol['STATUS'] = True
                metadata.status_markers = self.status_markers

        return metadata

    def to_csv(self, file=None, na_rep=""):
        result = self.dataset.to_csv(file, index=False, header=False, na_rep=na_rep)
        if isinstance(file, (str, Path)):
            self.filepath = Path(file)
        return result
