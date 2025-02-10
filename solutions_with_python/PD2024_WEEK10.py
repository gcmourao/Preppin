import pandas as pd
from Preppin.meta import read_save_files as rsf
import numpy as np
from Preppin.Evaluate.Verify import CompareSolutions


def rearrange_name(full_name):
    surname, name = full_name.split(',')
    return f"{name.strip().capitalize()} {surname.strip().capitalize()}"


map_loyalty_tier = {'Bronze': 'Bronze',
                    'Bronz': 'Bronze',
                    'bronze': 'Bronze',
                    'Silver': 'Silver',
                    'Sliver': 'Silver',
                    'silver': 'Silver',
                    'Gold': 'Gold',
                    'Goald': 'Gold',
                    'gold': 'Gold'}


# read file
transaction_df = pd.read_excel(rsf.get_file_path('input_files/', 'PD 2024 Wk10 Input.xlsx'),
                               sheet_name='Transaction Data')
product_df = pd.read_excel(rsf.get_file_path('input_files/', 'PD 2024 Wk10 Input.xlsx'),
                           sheet_name='Product Table')
loyalty_df = pd.read_excel(rsf.get_file_path('input_files/', 'PD 2024 Wk10 Input.xlsx'),
                           sheet_name="Loyalty Table")


# adjust transaction data
transaction_df['Transaction_Date'] = pd.to_datetime(transaction_df['Transaction_Date'])
transaction_df = transaction_df[transaction_df['Transaction_Date'].dt.year.isin([2023, 2024])]
transaction_df['Cash_or_Card'] = np.where(transaction_df['Cash_or_Card'] == 1, 'Card', 'Cash')
all_dates = pd.DataFrame(pd.date_range(start='2023-01-01', end='2024-03-06', freq='D'))
all_dates.columns = ['Transaction_Date']
transaction_df = pd.merge(all_dates, transaction_df, how="left")
transaction_df[['Product_Type', 'Product_Scent', 'Product_Size']] = transaction_df['Product_ID'].str.split('-',
                                                                                                           expand=True)
transaction_df['Product_Scent'] = transaction_df['Product_Scent'].str.replace('_', ' ')


# prepare product data for merge
product_df['Product_Size'] = np.where(product_df['Pack_Size'].isna() == True, product_df['Product_Size'],
                                      product_df['Pack_Size'])
transaction_df = pd.merge(transaction_df, product_df, on=['Product_Type', 'Product_Scent', 'Product_Size'], how='left')
transaction_df['Quantity'] = transaction_df['Sales_Before_Discount'] / transaction_df['Selling_Price']


# prepare loyalty data for merge
loyalty_df['Customer_Name'] = loyalty_df['Customer_Name'].apply(rearrange_name)
loyalty_df['Loyalty_Tier'] = loyalty_df['Loyalty_Tier'].map(map_loyalty_tier)
transaction_df = pd.merge(transaction_df, loyalty_df, how='left')
transaction_df['Loyalty_Discount'] = np.where(transaction_df['Loyalty_Discount'] == '5%', 0.05,
                                              np.where(transaction_df['Loyalty_Discount'] == '10%', 0.10,
                                                       np.where(transaction_df['Loyalty_Discount'] == '15%', 0.15, 0)))


# calculate extra fields
transaction_df['Sales_After_Discount'] = np.round(
    transaction_df['Sales_Before_Discount'] * (1 - transaction_df['Loyalty_Discount']), 2)
transaction_df['Profit'] = np.round(
    transaction_df['Sales_After_Discount'] - (transaction_df['Unit_Cost'] * transaction_df['Quantity']), 2)
transaction_df.columns = transaction_df.columns.str.replace('_', ' ')
transaction_df = transaction_df[['Transaction Date', 'Transaction Number', 'Product Type', 'Product Scent',
                                 'Product Size', 'Cash or Card', 'Loyalty Number', 'Customer Name', 'Loyalty Tier',
                                 'Loyalty Discount', 'Quantity', 'Sales Before Discount', 'Sales After Discount',
                                 'Profit']]


# ------Check output-----
# import official solution
official_solution = pd.read_csv(rsf.get_file_path('official_file_solution/', 'PD 2024 Wk 10 Output.csv'))
official_solution['Transaction Date'] = pd.to_datetime(official_solution['Transaction Date'])

# compare results
my_comp = CompareSolutions(transaction_df, official_solution, ['Transaction Date', 'Transaction Number',
                                                               'Product Type', 'Product Scent', 'Product Size'])
my_comp.execute_comparison()
# In the official solution, if the customer does not have loyalty number, profit and sales after discount are null
# because they don't replace null discount by 0
# -----------------------


# Save files
transaction_df.to_csv(rsf.get_file_path('output_files/', 'P2024Week10.csv'), index=False)
