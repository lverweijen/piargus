from pathlib import Path

from .inputdata import InputData
from .metadata import MetaData
from .table import Table
from .constants import SAFE, UNSAFE, PROTECTED

DEFAULT_STATUS_MARKERS = {
    "SAFE": SAFE,
    "UNSAFE": UNSAFE,
    "PROTECT": PROTECTED,
}


class TableData(InputData, Table):
    def __init__(
            self,
            dataset,
            explanatory,
            response,
            shadow=None,
            cost=None,
            labda=None,
            total_codes='Total',
            frequency=None,
            top_contributors=None,
            lower_protection_level=None,
            upper_protection_level=None,
            status_indicator=None,
            status_markers=None,
            safety_rules=(),
            apriori=None,
            suppress_method=None,
            suppress_method_args=None,
            **kwargs
    ):
        """
        A TableData instance contains data which has already been aggregated.

        It can be used for tables that are unprotected or partially protected.
        If it's already partially protected, this can be indicated by `status_indicator`.
        Most of the parameters are already explained either in InputData or in Table.

        :param dataset: The dataset containing the table. This dataset should include totals.
        :param explanatory: See Table
        :param response: See Table
        :param shadow: See Table
        :param cost: See Table
        :param labda: See Table
        :param total_codes: Codes within explanatory that are used for the totals.
        :param frequency: See Table
        :param top_contributors: The columns containing top contributions for dominance rule.
        The columns should be in the same order as they appear in the dataset.
        The first of the these columns should describe the highest contribution,
        the second column the second highest contribution.
        :param lower_protection_level: Column that denotes the level below which values are unsafe.
        :param upper_protection_level: Column that denotes the level above which values are unsafe.
        :param status_indicator: Column indicating the status of cells.
        :param status_markers: The meaning of each status.
        Should be dictionary mapping "SAFE", "UNSAFE" and "STATUS" to a code indicating status.
        :param kwargs: See InputData
        """

        Table.__init__(self,
                       explanatory=explanatory,
                       response=response,
                       shadow=shadow,
                       cost=cost,
                       labda=labda,
                       safety_rules=safety_rules,
                       apriori=apriori,
                       suppress_method=suppress_method,
                       suppress_method_args=suppress_method_args)
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
        """Generates a metadata file for tabular data."""
        metadata = super().generate_metadata()
        for col in self.dataset.columns:
            metacol = metadata[col]

            if col in {self.response, self.shadow, self.cost,
                       self.lower_protection_level, self.upper_protection_level}:
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
