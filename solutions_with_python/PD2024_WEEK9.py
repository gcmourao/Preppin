import pandas as pd
from Preppin.meta import read_save_files as rsf
from Preppin.Evaluate.Verify import CompareSolutions


# Read the input files
customer_actions_df = pd.read_excel(rsf.get_file_path('input_files/',
                                                      "PD 2024 Wk9 Input.xlsx"),
                                    sheet_name='Customer Actions')

flight_data_df = pd.read_excel(rsf.get_file_path('input_files/','PD 2024 Wk9 Input.xlsx'),
                               sheet_name='Flight Details')

# Filter cancelled customers:
cancelled_customers_df = customer_actions_df[customer_actions_df['Action'] == 'Cancelled'][['Flight Number',
                                                                                            'Flight Date',
                                                                                            'Customer ID']]
active_customers_df = pd.merge(customer_actions_df, cancelled_customers_df,
                               how='outer', indicator=True).query('_merge == "left_only"').drop(columns=['_merge'])

# Keep last action for each customer
active_customers_df.sort_values(by=['Flight Number', 'Flight Date', 'Customer ID', 'Date'], inplace=True)
last_action_df = active_customers_df.drop_duplicates(subset=['Flight Number', 'Flight Date', 'Customer ID'], keep='last')

# Count number of booked seats per flight
last_action_df.sort_values(by=['Flight Number', 'Flight Date', 'Class', 'Date'], inplace=True)
last_action_df['Total Seats booked over time'] = last_action_df.groupby(['Flight Number',
                                                                         'Flight Date', 'Class']).cumcount() + 1

# Merge with flight information
last_action_df = pd.merge(last_action_df, flight_data_df, how='outer', on=['Flight Number', 'Flight Date', 'Class'])
last_action_df['Total Seats booked over time'].fillna(0, inplace=True)

# Calculate capacity
last_action_df['Capacity %'] = last_action_df['Total Seats booked over time'] / last_action_df['Capacity']

# ------Check output-----
# import official solution
official_solution = pd.read_csv(rsf.get_file_path('official_file_solution/', 'PD 2024 Wk 9 Output.csv'))

# compare results
my_comp = CompareSolutions(last_action_df, official_solution, ['Flight Number', 'Flight Date', 'Class', 'Customer ID'])
my_comp.execute_comparison()

# -----------------------

# Save files
last_action_df.to_csv(rsf.get_file_path('output_files/', 'P2024Week9.csv'), index=False)









