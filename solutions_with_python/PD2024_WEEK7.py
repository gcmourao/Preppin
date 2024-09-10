import pandas as pd
from Preppin.meta import read_save_files as rsf
from datetime import datetime
import numpy as np
import inflect

p = inflect.engine()


def check_first_valentine(relationship_start, valentine_date):
    valentine_in_first_year_flag = []
    for start_date in relationship_start:
        first_valentine = datetime(start_date.year, valentine_date.month, valentine_date.day)
        if start_date > first_valentine:
            valentine_in_first_year_flag.append("No")
        else:
            valentine_in_first_year_flag.append("Yes")
    return valentine_in_first_year_flag


# import files
couple_df = pd.read_excel(rsf.get_file_path('input_files/',
                                            "PD 2024 Wk7 Valentine's Preppin' Data.xlsx"),
                          sheet_name='Couples')
gifts_df = pd.read_excel(rsf.get_file_path('input_files/',
                                           "PD 2024 Wk7 Valentine's Preppin' Data.xlsx"),
                         sheet_name='Gifts')

# prepare couple_df
couple_df['Relationship Start'] = pd.to_datetime(couple_df['Relationship Start'], format='%B %d, %Y')
date_string = "2024-02-14"
format_string = "%Y-%m-%d"
valentine_day = datetime.strptime(date_string, format_string)
couple_df['Valentine day'] = valentine_day
couple_df['Valentine in first year'] = check_first_valentine(couple_df['Relationship Start'], valentine_day)
couple_df['total_valentines'] = np.where(couple_df['Valentine in first year'] == 'Yes',
                                         couple_df['Valentine day'].dt.year - couple_df[
                                             'Relationship Start'].dt.year + 1,
                                         couple_df['Valentine day'].dt.year - couple_df['Relationship Start'].dt.year)
couple_df['total_valentines_ordinal'] = couple_df['total_valentines'].apply(lambda x: p.ordinal(x))


# merge with gifts_df
final_df = pd.merge(couple_df, gifts_df, left_on='total_valentines_ordinal', right_on='Year', how='left')
final_df.rename(columns={'total_valentines': "Number of Valentine's Day as a Couple"}, inplace=True)
final_df = final_df[["Couple", "Number of Valentine's Day as a Couple", "Gift"]]
# Check solution with the image here: https://preppindata.blogspot.com/2024/02/2024-week-7-valentines-day.html


# save output
final_df.to_csv(rsf.get_file_path('output_files/', 'P2024Week7.csv'), index=False)
