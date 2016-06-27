import tappy_sql_connection
import pandas as pd
import numpy as np
import datetime

# query:
sql_query = """
SELECT * FROM transactions;
"""
individual_sales_df = pd.read_sql_query(sql_query,tappy_sql_connection.conn)

print('Total orders in database: '+str(len(individual_sales_df)))  
print('Should have 17252 orders according to SalesVu.')

#drop known anomalousstar transactions
individual_sales_df.drop(individual_sales_df[individual_sales_df['unique_order_id'] == '13708_051320161038'].index, inplace=True)
individual_sales_df.drop(individual_sales_df[individual_sales_df['unique_order_id'] == '123_022120141008'].index, inplace=True)
individual_sales_df.drop(individual_sales_df[individual_sales_df['unique_order_id'] == '5221_032820151102'].index, inplace=True)

#print(individual_sales_df.tail(10))

tappy_sql_connection.cur.execute(" CREATE TABLE daily_summary \
   (datekey INT PRIMARY KEY, month INT, day INT, year INT, day_of_week INT,\
   is_friday INT, is_saturday INT, day_of_year INT, week_of_year INT, daily_subtotal REAL,\
   daily_tax REAL, daily_gratuity REAL, daily_grand_total REAL, number_of_customers REAL);")

year_month_day_list = np.array([])
daily_subtotal_list = np.array([])
#conn.rollback()
sql_query = """
SELECT * FROM daily_summary;
"""

tappy_sql_connection.cur.execute(sql_query)
rows = tappy_sql_connection.cur.fetchall()

years_of_interest = individual_sales_df['year'].unique()
for year in years_of_interest:
    for month in ((individual_sales_df[individual_sales_df.year == year])['month'].unique()):
        for day in (((individual_sales_df[(individual_sales_df.year == year) & (individual_sales_df.month == month)])['day'].unique())):
            number_of_customers = 0
            day_of_week = (datetime.date(int(year), int(month), int(day)).weekday())
            is_friday = 0
            is_saturday = 0
            #Friday = 4
            if day_of_week == 4:
                is_friday = 1
            #Saturday = 5
            if day_of_week == 5:
                is_saturday = 1
            week_of_year = (datetime.date(int(year), int(month), int(day)).isocalendar()[1])
            day_of_year = datetime.date(int(year), int(month), int(day)).timetuple().tm_yday
            datekey = str(year)+str(month).zfill(2)+str(day).zfill(2)
            daily_subtotal = (individual_sales_df[(individual_sales_df.year == year) & (individual_sales_df.month == month) & (individual_sales_df.day == day)])['subtotal'].sum()
            daily_gratuity = (individual_sales_df[(individual_sales_df.year == year) & (individual_sales_df.month == month) & (individual_sales_df.day == day)])['gratuity'].sum()
            daily_tax = (individual_sales_df[(individual_sales_df.year == year) & (individual_sales_df.month == month) & (individual_sales_df.day == day)])['tax'].sum()
            daily_grand_total = (individual_sales_df[(individual_sales_df.year == year) & (individual_sales_df.month == month) & (individual_sales_df.day == day)])['grand_total'].sum()
            number_of_sales = len((individual_sales_df[(individual_sales_df.year == year) & (individual_sales_df.month == month) & (individual_sales_df.day == day)])['grand_total'])
            number_of_customers = number_of_sales
            daily_subtotal_list = np.append(daily_subtotal_list,daily_subtotal)
            year_month_day_list = np.append(year_month_day_list,datekey)
            if (len(rows)) == 0:
                query = 'INSERT INTO daily_summary (datekey, month, day, year, day_of_week, is_friday, is_saturday, \
                                day_of_year, week_of_year, daily_subtotal, daily_tax, daily_gratuity, daily_grand_total, number_of_customers) VALUES (%s, %s, %s, %s, \
                                %s, %s, %s, %s, %s, %s, %s, %s, %s, %s);'
                data=( datekey, int(month), int(day), int(year), int(day_of_week), int(is_friday), int(is_saturday), int(day_of_year), int(week_of_year),\
                                 float(daily_subtotal), float(daily_tax), float(daily_gratuity), float(daily_grand_total), int(number_of_customers))
                try:
                    tappy_sql_connection.cur.execute(query,data)
                    tappy_sql_connection.conn.commit()
                except:
                    tappy_sql_connection.conn.rollback()