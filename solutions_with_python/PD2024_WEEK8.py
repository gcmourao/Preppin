import pandas as pd
from Preppin.meta import read_save_files as rsf
from datetime import datetime
import re
import numpy as np

cut_off_date = datetime(2023, 2, 21)
last_day = datetime(2024, 2, 21)


def adjust_benefits(benefit_dict):
    new_dict = {'Tier': [], 'Benefits': []}
    for i in range(0, len(benefit_dict['Tier'])):
        if re.search(",", str(benefit_dict['Benefits'][i])) is not None:
            benefit_adj = re.split(",", benefit_dict['Benefits'][i])
            for benefit in benefit_adj:
                new_dict['Tier'].append(benefit_dict['Tier'][i])
                new_dict['Benefits'].append(benefit)
        else:
            if benefit_dict['Tier'][i] == 0:
                new_dict['Tier'].append(benefit_dict['Tier'][i])
                new_dict['Benefits'].append(str(benefit_dict['Benefits'][i]))
            elif str(benefit_dict['Benefits'][i]) != 'nan':
                new_dict['Tier'].append(benefit_dict['Tier'][i])
                new_dict['Benefits'].append(benefit_dict['Benefits'][i])
    return new_dict


def expand_benefits(benefit_dict):
    new_dict = {'Tier': [], 'Benefits': []}
    for i in range(0, len(benefit_dict['Tier'])):
        if i == 0:
            new_dict['Tier'].append(i)
            new_dict['Benefits'].append(benefit_dict['Benefits'][i])
        else:
            for j in reversed(range(0, i + 1)):
                new_dict['Tier'].append(i)
                new_dict['Benefits'].append(benefit_dict['Benefits'][j])
    return new_dict


# import files
loyalty_benefits_df = pd.read_excel(rsf.get_file_path('input_files/',
                                                      "PD 2024 Wk8 Prep Air Loyalty.xlsx"),
                                    sheet_name='Prep Air Loyalty')
loyalty_costs_df = pd.read_excel(rsf.get_file_path('input_files/',
                                                   "PD 2024 Wk8 Prep Air Loyalty.xlsx"),
                                 sheet_name='Costings')
customers_df = pd.read_csv(rsf.get_file_path('input_files/',
                                             'PD 2024 Wk8 Prep Air Updated Customers.csv'))
print(f"customers_df: {customers_df.shape}")

# Filter frequent passengers
customers_df['Last Date Flown'] = pd.to_datetime(customers_df['Last Date Flown'], format='%Y-%m-%d')
customers_df = customers_df[customers_df['Last Date Flown'] >= cut_off_date]

# Number of years as customer
customers_df['First Flight'] = pd.to_datetime(customers_df['First Flight'], format='%Y-%m-%d')
customers_df['Number of Years as Customer'] = (last_day - customers_df['First Flight']).dt.days / 365
customers_df['Number of Years as Customer'] = customers_df['Number of Years as Customer'].apply(np.floor) + 1
customers_df['Avg Flights per Year'] = round(
    customers_df['Number of Flights'] / customers_df['Number of Years as Customer'], 4)

# Create bins
scheme1_bin = [0, 5, 10, 15, 20, 25, 30, 1000]
scheme1_label = ['5 Tier 0', '5 Tier 1', '5 Tier 2', '5 Tier 3', '5 Tier 4', '5 Tier 5', '5 Tier 6']
customers_df['binned'] = pd.cut(customers_df['Number of Flights'], bins=scheme1_bin, include_lowest=True, right=False,
                                labels=scheme1_label)
customers_df.rename(columns={'binned': 'scheme5_tier'}, inplace=True)
scheme2_bin = [0, 10, 20, 30, 1000]
scheme2_label = ['10 Tier 0', '10 Tier 1', '10 Tier 2', '10 Tier 3']
customers_df['binned'] = pd.cut(customers_df['Number of Flights'], bins=scheme2_bin, include_lowest=True, right=False,
                                labels=scheme2_label)
customers_df.rename(columns={'binned': 'scheme10_tier'}, inplace=True)

# Summarize program 1 data
my_list = [[pd.DataFrame(), 'scheme5_tier'], [pd.DataFrame(), 'scheme10_tier']]
for item in my_list:
    item[0] = customers_df.groupby(by=item[1], as_index=False, observed=False).agg({'Customer ID': 'count',
                                                                                    'Avg Flights per Year': 'mean'})
    item[0].rename(columns={'Customer ID': 'Number of Customers', item[1]: 'scheme_tier'}, inplace=True)
scheme5_df = my_list[0][0]
scheme10_df = my_list[1][0]

# Prepare loyalty benefits df for merge
scheme5_benefit_df = loyalty_benefits_df[loyalty_benefits_df['Tier Grouping'] == 5]
scheme5_dict_benefit = {'Tier': scheme5_benefit_df['Tier'].to_list(),
                        'Benefits': scheme5_benefit_df['Benefits'].to_list()}
