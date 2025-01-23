import os
from typing import Union, Optional, Any
from collections.abc import Sequence, Collection, Iterable, Mapping

import pandas as pd

from .apriori import Apriori
from .safetyrule import make_safety_rule, SafetyRule
from .tableresult import TableResult
from ..constants import FREQUENCY_RESPONSE, OPTIMAL


class Table:
    """
    A Table describes what the protected table should look like.

    Usually there are a few explanatory columns and one response.
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
        recodes: Mapping[str, Union[int, os.PathLike]] = None,
        suppress_method: Optional[str] = OPTIMAL,
        suppress_method_args: Sequence = (),
    ):
        """
        Create a new Table

        :param explanatory: List of background variables that explain the response.
            Will be set as a Dataframe-index.
        :param response: The column that needs to be explained.
        :param shadow: The column that is used for the safety rules. Default: response.
        :param cost: The column that contains the cost of suppressing a cell.
            Set to 1 to minimise the number of cells suppressed (although this might suppress totals).
            Default: response.
        :param labda: If set to a value > 0, a box-cox transformation is applied on the cost variable.
            If set to 0, a log transformation is applied on the cost.
            Default: 1.
        :param safety_rule: A set of safety rules on individual level.
            Can be supplied as:
                * str where parts are separated by |
                * A sequence of parts
                * A dict with keys {"individual": x "holding": y} with separate rules on individual and holding level.

            Each part can be:
                * "P(p, n=1)": p% rule
                * "NK(n, k)": (n, k)-dominance rule
                * "ZERO(safety_range)": Zero rule
                * "FREQ(minfreq, safety_range)": Frequency rule
                * "REQ(percentage_1, percentage_2, safety_margin)": Request rule

            See the Tau-Argus manual for details on those rules.
        :param apriori: Apriori file to change parameters.
        :param recodes: Recoding files that should be applied by TauArgus
            Note that it is also possible to recode in pandas by doing:
            - `df[col].map({old1: A, old2: A})`
            - `df[col].cut(boundaries)`
        :param suppress_method: Method to use for secondary suppression.
            Options are:
                * `GHMITER` ("GH"): Hypercube
                * `MODULAR` ("MOD"): Modular
                * `OPTIMAL` ("OPT"): Optimal [default]
                * `NETWORK` ("NET"): Network
                * `ROUNDING` ("RND"): Controlled rounding
                * `TABULAR_ADJUSTMENT` ("CTA"): Controlled Tabular Adjustment
                * None: No secondary suppression is applied

            See the Tau-Argus manual for details on those rules.
        :param suppress_method_args: Parameters to pass to suppress_method.
        """

        if recodes is None:
            recodes = dict()

        self.explanatory = explanatory
        self.response = response
        self.shadow = shadow
        self.cost = cost
        self.labda = labda
        self.filepath_result = None
        self.safety_rule = safety_rule
        self.apriori = apriori
        self.recodes = recodes
        self.suppress_method = suppress_method
        self.suppress_method_args = suppress_method_args
        self._result = None

    @property
    def safety_rule(self) -> str:
        """What safety rule applies to this table."""
        return self._safety_rule

    @safety_rule.setter
    def safety_rule(self, rule: Union[str, Collection[str], SafetyRule] = ""):
        self._safety_rule = make_safety_rule(rule)

    @property
    def apriori(self) -> Apriori:
        """Apriori settings of this table."""
        return self._apriori

    @apriori.setter
    def apriori(self, value):
        if isinstance(value, os.PathLike):
            value = Apriori.from_hst(value)
        elif not isinstance(value, Apriori):
            value = Apriori(value)
        self._apriori = value

    @property
    def result(self) -> TableResult:
        """Lazy property to load and obtain the result after TauArgus has run."""
        r = self._result
        if not r:
            r = self.load_result()
        return r

    def load_result(self) -> TableResult:
        """After tau argus has run, this obtains the protected data."""
        if self.response == FREQUENCY_RESPONSE:
            response = 'Freq'
        else:
            response = self.response

        df = pd.read_csv(self.filepath_result, index_col=self.explanatory)
        self._result = TableResult(df, response)
        return self._result


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
