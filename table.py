import pandas as pd
from pandas.core.dtypes.common import is_string_dtype

STATUS_CODES = {
    'S': [1, 2],  # Safe
    'U': [3, 4, 5, 6, 9],  # Unsafe
    'P': [10],  # Protected
    'M': [11, 12],  # Secondary unsafe
    'Z': [13, 14],  # Empty
}


class Table:
    def __init__(self, explanatory, response='<frequency>', name=None, filepath=None,
                 safety_rules=None, suppress_method=None, suppress_method_args=None):

        if name is None:
            name = f'table_{id(self)}'

        self.explanatory = explanatory
        self.response = response
        self.name = name
        self.filepath = filepath
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

    def load_data(self, strip=False):
        df = pd.read_csv(self.filepath)

        if strip:
            strip_whitespace(df, self.explanatory)

        df = df.set_index(self.explanatory)
        safe = self.response
        unsafe = self.response + '_unsafe'
        status_num = 'status_num'
        status_code = 'status_code'

        df.rename(columns={'Status': status_num}, inplace=True)
        df[status_code] = '?'
        for code, nums in STATUS_CODES.items():
            df.loc[df[status_num].isin(nums), status_code] = code

        df[unsafe] = df[safe]
        df.loc[~df[status_code].isin(['S', 'P', 'Z']), safe] = 'x'
        return df


def strip_whitespace(df, explanatories):
    for col in explanatories:
        if is_string_dtype(df[col].dtype):
            df[col] = df[col].map(str.strip)
