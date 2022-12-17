import pandas as pd

from .tableresult import TableResult

STATUS_CODES = {
    'S': [1, 2],  # Safe
    'U': [3, 4, 5, 6, 9],  # Unsafe
    'P': [10],  # Protected
    'M': [11, 12],  # Secondary unsafe
    'Z': [13, 14],  # Empty
}


class Table:
    def __init__(self, explanatory, response='<frequency>', shadow=None, cost=None, name=None, filepath=None,
                 safety_rules=None, suppress_method=None, suppress_method_args=None):

        if name is None:
            name = f'table_{id(self)}'

        self.explanatory = explanatory
        self.response = response
        self.shadow = shadow or response
        self.cost = cost or response
        self.name = name
        self.filepath_out = filepath
        self.safety_rules = safety_rules
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
        df = pd.read_csv(self.filepath_out, index_col=self.explanatory)
        return TableResult(df, self.response)
