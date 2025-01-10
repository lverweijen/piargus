from typing import Union, Optional, Sequence, Collection, Iterable, Any, Mapping

import pandas as pd

from .apriori import Apriori
from .safetyrule import make_safety_rule, SafetyRule
from ..result.tableresult import TableResult
from .treerecode import TreeRecode
from ..constants import FREQUENCY_RESPONSE, OPTIMAL


class Table:
    """
    A Table describes what the protected table should look like.

    Usually there is are a few explanatory columns one one response.
    """
    def __init__(
        self,
        explanatory: Sequence[str],
        response: Union[str, int] = FREQUENCY_RESPONSE,
        shadow: Optional[str] = None,
        cost: Optional[Union[int, str]] = None,
        labda: int = None,
        safety_rule: Union[str, Collection[str], SafetyRule] = (),
        apriori: Union[Apriori, Iterable[Sequence[Any]]] = (),
        recodes: Mapping[str, Union[int, TreeRecode]] = None,
        suppress_method: Optional[str] = OPTIMAL,
        suppress_method_args: Sequence = (),
    ):
        """
        Create a new Table

        Parameters:
        :param explanatory: List of background variables that explain the response.
        Will be set as a Dataframe-index.
        :param response: The column that needs to be explained.
        :param shadow: The column that is used for the safety rules. Default: response.
        :param cost: The column that contains the cost of suppressing a cell.
        Set to 1 to minimise the number of cells suppressed (although this might suppress totals).
        Default: response.
        :param labda: If set to a value > 0, a box-cox transformation is applied on the cost
        variable.
        If set to 0, a log transformation is applied on the cost.
        Default: 1.
        :param safety_rule: A set of safety rules on individual level.
        Can be supplied as:
        - str where parts are separated by |
        - A sequence of parts
        - A dict with keys {"individual": x "holding": y} with separate rules on individual and
        holding level .
        Each part can be:
        - "P(p, n=1)": p% rule
        - "NK(n, k)": (n, k)-dominance rule
        - "ZERO(safety_range)": Zero rule
        - "FREQ(minfreq, safety_range)": Frequency rule
        - "REQ(percentage_1, percentage_2, safety_margin)": Request rule
        See the Tau-Argus manual for details on those rules.
        :param apriori: Apriori file to change parameters
        :param suppress_method: Method to use for secondary suppression.
        Options are:
        - `GHMITER` ("GH"): Hypercube
        - `MODULAR` ("MOD"): Modular
        - `OPTIMAL` ("OPT"): Optimal [default]
        - `NETWORK` ("NET"): Network
        - `ROUNDING` ("RND"): Controlled rounding
        - `TABULAR_ADJUSTMENT` ("CTA"): Controlled Tabular Adjustment
        - None: No secondary suppression is applied
        See the Tau-Argus manual for details on those rules.
        :param suppress_method_args: Parameters to pass to suppress_method.
        """

        if recodes:
            recodes = {col: (recode if isinstance(recode, (int, TreeRecode))
                             else TreeRecode(recode))
                       for col, recode in recodes.items()}
        else:
            recodes = dict()

        self.explanatory = explanatory
        self.response = response
        self.shadow = shadow
        self.cost = cost
        self.labda = labda
        self.filepath_out = None
        self.safety_rule = safety_rule
        self.apriori = apriori
        self.recodes = recodes
        self.suppress_method = suppress_method
        self.suppress_method_args = suppress_method_args

    @property
    def safety_rule(self) -> str:
        """What safety rule applies to this table."""
        return self._safety_rule

    @safety_rule.setter
    def safety_rule(self, rule: Union[str, Collection[str], SafetyRule] = ""):
        self._safety_rule = make_safety_rule(rule)

    @property
    def apriori(self):
        """Apriori settings of this table."""
        return self._apriori

    @apriori.setter
    def apriori(self, value):
        if not isinstance(value, Apriori):
            value = Apriori(value)
        self._apriori = value

    def load_result(self) -> TableResult:
        """After tau argus has run, this obtains the protected data."""
        if self.response == FREQUENCY_RESPONSE:
            response = 'Freq'
        else:
            response = self.response

        df = pd.read_csv(self.filepath_out, index_col=self.explanatory)
        return TableResult(df, response)

    def find_variables(self, categorical=True, numeric=True):
        if categorical:
            yield from self.explanatory
            yield from self.recodes.keys()

        if numeric:
            if self.response != FREQUENCY_RESPONSE:
                yield self.response
            if self.shadow:
                yield self.shadow
            if self.cost and isinstance(self.cost, str):
                yield self.cost
