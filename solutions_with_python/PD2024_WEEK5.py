import pandas as pd
from Preppin.meta import read_save_files as rsf
import numpy as np
from Preppin.Evaluate.Verify import CompareSolutions

# Import files
flights_2024 = pd.read_csv(rsf.get_file_path('input_files/', 'PD 2024 Wk5 Prep Air 2024 Flights.csv'))
ticket_sales = pd.read_csv(rsf.get_file_path('input_files/', 'PD 2024 Wk5 Prep Air Ticket Sales.csv'))
customers = pd.read_csv(rsf.get_file_path('input_files/', 'PD 2024 Wk5 Prep Air Customers.csv'))
print(f"flights_2024 df shape: {flights_2024.shape}")
print(f"ticket_sales df shape: {ticket_sales.shape}")
print(f"customers df shape: {customers.shape}")


# Create first output: detailed booked flights.
booked_flights = pd.merge(pd.merge(ticket_sales, flights_2024, on=['Flight Number', 'Date'], how='left'), customers,
                          on='Customer ID', how='left')
print(f"First output (booked_flights) shape: {booked_flights.shape}")


# Create second output df: Not booked flights. Merge flights_2024 with summarized ticket_sales and then select the
# flights with no booking
ticket_sales_sum = ticket_sales.groupby(['Flight Number', 'Date'], as_index=False)['Ticket Price'].agg('sum')
not_booked_flights = pd.merge(flights_2024, ticket_sales_sum, on=['Flight Number', 'Date'], how='left')
not_booked_flights = not_booked_flights.loc[not_booked_flights.isnull().any(axis=1)].drop(
    columns=['Ticket Price'])
not_booked_flights['Flight unbooked as of'] = '2024-01-31'
print(f"Second output (not_booked_flights) shape: {not_booked_flights.shape}")


# Create third output df:
yet_to_book = pd.merge(customers, ticket_sales, on=['Customer ID'], how='left')
yet_to_book = yet_to_book.loc[yet_to_book.isnull().any(axis=1)].drop(columns=['Date', 'Flight Number', 'Ticket Price'])
yet_to_book['Last Date Flown'] = pd.to_datetime(yet_to_book['Last Date Flown'])
yet_to_book['Today'] = pd.to_datetime('2024-01-31')
yet_to_book['Days Since last Flown'] = (yet_to_book['Today'] - yet_to_book['Last Date Flown']).dt.days
yet_to_book.drop(columns=['Today'], inplace=True)
yet_to_book['Customer Category'] = np.where(yet_to_book['Days Since last Flown'] <= 90,
                                            'Recent Fliers (less than 3 months since last flight)',
                                            np.where(yet_to_book['Days Since last Flown'] <= 180,
                                                     'Taking a break (3-6 months since last flight)',
                                                     np.where(yet_to_book['Days Since last Flown'] <= 270,
                                                              'Been away a while (6-9 months since last flight)',
                                                              'Lapsed (over 9 months since last flight)')))
print(f"Third output (yet_to_book) shape: {yet_to_book.shape}")


# Check solution first solution
print("FIRST COMPARISON OUTPUT:")
official_file_name = rsf.get_file_path('official_file_solution/', 'Prep Air Output.xlsx')
booked_flights_official_df = pd.read_excel(official_file_name, sheet_name='2024 Booked Flights')
my_comp1 = CompareSolutions(booked_flights, booked_flights_official_df, ['Date', 'Flight Number', 'Customer ID'])
my_comp1.execute_comparison()

# Check solution second solution
print("SECOND COMPARISON OUTPUT:")
unbooked_flights_official_df = pd.read_excel(official_file_name, sheet_name='Unbooked Flights')
my_comp2 = CompareSolutions(not_booked_flights, unbooked_flights_official_df, ['Date', 'Flight Number'])
my_comp2.execute_comparison()

# Check solution second solution
print("THIRD COMPARISON OUTPUT:")
customers_yet_to_book_df = pd.read_excel(official_file_name, sheet_name='Customers Yet to Book in 2024')
my_comp3 = CompareSolutions(yet_to_book, customers_yet_to_book_df, ['Customer ID'])
my_comp3.execute_comparison()


# Save files
with pd.ExcelWriter(rsf.get_file_path('output_files/', 'P2024Week5.xlsx')) as writer:
    booked_flights.to_excel(writer, sheet_name='2024 Booked Flights', index=False)
    not_booked_flights.to_excel(writer, sheet_name='Unbooked Flights', index=False)
    yet_to_book.to_excel(writer, sheet_name='Customers Yet to Book in 2024', index=False)