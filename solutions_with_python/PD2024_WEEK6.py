import pandas as pd
from Preppin.meta import read_save_files as rsf
import numpy as np
from Preppin.Evaluate.Verify import CompareSolutions


def create_salary_band(input_df, total_salary_col_name):
    # Create salary band
    input_df['Max Tax Rate'] = np.where(input_df[total_salary_col_name] <= 12570, '0% rate',
                                        np.where(input_df[total_salary_col_name] <= 50270, '20% rate',
                                                 np.where(input_df[total_salary_col_name] <= 125140, '40% rate',
                                                          '45% rate')))
    return input_df


# Import files
input_df = pd.read_csv(rsf.get_file_path('input_files/', 'PD 2024 Wk 6 Input.csv'))
print(f"Salary report input df: {input_df.shape}")
input_df['row_number'] = list(range(1, input_df.shape[0] + 1, 1))
input_df.sort_values(['StaffID', 'row_number'], inplace=True)
input_df.drop_duplicates(['StaffID'], keep='last', inplace=True)
input_df.drop(columns=['row_number'], inplace=True)
input_df_T = pd.melt(input_df, id_vars=['StaffID'])
input_df_T.rename(columns={'variable': 'Month', 'value': 'Salary'}, inplace=True)
input_df_T['Month'] = input_df_T['Month'].astype(np.int64)
input_df_T.sort_values(['StaffID', 'Month'], inplace=True)
salary_report = input_df_T.groupby('StaffID', as_index=False)['Salary'].agg('sum')
salary_report = create_salary_band(salary_report, 'Salary')

# create tax calculation
salary_report['20% rate tax paid'] = 0
salary_report['40% rate tax paid'] = 0
salary_report['45% rate tax paid'] = 0
salary_report["remaining salary"] = salary_report['Salary'] - 12570
salary_report["20% rate tax paid"] = np.where((salary_report['remaining salary'] > 0) &
                                              (salary_report['remaining salary'] <= (50270 - 12570)),
                                              salary_report['remaining salary'] * 0.2, (50270 - 12570) * 0.2)
salary_report["remaining salary"] = salary_report['Salary'] - 50270
salary_report["40% rate tax paid"] = np.where(salary_report['remaining salary'] < 0, 0,
                                              np.where(salary_report['remaining salary'] <= (125140 - 50270),
                                                       salary_report['remaining salary'] * 0.4,
                                                       (125140 - 50270) * 0.4))

salary_report["remaining salary"] = salary_report['Salary'] - 125140
salary_report["45% rate tax paid"] = np.where(salary_report['remaining salary'] > 0,
                                              salary_report['remaining salary'] * 0.45, 0)

salary_report['Total Tax Paid'] = (salary_report['20% rate tax paid'] + salary_report['40% rate tax paid']
                                   + salary_report['45% rate tax paid'])
salary_report.drop(columns=['remaining salary'], inplace=True)

# import official solution
official_solution = pd.read_csv(rsf.get_file_path('official_file_solution/', 'PD 2024 Wk 6 Output.csv'))

# compare results
my_comp = CompareSolutions(salary_report, official_solution, ['StaffID'])
my_comp.execute_comparison()

# Save files
salary_report.to_csv(rsf.get_file_path('output_files/', 'P2024Week6.csv'), index=False)