import pandas as pd


STATUS_CODES = {
    'S': [1, 2],  # Safe
    'U': [3, 4, 5, 6, 9],  # Unsafe
    'P': [10],  # Protected
    'M': [11, 12],  # Secondary unsafe
    'Z': [13, 14],  # Empty
}


class TableResult:
    def __init__(self, df, response):
        self._df = df
        self._response = response

    @property
    def response(self):
        return self._response

    @property
    def unsafe(self):
        return self._df[self._response]

    @property
    def safe(self):
        if 'safe' not in self._df.columns:
            self._df['safe'] = self.unsafe
            self._df.loc[~self.status_code.isin(['S', 'P', 'Z']), 'safe'] = 'x'
        return self._df['safe']

    @property
    def status_num(self):
        return self._df['Status']

    @property
    def status_code(self):
        if 'status_code' not in self._df.columns:
            self._df['status_code'] = '?'
            for code, nums in STATUS_CODES.items():
                self._df.loc[self.status_num.isin(nums), 'status_code'] = code

        return self._df['status_code']

    def __str__(self):
        return f"Response: {self.response}\n{self.dataframe()}"

    def dataframe(self):
        return pd.DataFrame({
            'safe': self.safe,
            'status_code': self.status_code,
            'unsafe': self.unsafe})
