import pandas as pd
import _read_save_files as rsf
import _geolocation as geo


# Read the data from the challenge file
input_file = pd.read_csv(rsf.get_file_path('input_files/', 'PD 2024 Wk 1 Input.csv'))

# Break 'Flight details' into columns
input_file[['Date', 'Flight Number', 'From-To', 'Class', 'Price']] = (input_file['Flight Details'].
                                                                      str.split('//', expand=True))
input_file[['From', 'To']] = input_file['From-To'].str.split('-', expand=True)
input_file.drop(columns=['Flight Details', 'From-To'], inplace=True)

# adjust date, price format and Flow card
input_file['Date'] = pd.to_datetime(input_file['Date']).dt.strftime('%d/%m/%Y')
input_file['Price'] = input_file['Price'].astype(float).apply(lambda x: '{:,.2f}'.format(x))
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

# Check files. Note that it will have 4 extra columns when compared to the official challenge answer
print(output_has_flow_card.head(4).T)
print(output_has_flow_card.shape)
print(output_no_flow_card.head(4).T)
print(output_no_flow_card.shape)

# Save files
output_has_flow_card.to_csv(rsf.get_file_path('output_files/', 'P2024Week1_withFlowCard.csv'), index=False)
output_no_flow_card.to_csv(rsf.get_file_path('output_files/', 'P2024Week1_withoutFlowCard.csv'), index=False)
