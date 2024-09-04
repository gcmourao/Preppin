import pandas as pd
from Preppin.meta import read_save_files as rsf
from Preppin.meta import geolocation as geo
from Preppin.Evaluate.Verify import CompareSolutions


# Read the data from the challenge file
input_file = pd.read_csv(rsf.get_file_path('input_files/', 'PD 2024 Wk 1 Input.csv'))


# Break 'Flight details' into columns
input_file[['Date', 'Flight Number', 'From-To', 'Class', 'Price']] = (input_file['Flight Details'].
                                                                      str.split('//', expand=True))
input_file[['From', 'To']] = input_file['From-To'].str.split('-', expand=True)
input_file.drop(columns=['Flight Details', 'From-To'], inplace=True)


# adjust date, price format and Flow card
input_file['Date'] = pd.to_datetime(input_file['Date']).dt.strftime('%d/%m/%Y')
input_file['Price'] = input_file['Price'].astype(float)
input_file['Flow Card?'] = input_file['Flow Card?'].replace({1: 'Yes', 0: 'No'})


# reorder the columns
input_file = input_file[['Date', 'Flight Number', 'From', 'To', 'Class', 'Price', 'Flow Card?', 'Bags Checked',
                         'Meal Type']]


# Extra step for visualization in tableau
cities = input_file["From"].unique()
input_file = geo.input_geolocation(cities, input_file, 'From')
input_file = geo.input_geolocation(cities, input_file, 'To')


# Creating output files
output_has_flow_card = input_file[input_file['Flow Card?'] == 'Yes']
output_no_flow_card = input_file[input_file['Flow Card?'] == 'No']


# Check solution
os_flow_card = pd.read_csv(rsf.get_file_path(
    'official_file_solution/', 'PD 2024 Wk 1 Output Flow Card.csv'))
os_no_flow_card = pd.read_csv(rsf.get_file_path(
    'official_file_solution/', 'PD 2024 Wk 1 Output Non-Flow Card.csv'))
my_flow_card = output_has_flow_card.drop(columns=['From latitude', 'To latitude', 'From longitude', 'To longitude'])
my_no_flow_card = output_no_flow_card.drop(columns=['From latitude', 'To latitude', 'From longitude', 'To longitude'])
my_comp1 = CompareSolutions(os_flow_card, my_flow_card, ['Date', 'Flight Number'])
my_comp1.execute_comparison()
my_comp2 = CompareSolutions(os_no_flow_card, my_no_flow_card, ['Date', 'Flight Number'])
my_comp2.execute_comparison()


# Save files
output_has_flow_card.to_csv(rsf.get_file_path('output_files/', 'P2024Week1_withFlowCard.csv'),
                            index=False)
output_no_flow_card.to_csv(rsf.get_file_path('output_files/', 'P2024Week1_withoutFlowCard.csv'),
                           index=False)
