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
    def status_num(self):
        return self._df['Status']

    def make_safe(self, marker='x'):
        safe = self.unsafe.copy()
        status_code = self.get_status_code()
        safe[~status_code.isin(['S', 'P', 'Z'])] = marker
        return safe

    def get_status_code(self):
        status_code = pd.Series('?', index=self.status_num.index)
        for code, nums in STATUS_CODES.items():
            status_code[self.status_num.isin(nums)] = code

        return status_code

    def __str__(self):
        return f"Response: {self.response}\n{self.dataframe()}"

    def dataframe(self):
        return pd.DataFrame({
            'safe': self.make_safe(),
            'status': self.get_status_code(),
            'unsafe': self.unsafe})
