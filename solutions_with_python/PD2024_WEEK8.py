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
                new_dict['Benefits'].append(benefit.strip())
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


def create_new_benefit_df(tier, benefits_df):
    scheme_benefit_df = benefits_df[benefits_df['Tier Grouping'] == tier]
    scheme_dict_benefit = {'Tier': scheme_benefit_df['Tier'].to_list(),
                           'Benefits': scheme_benefit_df['Benefits'].to_list()}
    scheme_dict_benefit = expand_benefits(scheme_dict_benefit)
    scheme_dict_benefit = adjust_benefits(scheme_dict_benefit)
    scheme_benefit_df2 = pd.DataFrame.from_dict(scheme_dict_benefit)
    scheme_benefit_df2['scheme_tier'] = str(tier) + ' Tier ' + scheme_benefit_df2['Tier'].apply(str)
    return scheme_benefit_df2


# import files
benefits_df = pd.read_excel(rsf.get_file_path('input_files/',
                                              "PD 2024 Wk8 Prep Air Loyalty.xlsx"),
                            sheet_name='Prep Air Loyalty')
costs_df = pd.read_excel(rsf.get_file_path('input_files/',
                                           "PD 2024 Wk8 Prep Air Loyalty.xlsx"),
                         sheet_name='Costings')
customers_df = pd.read_csv(rsf.get_file_path('input_files/',
                                             'PD 2024 Wk8 Prep Air Updated Customers.csv'))
print(f"customers_df: {customers_df.shape}")


# Filter frequent passengers
customers_df['Last Date Flown'] = pd.to_datetime(customers_df['Last Date Flown'], format='%Y-%m-%d')
customers_df = customers_df[customers_df['Last Date Flown'] >= cut_off_date]


# Number of years as customer and average flights per year
customers_df['First Flight'] = pd.to_datetime(customers_df['First Flight'], format='%Y-%m-%d')
customers_df['Number of Years as Customer'] = (last_day - customers_df['First Flight']).dt.days / 365
customers_df['Number of Years as Customer'] = customers_df['Number of Years as Customer'].apply(np.floor) + 1
customers_df['Avg Flights per Year'] = round(customers_df['Number of Flights'] /
                                             customers_df['Number of Years as Customer'], 4)


# Create bins
scheme5_bin = [0, 5, 10, 15, 20, 25, 30, 1000]
scheme5_label = ['5 Tier 0', '5 Tier 1', '5 Tier 2', '5 Tier 3', '5 Tier 4', '5 Tier 5', '5 Tier 6']
customers_df['binned'] = pd.cut(customers_df['Number of Flights'],
                                bins=scheme5_bin,
                                include_lowest=True,
                                right=False,
                                labels=scheme5_label)
customers_df.rename(columns={'binned': 'scheme5_tier'}, inplace=True)
scheme10_bin = [0, 10, 20, 30, 1000]
scheme10_label = ['10 Tier 0', '10 Tier 1', '10 Tier 2', '10 Tier 3']
customers_df['binned'] = pd.cut(customers_df['Number of Flights'],
                                bins=scheme10_bin,
                                include_lowest=True,
                                right=False,
                                labels=scheme10_label)
customers_df.rename(columns={'binned': 'scheme10_tier'}, inplace=True)


# Summarize data per scheme
sum_list = [[pd.DataFrame(), 'scheme5_tier'], [pd.DataFrame(), 'scheme10_tier']]
for item in sum_list:
    item[0] = customers_df.groupby(by=item[1], as_index=False, observed=False).agg({'Customer ID': 'count',
                                                                                    'Avg Flights per Year': 'mean'})
    item[0].rename(columns={'Customer ID': 'Number of Customers', item[1]: 'scheme_tier'}, inplace=True)
scheme5_df = sum_list[0][0]
scheme10_df = sum_list[1][0]
summarized_scheme_df = pd.concat([scheme5_df, scheme10_df], ignore_index=True)


# Prepare loyalty benefits df for merge
scheme5_benefit_df2 = create_new_benefit_df(5, benefits_df)
scheme10_benefit_df2 = create_new_benefit_df(10, benefits_df)
benefit_df_adj = pd.concat([scheme5_benefit_df2, scheme10_benefit_df2], ignore_index=True)


# Merge program1_df with loyalty_costs_df and loyalty_benefits_df
costs_df.rename(columns={'Benefit': 'Benefits'}, inplace=True)
costs_df['cost_number'] = costs_df['Cost'].str.extract('(\d+)').astype(float)
benefit_df_adj = benefit_df_adj.merge(costs_df, on='Benefits', how='left')


# Merge with summarized df per schema:
benefit_df_adj2 = summarized_scheme_df.merge(benefit_df_adj, on='scheme_tier', how='left')


# Calculate benefit - type: per flight
per_flight_benefit = ['Free Seat Selection', 'First Checked Bag Free', 'First Class Lounge Access',
                      'First Class Lounge Access for 1 Guest']
scheme_benefit_per_flight = benefit_df_adj2[benefit_df_adj2['Benefits'].isin(per_flight_benefit)]
scheme_benefit_per_flight['total_cost'] = (scheme_benefit_per_flight['Number of Customers'] *
                                           scheme_benefit_per_flight['Avg Flights per Year'] *
                                           scheme_benefit_per_flight['cost_number'])


# Calculate benefit - per year
per_year_benefit = ['£250 off a flight each Year']
scheme_benefit_per_year = benefit_df_adj2[benefit_df_adj2['Benefits'].isin(per_year_benefit)]
scheme_benefit_per_year['total_cost'] = (scheme_benefit_per_year['Number of Customers'] *
                                         scheme_benefit_per_year['cost_number'])

# Zero cost
zero_cost = ['Early Seat Selection', 'Priority Bag Drop & Boarding', 'nan']
scheme_benefit_zero = benefit_df_adj2[benefit_df_adj2['Benefits'].isin(zero_cost)]
scheme_benefit_zero.insert(scheme_benefit_zero.shape[1], 'total_cost', 0)


# Append
final_benefit_cost = pd.concat([scheme_benefit_per_flight, scheme_benefit_zero, scheme_benefit_per_year],
                               ignore_index=True)
final_df = final_benefit_cost.groupby(by='scheme_tier',
                                      as_index=False,
                                      observed=False).agg({'Number of Customers': 'max',
                                                           'total_cost': 'sum'})
final_df['total_cost'] = round(final_df['total_cost'], 2)


# Print solution
scheme5 = ['5 Tier 0', '5 Tier 1', '5 Tier 2', '5 Tier 3', '5 Tier 4', '5 Tier 5', '5 Tier 6']
scheme10 = ['10 Tier 0', '10 Tier 1', '10 Tier 2', '10 Tier 3']
print(final_df[final_df['scheme_tier'].isin(scheme5)])
print(final_df[final_df['scheme_tier'].isin(scheme10)])
