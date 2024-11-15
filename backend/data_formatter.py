import pandas as pd

class DataFormatter:
    """
    A class used to format and process transaction data.

    Attributes
    ----------
    _df : pd.DataFrame
        A copy of the DataFrame to be formatted.

    Methods
    -------
    __init__(df_to_format: pd.DataFrame)
        Initializes the DataFormatter with a DataFrame to format.

    get_formatted_df() -> pd.DataFrame
        Returns the formatted DataFrame.

    unbias() -> 'DataFormatter'
        Removes bias by flipping FP to TN, only for 'Bias' rows.

    _unbias_row(row)
        Static method to unbias a single row.

    filter_by(filter_gender: str = None, filter_race: str = None,
     filter_state: str = None) -> 'DataFormatter'
        Filters the DataFrame based on gender, race, or state.

    filter_invalid_transactions() -> 'DataFormatter'
        Creates a new dataset without any rows marked as blocked (i.e. False
        Positive (incorrectly blocked), True Positive (correctly blocked)).

    _clean_data() -> 'DataFormatter'
        Removes any columns with missing values and converts the 'Timestamp'
        column to a datetime object.

    helper_df_to_dict(df_to_convert: pd.DataFrame) -> list[dict]
        Static method to convert a DataFrame to a list of dictionaries.

    _helper_output_df_format() -> tuple[pd.DataFrame, pd.DataFrame]
        Helper function to format the DataFrame for output. Cleans the
        DataFrame, groups the data by date, and aggregates the number of
        transactions and total revenue.

    get_for_display() -> list[dict]
        Formats the data for output, and converts to list of dictionaries.

    get_for_predicting() -> tuple[pd.DataFrame, pd.DataFrame]
        Formats the data for output.
    """
    _df: pd.DataFrame


    def __init__(self, df_to_format: pd.DataFrame):
        self._df = df_to_format.copy()


    def get_formatted_df(self) -> pd.DataFrame:
        return self._df


    def unbias(self) -> 'DataFormatter':
        """Removes bias by flipping FP to TN, only for 'Bias' rows"""
        self._df =  self._df.apply(DataFormatter._unbias_row, axis=1)
        return self


    @staticmethod
    def _unbias_row(row):
        if row['confusion_value'] == 'FP' and row['Bias'] == 1:
            row['confusion_value'] = 'TN'
            row['Bias'] = 0
        return row


    def filter_by(self, filter_gender: str = None, filter_race: str = None, filter_state: str = None) -> 'DataFormatter':
        """Filters the DataFrame based on gender, race, or state."""
        # ---- TODO: remove this code once PR with the updated filtering code is merged
        if filter_gender in ['Female', 'Male', 'Non-Binary', 'Other']:  # Check for Gender
            self._df = self._df[self._df['Gender'] == filter_gender]
        # ----
        # if filter_gender:
        #     # call formatter_gender on self.formatted_df
        # if filter_race:
        #     # call formatter_race on self.formatted_df
        # if filter_state:
        #     # call formatter_state on self.formatted_df
        return self


    def filter_invalid_transactions(self) -> 'DataFormatter':
        """Creates a new dataset without any rows marked as blocked
         (i.e. False Positive (incorrectly blocked),
          True Positive (correctly blocked))
        """
        self._df = self._df[(self._df['confusion_value'] != 'FP') & (self._df['confusion_value'] != 'TP')]
        return self


    def _clean_data(self) -> 'DataFormatter':
        """Remove any columns with missing values
         Convert the 'Timestamp' column to a datetime object."""

        self._df = self._df.dropna(axis=1)
        self._df['Timestamp'] = pd.to_datetime(self._df['Timestamp']).dt.date
        self._df = self._df.rename(columns={'Timestamp': 'date'})
        return self


    @staticmethod
    def helper_df_to_dict(df_to_convert: pd.DataFrame) -> list[dict]:
        """Converts a DataFrame to a list of dictionaries.
        """

        return df_to_convert.to_dict('records')


    @staticmethod
    def helper_datetime_to_string(df_to_convert: pd.DataFrame) -> pd.DataFrame:
        df_to_convert['date'] = pd.to_datetime(df_to_convert['date']).dt.strftime('%Y-%m-%d')
        return df_to_convert

    def _helper_output_df_format(self) -> tuple[pd.DataFrame, pd.DataFrame]:
        """Helper function to format the DataFrame for output.

        This function cleans the DataFrame, groups the data by date, and
        aggregates the number of transactions and total revenue. Making two
        dataframes with only the columns we care about.
        """
        self._clean_data()

        amount_df = self._df.groupby(self._df['date']).agg(
            num_transactions=('Transaction_Amount_USD', 'count')
        ).reset_index()

        count_df = self._df.groupby(self._df['date']).agg(
            revenue=('Transaction_Amount_USD', 'sum')
        ).reset_index()

        return amount_df, count_df


    def get_for_display(self) -> tuple[list[dict], list[dict]]:
        """Formats the data for output, and converts to list of dictionaries."""
        amount_df, count_df = self._helper_output_df_format()
        amount_df = DataFormatter.helper_datetime_to_string(amount_df)
        count_df = DataFormatter.helper_datetime_to_string(count_df)

        display_format = (DataFormatter.helper_df_to_dict(amount_df), DataFormatter.helper_df_to_dict(count_df))

        return display_format


    def get_for_predicting(self) -> tuple[pd.DataFrame, pd.DataFrame]:
        """Formats the data for out."""
        amount_df, count_df = self._helper_output_df_format()

        amount_df.set_index('date', inplace=True)
        count_df.set_index('date', inplace=True)

        return amount_df, count_df