scheme5_dict_benefit = expand_benefits(scheme5_dict_benefit)
scheme5_dict_benefit = adjust_benefits(scheme5_dict_benefit)
scheme5_benefit_df2 = pd.DataFrame.from_dict(scheme5_dict_benefit)
scheme5_benefit_df2['scheme_tier'] = '5 Tier ' + scheme5_benefit_df2['Tier'].apply(str)
scheme10_benefit_df = loyalty_benefits_df[loyalty_benefits_df['Tier Grouping'] == 10]
scheme10_dict_benefit = {'Tier': scheme10_benefit_df['Tier'].to_list(),
                         'Benefits': scheme10_benefit_df['Benefits'].to_list()}
scheme10_dict_benefit = expand_benefits(scheme10_dict_benefit)
scheme10_dict_benefit = adjust_benefits(scheme10_dict_benefit)
scheme10_benefit_df2 = pd.DataFrame.from_dict(scheme10_dict_benefit)
scheme10_benefit_df2['scheme_tier'] = '10 Tier ' + scheme10_benefit_df2['Tier'].apply(str)

# Merge program1_df with loyalty_costs_df and loyalty_benefits_df
loyalty_costs_df.rename(columns={'Benefit': 'Benefits'}, inplace=True)
loyalty_costs_df['cost_number'] = loyalty_costs_df['Cost'].str.extract('(\d+)')
loyalty_costs_df['cost_number'] = loyalty_costs_df['cost_number'].apply(float)

scheme5_benefit_df2 = scheme5_benefit_df2.merge(loyalty_costs_df, on='Benefits', how='left')
scheme10_benefit_df2 = scheme10_benefit_df2.merge(loyalty_costs_df, on='Benefits', how='left')

# Merge with summarized df per schema:
scheme5_benefit_df2 = scheme5_df.merge(scheme5_benefit_df2, on='scheme_tier', how='left')
scheme10_benefit_df2 = scheme10_df.merge(scheme10_benefit_df2, on='scheme_tier', how='left')

# Calculate benefit - type: per flight
per_flight_benefit = ['Free Seat Selection', 'First Checked Bag Free', 'First Class Lounge Access',
                      'First Class Lounge Access for 1 Guest']
scheme5_benefit_per_flight = scheme5_benefit_df2[scheme5_benefit_df2['Benefits'].isin(per_flight_benefit)]
scheme5_benefit_per_flight['total_cost'] = (scheme5_benefit_per_flight['Number of Customers'] *
                                            scheme5_benefit_per_flight['Avg Flights per Year'] *
                                            scheme5_benefit_per_flight['cost_number'])

scheme10_benefit_per_flight = scheme10_benefit_df2[scheme10_benefit_df2['Benefits'].isin(per_flight_benefit)]
scheme10_benefit_per_flight['total_cost'] = (scheme10_benefit_per_flight['Number of Customers'] *
                                             scheme10_benefit_per_flight['Avg Flights per Year'] *
                                             scheme10_benefit_per_flight['cost_number'])

# Calculate benefit - per year
per_year_benefit = ['£250 off a flight each Year']
scheme5_benefit_per_year = scheme5_benefit_df2[scheme5_benefit_df2['Benefits'].isin(per_year_benefit)]
scheme5_benefit_per_year['total_cost'] = (scheme5_benefit_per_year['Number of Customers'] *
                                          scheme5_benefit_per_year['cost_number'])
scheme10_benefit_per_year = scheme10_benefit_df2[scheme10_benefit_df2['Benefits'].isin(per_year_benefit)]
scheme10_benefit_per_year['total_cost'] = (scheme10_benefit_per_year['Number of Customers'] *
                                           scheme10_benefit_per_year['cost_number'])

# Zero cost
zero_cost = ['Early Seat Selection', 'Priority Bag Drop & Boarding']
scheme5_benefit_zero = scheme5_benefit_df2[scheme5_benefit_df2['Benefits'].isin(zero_cost)]
scheme5_benefit_zero['total_cost'] = 0
scheme10_benefit_zero = scheme10_benefit_df2[scheme10_benefit_df2['Benefits'].isin(zero_cost)]
scheme10_benefit_zero['total_cost'] = 0

# Append
scheme5_all = pd.concat([scheme5_benefit_per_flight, scheme5_benefit_zero, scheme5_benefit_per_year], ignore_index=True)
scheme5_final = scheme5_all.groupby(by='scheme_tier', as_index=False, observed=False).agg({'Number of Customers': 'max',
                                                                                           'total_cost': 'sum'})
scheme5_final['total_cost'] = round(scheme5_final['total_cost'], 2)
scheme10_all = pd.concat([scheme10_benefit_per_flight, scheme10_benefit_zero, scheme10_benefit_per_year],
                         ignore_index=True)
scheme10_final = scheme10_all.groupby(by='scheme_tier', as_index=False, observed=False).agg(
    {'Number of Customers': 'max',
     'total_cost': 'sum'})
scheme10_final['total_cost'] = round(scheme10_final['total_cost'], 2)
print(scheme5_final)
print(scheme10_final)
