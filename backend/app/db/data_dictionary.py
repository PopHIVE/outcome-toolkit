import numpy as np
import pandas as pd
from typing import Dict


class DataDictionary(object):
    """This class parses the Excel Data Dictionary and into machine readable Dict
    format stored in memory for use when wrapping responses.
    """

    def __init__(self, data_dictionary_path: str):
        self.excel = pd.ExcelFile(data_dictionary_path)
        self.data_dictionary = {
            sheet_name: self.excel.parse(sheet_name).replace({'-': None, np.nan: None})
            for sheet_name in self.excel.sheet_names
        }
        self.mappings = {k: self.generate_mappings(df) for k, df in self.data_dictionary.items()}

    def generate_mappings(self, df: pd.DataFrame) -> Dict[str, Dict[str, str]]:
        """Takes in an excel sheet dataframe and generated a clean-lightweight
        dictionary for easy lookup. Its keyed on the COLUMN field.

        Parameters
        ----------
        df : pd.DataFrame

        Returns
        -------
        Dict[str, Dict[str, str]]

        """

        mappings = {}
        for _, row in df.iterrows():
            mappings[row.COLUMN] = {
                'characteristic': row.CHARACTERISTIC,
                'metric': row.METRIC,
                'label': row.LABEL,
                'display_name': row.DISPLAY_NAME,
                'include': row.INCLUDE,
            }
        return mappings
