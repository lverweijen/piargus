import warnings
from typing import Union, Optional, Sequence, Collection, Iterable, Any, Mapping

import pandas as pd

from .apriori import Apriori
from .constants import FREQUENCY_RESPONSE, OPTIMAL
from .graphrecode import GraphRecode
from .safetyrule import make_safety_rule
from .tableresult import TableResult


class Table:
    def __init__(
        self,
        explanatory: Sequence[str],
        response: Union[str, int] = FREQUENCY_RESPONSE,
        shadow: Optional[str] = None,
        cost: Optional[Union[int, str]] = None,
        labda: int = None,
        name: str = None,  # Deprecated
        safety_rule: Union[str, Collection[str], Mapping[str, Collection[str]]] = (),
        safety_rules=None,  # Deprecated
        safety_rules_holding=None,  # Deprecated
        apriori: Union[Apriori, Iterable[Sequence[Any]]] = (),
        recodes: Mapping[str, Union[int, GraphRecode]] = None,
        suppress_method: Optional[str] = OPTIMAL,
        suppress_method_args: Sequence = (),
    ):
        """
        A Table instance describes the output of the table.

        A simple table can be created from MicroData.

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
        :param name: (unused)
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

        if name is not None:
            warnings.warn("name is deprecated, pass a dict to Job instead")

        if not isinstance(apriori, Apriori):
            apriori = Apriori(apriori)

        if recodes:
            recodes = {col: (recode if isinstance(recode, (int, GraphRecode))
                             else GraphRecode(recode))
                       for col, recode in recodes.items()}
        else:
            recodes = dict()

        if safety_rules is not None:
            warnings.warn("safety_rules is deprecated, use safety_rule instead")
            safety_rule = safety_rules

        if safety_rules_holding is not None:
            warnings.warn("safety_rules_holding is deprecated"
                          'use safety_rule={'
                          '"individual": individual_rules, '
                          '"holding": holding_rules} instead')
            safety_rule = make_safety_rule(safety_rule, safety_rules_holding)

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
        return self._safety_rule

    @safety_rule.setter
    def safety_rule(self,
                    value: Union[str, Collection[str], Mapping[str, Union[str, Collection[str]]]]):
        if isinstance(value, str):
            self._safety_rule = value
        elif isinstance(value, dict):
            self._safety_rule = make_safety_rule(**value)
        else:
            self._safety_rule = "|".join(value)

    def load_result(self) -> TableResult:
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
