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

    def unsafe(self):
        return self._df[self._response]

    def status(self, recode=True):
        status_num = self._df['Status']

        if recode:
            status_code = pd.Series('?', index=status_num.index, name='status')
            for code, nums in STATUS_CODES.items():
                status_code[status_num.isin(nums)] = code
            return status_code
        else:
            return status_num

    def safe(self, unsafe_marker='x'):
        safe = self._df[self._response].copy()
        status = self._df['Status']
        suppress = status.isin(STATUS_CODES['U']) | status.isin(STATUS_CODES['M'])
        safe[suppress] = unsafe_marker
        return safe

    def __str__(self):
        return f"Response: {self._response}\n{self.dataframe()}"

    def dataframe(self):
        return pd.DataFrame({
            'safe': self.safe(),
            'status': self.status(),
            'unsafe': self.unsafe()})
