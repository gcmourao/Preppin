import pandas as pd
import numpy as np
from pandas._libs.tslibs.parsing import DateParseError
from datacompy import Compare


class CompareSolutions:
    def __init__(self,
                 my_solution: pd.DataFrame,
                 official_solution: pd.DataFrame,
                 keys: list):
        self.my_solution = my_solution
        self.official_solution = official_solution
        self.keys = keys

    def adjust_float(self):
        for df in [self.official_solution, self.my_solution]:
            for col in df.columns[df.dtypes == 'object']:
                try:
                    df[col] = df[col].astype(np.float64)
                except ValueError:
                    pass

    def adjust_date(self):
        for df in [self.official_solution, self.my_solution]:
            for col in df.columns[df.dtypes == 'object']:
                try:
                    new_dt = pd.to_datetime(df[col], format='%d/%m/%Y').dt.strftime('%d/%m/%Y').to_list()
                    df.loc[col] = new_dt
                except:
                    try:
                        new_dt = pd.to_datetime(df[col], format='%Y-%m-%d').dt.strftime('%Y-%m-%d').to_list()
                        df.loc[col] = new_dt
                    except:
                        try:
                            df[col] = pd.to_datetime(df[col], format='%d/%m/%Y')
                        except:
                            try:
                                df[col] = pd.to_datetime(df[col], format='%Y-%m-%d')
                            except:
                                pass

    def compare_files(self):
        compare = Compare(
            self.my_solution,
            self.official_solution,
            join_columns=self.keys,
            abs_tol=0.001,  # Optional, defaults to 0
            rel_tol=0,  # Optional, defaults to 0
            df1_name='my solution',  # Optional, defaults to 'df1'
            df2_name='official solution'  # Optional, defaults to 'df2'
        )
        print(compare.report())

    def execute_comparison(self):
        self.adjust_float()
        self.adjust_date()
        self.compare_files()
