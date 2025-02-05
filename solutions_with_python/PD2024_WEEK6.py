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


def calculate_remaining_salary_to_tax(input_df, salary_column_name, cap):
    input_df["remaining_salary"] = np.where(input_df[salary_column_name] > cap, input_df[salary_column_name] - cap, 0)
    return input_df


def define_salary_to_tax_by_cap(input_df, salary_column_name, cap_start, cap_end):
    input_df = calculate_remaining_salary_to_tax(input_df, salary_column_name, cap_start)
    if cap_end in (np.inf, np.NAN):
        input_df["taxable_salary"] = np.where(input_df[salary_column_name] > cap_start,
                                              input_df["remaining_salary"], 0)
    else:
        input_df["taxable_salary"] = np.where(input_df[salary_column_name] > cap_end, (cap_end - cap_start),
                                              input_df["remaining_salary"])
    return input_df


# Import files
input_salaries = pd.read_csv(rsf.get_file_path('input_files/', 'PD 2024 Wk6 Input.csv'))
print(f"Salary report input df: {input_salaries.shape}")

# Adjust salary
input_salaries['row_number'] = list(range(1, input_salaries.shape[0] + 1, 1))
input_salaries.sort_values(['StaffID', 'row_number'], inplace=True)
input_salaries.drop_duplicates(['StaffID'], keep='last', inplace=True)
input_salaries.drop(columns=['row_number'], inplace=True)
input_salaries_T = pd.melt(input_salaries, id_vars=['StaffID'])
input_salaries_T.rename(columns={'variable': 'Month', 'value': 'Salary'}, inplace=True)
input_salaries_T['Month'] = input_salaries_T['Month'].astype(np.int64)
input_salaries_T.sort_values(['StaffID', 'Month'], inplace=True)

# Calculate yearly salary
salary_report = input_salaries_T.groupby('StaffID', as_index=False)['Salary'].agg('sum')
salary_report = create_salary_band(salary_report, 'Salary')

# Calculate tax paid
salary_report['20% rate tax paid'] = define_salary_to_tax_by_cap(salary_report, 'Salary',
                                                                 12570, 50270)["taxable_salary"] * 0.2
salary_report['40% rate tax paid'] = define_salary_to_tax_by_cap(salary_report, 'Salary',
                                                                 50270, 125140)["taxable_salary"] * 0.4
salary_report['45% rate tax paid'] = define_salary_to_tax_by_cap(salary_report, 'Salary',
                                                                 125140, np.inf)["taxable_salary"] * 0.45

# import official solution
official_solution = pd.read_csv(rsf.get_file_path('official_file_solution/', 'PD 2024 Wk 6 Output.csv'))

# compare results
my_comp = CompareSolutions(salary_report, official_solution, ['StaffID'])
my_comp.execute_comparison()

# Save files
salary_report.to_csv(rsf.get_file_path('output_files/', 'P2024Week6.csv'), index=False)
