import pandas as pd

from ..constants import SAFE, UNSAFE, PROTECTED, SUPPRESSED, EMPTY


STATUS_CODES = {
    SAFE: [1, 2],
    UNSAFE: [3, 4, 5, 6, 9],
    PROTECTED: [10],
    SUPPRESSED: [11, 12],
    EMPTY: [13, 14],
}


class TableResult:
    def __init__(self, df, response):
        self._df = df
        self._response = response

    def unsafe(self) -> pd.Series:
        """Return the unsafe original response.

        :returns: The raw unprotected totals as a series.
        """
        return self._df[self._response]

    def status(self, recode=True) -> pd.Series:
        """Return the status of each response.

        :param recode: If True, readable codes will be returned.
        S - safe
        P - protected
        U - primary unsafe
        M - secondary unsafe
        Z - empty
        Otherwise raw status codes from Tau-Argus are returned. See the documentation of Tau-Argus.
        :returns: Status for each combination.
        """
        status_num = self._df['Status']

        if recode:
            status_code = pd.Series('?', index=status_num.index, name='status')
            for code, nums in STATUS_CODES.items():
                status_code[status_num.isin(nums)] = code
            return status_code
        else:
            return status_num

    def safe(self, unsafe_marker='x') -> pd.Series:
        """Return the (safe) totals of the response.

        :param unsafe_marker: The marker to shield unsafe values
        :returns: The totals of the response as a Series
        """
        safe = self._df[self._response].copy()
        status = self._df['Status']
        suppress = status.isin(STATUS_CODES[UNSAFE]) | status.isin(STATUS_CODES[SUPPRESSED])
        safe[suppress] = unsafe_marker
        return safe

    def __str__(self):
        return f"Response: {self._response}\n{self.dataframe()}"

    def dataframe(self) -> pd.DataFrame:
        """Combines safe, status and unsafe in a dataframe."""
        return pd.DataFrame({
            'safe': self.safe(),
            'status': self.status(),
            'unsafe': self.unsafe(),
        })
