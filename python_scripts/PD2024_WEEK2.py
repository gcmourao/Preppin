import pandas as pd
import _read_save_files as rsf


def get_stats(group):
    return {'price_median': group.median(), 'price_maximum': group.max(), 'price_minimum': group.min()}


def transpose_df(df, column_name):
    new_df = df.pivot_table(index=['Quarter', 'Flow Card?'], columns='Class', values=column_name).reset_index()
    new_df['Aggregation type'] = column_name.split('_')[1]
    return new_df


# the input files from week 2 are the output files from week 1
input_file_with_card = pd.read_csv(rsf.get_file_path('output_files/', 'P2024Week1_withFlowCard.csv'))
input_file_without_card = pd.read_csv(rsf.get_file_path('output_files/', 'P2024Week1_withoutFlowCard.csv'))

# Concatenate the files
input_file_full = pd.concat([input_file_with_card, input_file_without_card], ignore_index=True)

# Change date to quarter
input_file_full['Quarter'] = pd.to_datetime(input_file_full['Date'], format='%d/%m/%Y').dt.quarter

# Adjust price dtype
input_file_full['Price'] = input_file_full['Price'].str.replace(',', '').astype(float)

# Aggregate data
key = ['Quarter', 'Flow Card?', 'Class']
grouped = input_file_full.groupby(key, as_index=False)['Price']
summarised_data = grouped.apply(get_stats).unstack().reset_index()

# adjusting the classes labels as required
summarised_data['Class'] = summarised_data['Class'].replace({'Economy': 'First Class',
                                                             'First Class': 'Economy',
                                                             'Business Class': 'Premium Economy',
                                                             'Premium Economy': 'Business Class'})

# Summarize the data
df_median = transpose_df(summarised_data, 'price_median')
df_min = transpose_df(summarised_data, 'price_minimum')
df_max = transpose_df(summarised_data, 'price_maximum')
final_df = pd.concat([df_median, df_min, df_max], ignore_index=True)

# check data and the final df size
print(final_df.head(5).T)
print(final_df.shape)

# Save files
final_df.to_csv(rsf.get_file_path('output_files/', 'P2024Week2.csv'), index=False)
