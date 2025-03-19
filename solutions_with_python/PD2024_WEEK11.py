import pandas as pd


# Creating a list with all days from 2024
days_2024 = pd.date_range(start="2024-01-01", end="2024-12-31", freq="D")
days_list = days_2024.strftime("%Y-%m-%d").tolist()

# Create new date:
new_days_list = []
month_calc = 0
day_calc = 0
for i in range(len(days_list)):
    day_calc = (i+1) - 28*month_calc
    new_days_list.append(f"2024-{month_calc+1}-{day_calc}")
    if day_calc == 28:
        month_calc += 1

# The expected answer from the challenge is:
# - The new calendar should have 14 months
# - The last month of this new calendar should have 2 days only:

# Checking my results:
print(f"Number of months in the new calendar: {month_calc+1}")
print(f"Last two days of the year in the new calendar: {new_days_list[-2:]}")