from typing import Dict, Collection
from typing import Optional, Sequence, Iterable, Union, Any

from .hierarchy import Hierarchy
from .inputdata import InputData
from ..constants import SAFE, UNSAFE, PROTECTED, OPTIMAL
from ..outputspec import Table, Apriori

DEFAULT_STATUS_MARKERS = {
    "SAFE": SAFE,
    "UNSAFE": UNSAFE,
    "PROTECT": PROTECTED,
}


class TableData(InputData, Table):
    """
    A TableData instance contains data that has already been aggregated.

    It can be used for tables that are unprotected or partially protected.
    If it's already partially protected, this can be indicated by `status_indicator`.
    Most of the parameters are already explained either in InputData or in Table.
    """
    def __init__(
        self,
        dataset,
        explanatory: Sequence[str],
        response: str,
        shadow: Optional[str] = None,
        cost: Optional[str] = None,
        labda: Optional[int] = None,
        *,
        hierarchies: Dict[str, Hierarchy] = None,
        total_codes: Union[str, Dict[str, str]] = None,
        frequency: Optional[str] = None,
        top_contributors: Sequence[str] = (),
        lower_protection_level: Optional[str] = None,
        upper_protection_level: Optional[str] = None,
        status_indicator: Optional[str] = None,
        status_markers: Optional[Dict[str, str]] = None,
        safety_rule: Union[str, Collection[str]] = (),
        apriori: Union[Apriori, Iterable[Sequence[Any]]] = (),
        suppress_method: Optional[str] = OPTIMAL,
        suppress_method_args: Sequence[Any] = (),
        **kwargs
    ):
        """
        Initialize a TableData instance.

        :param dataset: The dataset containing the table. This dataset should include totals.
        :param explanatory: See Table.
        :param response: See Table.
        :param shadow: See Table.
        :param cost: See Table.
        :param labda: See Table.
        :param total_codes: Codes within explanatory that are used for the totals.
        :param frequency: Column containing number of contributors to this cell.
        :param top_contributors: The columns containing top contributions for dominance rule.
            The columns should be in the same order as they appear in the dataset.
            The first of the these columns should describe the highest contribution,
            the second column the second-highest contribution.
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
                       safety_rule=safety_rule,
                       apriori=apriori,
                       suppress_method=suppress_method,
                       suppress_method_args=suppress_method_args)

        InputData.__init__(self, dataset, hierarchies=hierarchies, total_codes=total_codes, **kwargs)

        if status_markers is None:
            status_markers = DEFAULT_STATUS_MARKERS

        self.lower_protection_level = lower_protection_level
        self.upper_protection_level = upper_protection_level
        self.frequency = frequency
        self.top_contributors = top_contributors
        self.status_indicator = status_indicator
        self.status_markers = status_markers

    def _write_data(self, file=None):
        return self._dataset.to_csv(file, index=False, header=False, na_rep="")

    def _write_metadata(self, file):
        """Generates a metadata file for tabular data."""

        file.write(f'\t<SEPARATOR> {self.separator}\n')

        if self.status_indicator:
            for status, marker in self.status_markers.items():
                file.write(f'\t<{status}> {marker}\n')

        for name, col in self._columns.items():
            col.write_metadata(file, include_length=False)

            if name in self.top_contributors:
                file.write("<\tMAXSCORE>\n")
            if name == self.lower_protection_level:
                file.write('\t<LOWERPL>\n')
            if name == self.upper_protection_level:
                file.write('\t<UPPERPL>\n')
            if name == self.frequency:
                file.write('\t<FREQUENCY>\n')
            if name == self.status_indicator:
                file.write('\t<STATUS>\n')
