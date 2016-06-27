import tappy_sql_connection
import numpy as np
import pandas as pd
import datetime

sql_query = """
SELECT * FROM daily_summary;
"""
simple_prediction_df = pd.read_sql_query(sql_query,tappy_sql_connection.conn)

def simple_median_predict(day):
    if day == 'friday':
        day_of_interest = 'is_friday'
        day_number = 4
    if day == 'saturday':
        day_of_interest = 'is_saturday'
        day_number = 5
    #given todays date, find the datekey for the upcoming friday and saturday
    day_of_week_today = (datetime.datetime.today().weekday())
    days_until = day_number-day_of_week_today
    upcoming_day = ((datetime.date.today() + datetime.timedelta(days=days_until)))
    week_of_year_today = datetime.datetime.today().isocalendar()[1]

    #using that friday/saturday, find the median (and mean) sales for the previous sales of that friday/saturday
    friday_array = np.array([])
    saturday_array = np.array([])
    day_array = np.array([])
    for index, row in simple_prediction_df.iterrows():
        if row['week_of_year'] == week_of_year_today:
            if row[day_of_interest]:
                day_array = np.append(day_array,row['daily_subtotal'])
    return [upcoming_day, round(np.median(day_array),2)]
