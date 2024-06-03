import pandas as pd
import _read_save_files as rsf

# import files
flow_card = pd.read_excel(rsf.get_file_path('input_files/', 'PD 2024 Wk 4 Input.xlsx'),
                          sheet_name='Flow Card')
flow_card['Flow Card?'] = 'Yes'
print(f"Flow card sheet shape: {flow_card.shape}")
non_flow_card = pd.DataFrame(columns=flow_card.columns.values.tolist())
for sheet in ['Non_flow Card', 'Non_flow Card2']:
    non_flow_card = pd.concat([non_flow_card, pd.read_excel(rsf.get_file_path('input_files/',
                                                                              'PD 2024 Wk 4 Input.xlsx'),
                                                            sheet_name=sheet)], ignore_index=True)
non_flow_card['Flow Card?'] = 'No'
print(f"Non Flow card sheets shape: {non_flow_card.shape}")
all_passengers = pd.concat([flow_card, non_flow_card], ignore_index=True)
print(f"Final file shape: {all_passengers.shape}")

seat_plan = pd.read_excel(rsf.get_file_path('input_files/', 'PD 2024 Wk 4 Input.xlsx'),
                          sheet_name='Seat Plan')
print(f"seat_plan sheet shape: {seat_plan.shape}")

# merge files
customer_and_seat = pd.merge(seat_plan, all_passengers, on=['Class', 'Seat', 'Row'], how='left')

# filter empty seats
available_seats = customer_and_seat.loc[customer_and_seat.isnull().any(axis=1)].drop(
    columns=['CustomerID', 'Flow Card?'])
print(f"available_seats shape: {available_seats.shape}")

# save files
available_seats.to_csv(rsf.get_file_path('output_files/', 'P2024Week4.csv'), index=False)
