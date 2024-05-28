import pandas as pd
import _read_save_files as rsf


# Import files
input_file_with_card = pd.read_csv(rsf.get_file_path('output_files/', 'P2024Week1_withFlowCard.csv'))
input_file_without_card = pd.read_csv(rsf.get_file_path('output_files/', 'P2024Week1_withoutFlowCard.csv'))
target = pd.DataFrame(columns=['Month', 'Class', 'Target'])
for quarter in ['Q1', 'Q2', 'Q3', 'Q4']:
    quarter_sheet = pd.read_excel(rsf.get_file_path('input_files/', 'PD 2024 Wk 3 Input.xlsx'),
                          sheet_name=quarter)
    target = pd.concat([target, quarter_sheet], ignore_index=True)
print('Check target file size:')
print(target.shape)

# append week1 files
input_file_full = pd.concat([input_file_with_card, input_file_without_card], ignore_index=True)
# Create column for the month
input_file_full['Month'] = pd.to_datetime(input_file_full['Date'], format='%d/%m/%Y').dt.month
# Adjust price dtype
input_file_full['Price'] = input_file_full['Price'].str.replace(',', '').astype(float)
# adjusting the classes labels as required
input_file_full['Class'] = input_file_full['Class'].replace({'Economy': 'First Class',
                                                             'First Class': 'Economy',
                                                             'Business Class': 'Premium Economy',
                                                             'Premium Economy': 'Business Class'})

# Create Class with only first letters to work as key for merging with target data. The requirement is to create this
# variable extracting the first letter of each word in the Class variable.
input_file_full['Class'] = input_file_full['Class'].apply(lambda x: ''.join([i[0] for i in x.split(' ')]))

# Summarize the week1 file
key = ['Month', 'Class']
grouped = input_file_full.groupby(key, as_index=False)['Price'].agg('sum')
grouped.rename(columns={"Price": "Total Price"}, inplace=True)
print('Check summarized file size:')
print(grouped.shape)

# Merge the files
merged_file = pd.merge(grouped, target, on=['Month', 'Class'], how='left')
print('Check final file size:')
print(merged_file.shape)

# Adjust target dtype
merged_file['Target'] = merged_file['Target'].astype(float)
# Create difference to target column
merged_file['Difference to Target'] = merged_file['Target'] - merged_file['Total Price']

# Save file
merged_file.to_csv(rsf.get_file_path('output_files/', 'P2024Week3.csv'), index=False)
