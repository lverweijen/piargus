import pandas as pd

from .apriori import Apriori
from .tableresult import TableResult

STATUS_CODES = {
    'S': [1, 2],  # Safe
    'U': [3, 4, 5, 6, 9],  # Unsafe
    'P': [10],  # Protected
    'M': [11, 12],  # Secondary unsafe
    'Z': [13, 14],  # Empty
}


class Table:
    def __init__(self,
                 explanatory,
                 response='<freq>',
                 shadow=None,
                 cost=None,
                 labda=None,
                 name=None,
                 filepath_out=None,
                 safety_rules=None,
                 apriori=None,
                 suppress_method=None,
                 suppress_method_args=None):
        """
        A Tabel instance describes the output of the table.

        A simple table can be created from MicroData.

        Parameters:
        :param explanatory: List of background variables that explain the response. Will be set as a Dataframe-index.
        :param response: The column that needs to be explained.
        :param shadow: The column that is used for the safety rules. Default: response.
        :param cost: The column that contains the cost of suppressing a cell.
        Set to 1 to minimise the number of cells suppressed (although this might suppress totals).
        Default: response.
        :param labda: If set to a value > 0, a box-cox transformation is applied on the cost variable.
        If set to 0, a log transformation is applied on the cost.
        Default: 1.
        :param safety_rules: A set of safety rules.
        Options are:
        - P(p, n) - For p-rule
        - NK(n, k) - Dominance rule
        - ZERO(safety_range)
        - FREQ(minfreq, safety_range)
        - REQ(proc1, proc2, safety_margin)
        See the Tau-Argus manual for details on those rules.
        :param name: Name to use for generated files
        :param filepath_out: Where the file will be located (by default determined from name)
        :param apriori: Apriori file to change parameters
        :param suppress_method: Method to use for secondary suppression.
        Options are:
        - GH: Hypercube
        - MOD: Modular
        - OPT: Optimal
        - NET: Network
        - RND: Controlled rounding
        - CTA: Controlled Tabular Adjustment
        See the Tau-Argus manual for details on those rules.
        :param suppress_method_args: Parameters to pass to suppress_method method.
        """

        if name is None:
            name = f'table_{id(self)}'

        if apriori is not None and not isinstance(apriori, Apriori):
            apriori = Apriori(apriori)

        self.explanatory = explanatory
        self.response = response
        self.shadow = shadow
        self.cost = cost
        self.labda = labda
        self.name = name
        self.filepath_out = filepath_out
        self.safety_rules = safety_rules
        self.apriori = apriori
        self.suppress_method = suppress_method
        self.suppress_method_args = suppress_method_args

    @property
    def safety_rules(self):
        return self._safety_rules

    @safety_rules.setter
    def safety_rules(self, value):
        if value is None:
            value = set()
        elif isinstance(value, str):
            value = set(value.split('|'))
        else:
            value = set(value)

        self._safety_rules = value

    def load_result(self) -> TableResult:
        if self.response == '<freq>':
            response = 'Freq'
        else:
            response = self.response

        df = pd.read_csv(self.filepath_out, index_col=self.explanatory)
        return TableResult(df, response)
