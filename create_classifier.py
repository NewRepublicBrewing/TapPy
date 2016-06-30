import tappy_sql_connection
from pandas.tseries.holiday import USFederalHolidayCalendar
import pandas as pd
import numpy as np
import pickle
from os.path import isfile
from shutil import move
import datetime
import matplotlib.pyplot as plt

from sklearn.cross_validation import train_test_split
#from sklearn.tree import DecisionTreeRegressor
#from sklearn.tree import DecisionTreeClassifier
#from sklearn.linear_model import Ridge
#from sklearn.linear_model import RidgeCV
from sklearn.linear_model import ElasticNet
from sklearn.linear_model import Lasso
#from sklearn.linear_model import SGDRegressor
#from sklearn.linear_model import ARDRegression
#from sklearn.svm import SVR
#from sklearn.ensemble import RandomForestRegressor
#from sklearn.ensemble import ExtraTreesRegressor
#from sklearn.ensemble import AdaBoostRegressor
#from sklearn.linear_model import LinearRegression
from sklearn.feature_selection import SelectFromModel

def heat_index_calculator(temperature, humidity):
    if humidity < 13:
        if 80 < temperature < 112:
            adjustment = ((13-humidity)/4)*np.sqrt((17-np.abs(temperature-95.))/17)
            humidity = humidity-adjustment
    if humidity > 85:
        if 80 < temperature < 87:
            adjustment = ((humidity-85)/10) * ((87-temperature)/5)
            humidity = humidity + adjustment
    heat_ind = -42.379 + 2.04901523*temperature + 10.14333127*humidity - .22475541*temperature*humidity - .00683783*temperature*temperature - .05481717*humidity*humidity + .00122874*temperature*temperature*humidity + .00085282*temperature*humidity*humidity - .00000199*temperature*temperature*humidity*humidity
    return heat_ind

bartender_cutoff = 575 #cutoff between 1 and 2 bartenders

#Pull in the weather DB because we're going to be using it to derive a LOT of the other features
# query:
sql_query = """
SELECT * FROM weather;
"""
weather_df = pd.read_sql_query(sql_query,tappy_sql_connection.conn)

sql_query = """
SELECT * FROM daily_summary;
"""
daily_df = pd.read_sql_query(sql_query,tappy_sql_connection.conn)

#easy pandas routines to engineer new features
weather_df['temp_deviation_from_avg'] = (weather_df.mean_temp - weather_df.avg_mean_temp)
weather_df['mean_temp_deviation_from_75'] = np.abs(weather_df.mean_temp - 70)
weather_df['max_temp_deviation_from_75'] = np.abs(weather_df.max_temp - 70)
heat_index_array = np.array([])
dew_point_above = np.array([])
for weather_index, temp in enumerate(weather_df.mean_temp):
    heat_index_array = np.append(heat_index_array, heat_index_calculator((weather_df.mean_temp[weather_index]),(weather_df.mean_humidity[weather_index])))
    if weather_df.dew_point[weather_index] > 74:
        dew_point_above = np.append(dew_point_above, 1)
    else:
        dew_point_above = np.append(dew_point_above, 0)
    
weather_df['heat_index'] = np.abs(heat_index_array-70)
weather_df['dew_point_high'] = np.abs(dew_point_above)
weather_df['temp_max_minus_mean'] = (weather_df.max_temp - weather_df.mean_temp)
weather_df['cumulative_precipitation'] = (weather_df.mtd_precipitation-weather_df.precipitation)


#make the first friday column to append to the whole data frame later
datekey_list = []
first_friday_list = []
for weather_datekey in weather_df.datekey:
    year = int(str(weather_datekey)[:4])
    month = int(str(weather_datekey)[4:6])
    day = int(str(weather_datekey)[6:])
    today = (datetime.date(int(year), int(month), int(day)))
    first_friday = 0
    if today.weekday() == 4:
        if day <= 7:
            first_friday = 1
    first_friday_list.append(first_friday)
    datekey_list.append(weather_datekey)
first_friday_db = {'first_friday' : pd.Series(first_friday_list, index=datekey_list)}
first_friday_df = pd.DataFrame(first_friday_db)



#Set values in column to 1 if school is in session
all_days_list = []
in_school_list = []
for weather_datekey in weather_df.datekey:
    year = int(str(weather_datekey)[:4])
    month = int(str(weather_datekey)[4:6])
    day = int(str(weather_datekey)[6:])
    date_of_interest = datetime.date(year, month, day)
    in_school = 0
    #fall 2013 schedule
    beginning_range = datetime.date(2013, 8, 26)
    end_range = datetime.date(2013, 12, 11)
    if beginning_range <= date_of_interest <= end_range:
        in_school = 1
    #spring 2014 schedule
    beginning_range = datetime.date(2014, 1, 13)
    end_range = datetime.date(2013, 5, 7)
    if beginning_range <= date_of_interest <= end_range:
        in_school = 1
    #fall 2014 schedule
    beginning_range = datetime.date(2014, 9, 1)
    end_range = datetime.date(2014, 12, 17)
    if beginning_range <= date_of_interest <= end_range:
        in_school = 1
    #spring 2015 schedule
    beginning_range = datetime.date(2015, 1, 20)
    end_range = datetime.date(2015, 5, 11)
    if beginning_range <= date_of_interest <= end_range:
        in_school = 1
    #fall 2015 schedule
    beginning_range = datetime.date(2015, 8, 31)
    end_range = datetime.date(2015, 12, 16)
    if beginning_range <= date_of_interest <= end_range:
        in_school = 1
    #spring 2016 schedule
    beginning_range = datetime.date(2016, 1, 19)
    end_range = datetime.date(2016, 5, 10)
    if beginning_range <= date_of_interest <= end_range:
        in_school = 1
    all_days_list.append(weather_datekey)
    in_school_list.append(in_school)
school_db = {'in_school' : pd.Series(in_school_list, index=all_days_list)}
school_df = pd.DataFrame(school_db)



#As a proxy for the growth of the business over time, we'll count days since the first day in the database
datekey_list = []
days_since_open_list = []
#for weather_datekey in weather_df.index.values:
for weather_datekey in weather_df.datekey:
    year = int(str(weather_datekey)[:4])
    month = int(str(weather_datekey)[4:6])
    day = int(str(weather_datekey)[6:])
    opening_day = datetime.date(2013, 9, 6)
    date_of_interest = datetime.date(year, month, day)
    delta = date_of_interest - opening_day
    days_since_open = delta.days
    #print(days_since_open)
    datekey_list.append(weather_datekey)
    days_since_open_list.append(days_since_open)
days_since_open_db = {'days_since_open' : pd.Series(days_since_open_list, index=datekey_list)}
days_since_open_df = pd.DataFrame(days_since_open_db)



#Honestly not sure why this one works, but there's a definite trend between
#days since the start of the school year begins and the daily total
datekey_list = []
days_since_school_year_start_list = []
for weather_datekey in weather_df.datekey:
    year = int(str(weather_datekey)[:4])
    month = int(str(weather_datekey)[4:6])
    day = int(str(weather_datekey)[6:])
    date_of_interest = datetime.date(year, month, day)
    #for 2013/2014 School year
    beginning_range = datetime.date(2013, 8, 26)
    end_range = datetime.date(2014, 9, 1)
    if beginning_range <= date_of_interest <= end_range:
        days_since_school_year_start = (date_of_interest - beginning_range).days
    #for 2014/2015 School year
    beginning_range = datetime.date(2014, 9, 1)
    end_range = datetime.date(2015, 8, 31)
    if beginning_range <= date_of_interest <= end_range:
        days_since_school_year_start = (date_of_interest - beginning_range).days
    #for 2015/2016 School year
    beginning_range = datetime.date(2015, 8, 31)
    end_range = datetime.date(2016, 8, 29)
    if beginning_range <= date_of_interest <= end_range:
        days_since_school_year_start = (date_of_interest - beginning_range).days
    datekey_list.append(weather_datekey)
    days_since_school_year_start_list.append(days_since_school_year_start)
days_since_school_year_start_db = {'days_since_school_year_start' : pd.Series(days_since_school_year_start_list, index=datekey_list)}
days_since_school_year_start_df = pd.DataFrame(days_since_school_year_start_db)



#Account for major US federal holidays
cal = USFederalHolidayCalendar()
holidays = cal.holidays(start='2013-01-01', end='2016-12-31').to_pydatetime()
datekey_list = []
holidays_list = []
#for weather_datekey in weather_df.index.values:
for weather_datekey in weather_df.datekey:
    year = int(str(weather_datekey)[:4])
    month = int(str(weather_datekey)[4:6])
    day = int(str(weather_datekey)[6:])
    date_of_interest = datetime.date(year, month, day)
    if date_of_interest in holidays:
        holidays_list.append(1)
    else:
        holidays_list.append(0)
    datekey_list.append(weather_datekey)
holidays_db = {'holidays' : pd.Series(holidays_list, index=datekey_list)}
holidays_df = pd.DataFrame(holidays_db)



#incase the week of the month matters
first_week_list = []
second_week_list = []
third_week_list = []
fourth_week_list = []
all_datekey_list = []
for weather_datekey in weather_df.datekey:
    first_week_of_month = 0
    second_week_of_month = 0
    third_week_of_month = 0
    fourth_week_of_month = 0
    day = int(str(weather_datekey)[6:])
    if day <= 7:
        first_week_of_month = 1
    if 7 < day <= 14:
        second_week_of_month = 1
    if 14 < day <= 21:
        third_week_of_month = 1
    if 21 < day:
        fourth_week_of_month = 1
    all_datekey_list.append(weather_datekey)
    first_week_list.append(first_week_of_month)
    second_week_list.append(second_week_of_month)
    third_week_list.append(third_week_of_month)
    fourth_week_list.append(fourth_week_of_month)
week_of_month_db = {'first_week_of_month' : pd.Series(first_week_list, index=all_datekey_list),
                'second_week_of_month' : pd.Series(second_week_list, index=all_datekey_list),
                'third_week_of_month' : pd.Series(third_week_list, index=all_datekey_list),
                'fourth_week_of_month' : pd.Series(fourth_week_list, index=all_datekey_list),}
week_of_month_df = pd.DataFrame(week_of_month_db)



#This acts as sort of a onehot for the strings in the events column of the weather db
datekey_list = []
no_adverse_weather_event_list = []
fog_event_list = []
rain_event_list = []
thunderstorm_event_list = []
snow_event_list = []
for line in weather_df.index.values:
    no_adverse_weather_event = 1
    fog_event = 0
    rain_event = 0
    thunderstorm_event = 0
    snow_event = 0
    for event in (weather_df.iloc[line])['events']:
        if event == 'Fog':
            fog_event = 1
            no_adverse_weather_event = 0
        if event == 'Rain':
            rain_event = 1
            no_adverse_weather_event = 0
        if event == 'Snow':
            snow_event = 1
            no_adverse_weather_event = 0
        if event == 'Thunderstorm':
            thunderstorm_event = 1
            no_adverse_weather_event = 0
    datekey_list.append((weather_df.index)[line])
    no_adverse_weather_event_list.append(no_adverse_weather_event)
    fog_event_list.append(fog_event)
    rain_event_list.append(rain_event)
    thunderstorm_event_list.append(thunderstorm_event)
    snow_event_list.append(snow_event)
weather_events_db = {'no_adverse_weather_event' : pd.Series(no_adverse_weather_event_list, index=all_datekey_list),
                'fog_event' : pd.Series(fog_event_list, index=all_datekey_list), 
                'rain_event' : pd.Series(rain_event_list, index=all_datekey_list), 
                'thunderstorm_event' : pd.Series(thunderstorm_event_list, index=all_datekey_list), 
                'snow_event' : pd.Series(snow_event, index=all_datekey_list)}
weather_events_df = pd.DataFrame(weather_events_db)



#account for special events that happen at the brewery
datekey_list = []
brewery_events_list = []
for weather_datekey in weather_df.datekey:
    year = int(str(weather_datekey)[:4])
    month = int(str(weather_datekey)[4:6])
    day = int(str(weather_datekey)[6:])
    brewery_event = 0
    if weather_datekey == 20140503:
        #anniversary party
        brewery_event = 1
    if weather_datekey == 20150502:
        #anniversary party
        brewery_event = 1
    if weather_datekey == 20160507:
        #anniversary party
        brewery_event = 1
    if weather_datekey == 20160430:
        #big dady Z's luau
        brewery_event = 1
    if weather_datekey == 20160423:
        #I was not working this day, there was a bend and brew, and also stayed open way late
        brewery_event = 1
    if weather_datekey == 20160416:
        #microdistrict launch
        brewery_event = 1
    if weather_datekey == 20160422:
        #open way late again, need to investigate further
        brewery_event = 1
    if weather_datekey == 20140221:
        #has a $236 cash transaction!? transaction# 123_022120141008
        brewery_event = 1
    if weather_datekey == 20150328:
        #has a $100 cash transaction after closeout, I was at Rocky transaction# 5221_032820151102
        brewery_event = 1
    if weather_datekey == 20150221:
        #had art night, but otherwise just a legit good day
        brewery_event = 1
    if weather_datekey == 20150327:
        #has a $50 cash transaction after closeout, john was working, Ronin cooking was there,
        brewery_event = 1
    if weather_datekey == 20150718:
        #looks legit, morgan and sarah were out, they drew some of the crowd
        brewery_event = 1
    if weather_datekey == 20150829:
        #looks legit, brice woolard was out
        brewery_event = 1
    if weather_datekey == 20140418:
        #this was girls night out at the brewery, open later than normal
        brewery_event = 1
    if weather_datekey == 20150411:
        #food truck battle, open way more hours than normal
        brewery_event = 1
    datekey_list.append(weather_datekey)
    brewery_events_list.append(brewery_event)
brewery_events_db = {'brewery_events' : pd.Series(brewery_events_list, index=datekey_list)}
brewery_events_df = pd.DataFrame(brewery_events_db)



#incase we need to switch from money to categorization, this will be the ground truth
datekey_list = []
number_of_bartenders_list = []
for line in daily_df.index.values:
    number_of_bartenders = 0
    if ((daily_df.iloc[line])['daily_subtotal']) > bartender_cutoff:
        number_of_bartenders = 1 #doing 0 or 1 because it's easier than working out 1 and 2
        #let's just pretend we're counting from 0...
    datekey_list.append(int(((daily_df.iloc[line])['datekey'])))
    number_of_bartenders_list.append(number_of_bartenders)
number_of_bartenders_db = {'number_of_bartenders' : pd.Series(number_of_bartenders_list, index=datekey_list)}



#Pull in the manually constructed database which contains historical information on
#bands, food trucks, and bartenders working.  This is known to not be 100% accurate
band_food_bartender_special_events = pd.read_csv('/Users/jimmy/Downloads/brewery_stats_v1.csv', index_col=0)
food_trucks = pd.get_dummies(band_food_bartender_special_events['food_truck'])
food_trucks['any_truck'] = food_trucks['Big Daddy Zs']+food_trucks['DBQ']+food_trucks['Fusion Peru']+\
    food_trucks['Goats Catering']+food_trucks['In-between girls']+food_trucks['Into the Fire Pizza']+\
    food_trucks['Many']+food_trucks["Mickey's Sliders"]+food_trucks['Napa Flats']+food_trucks['Pik Pak Push']+\
    food_trucks['Pin-Toh Thai']+food_trucks['Potato Shack']+food_trucks['Raspas']+food_trucks['Ronin Cooking']+\
    food_trucks['Sugba']+food_trucks['Taz']+food_trucks['Wafology']
number_of_bartenders_df = pd.DataFrame(number_of_bartenders_db)



#Create the historical median, yearly median, and day before columns
def prior(date_of_interest):
    day_of_week_for_prior = (date_of_interest.weekday())
    week_of_year_for_prior = date_of_interest.isocalendar()[1]
    day_array = np.array([])
    for prior_index, row in daily_df.iterrows():
        if row['week_of_year'] == week_of_year_for_prior:
            if row['day_of_week'] == day_of_week_for_prior:
                #if row['day_of_week'] == 4 or row['day_of_week'] == 5:
                day_array = np.append(day_array,row['daily_subtotal'])
    return np.median(day_array)

def yearly_median(date_of_interest):
    year_for_prior = date_of_interest.year
    day_array = np.array([])
    for prior_index, row in daily_df.iterrows():
        if row['year'] == year_for_prior:
            day_array = np.append(day_array,row['daily_subtotal'])
    return np.median(day_array)

def previous_day(date_of_interest):
    day_of_week_for_prior = (date_of_interest.weekday())
    if date_of_interest == datetime.date(2013,9,6):
        previous_subtotal = 0.0
    if date_of_interest != datetime.date(2013,9,6):
        if day_of_week_for_prior == (date_of_interest.weekday()) == 4:
            date_6_days_ago = date_of_interest - datetime.timedelta(days=6)
            previous_year = date_6_days_ago.year
            previous_month = date_6_days_ago.month
            previous_day = date_6_days_ago.day
            #previous_subtotal = date_6_days_ago
            previous_subtotal = ((daily_df[(daily_df.year == previous_year) & (daily_df.month == previous_month) & (daily_df.day == previous_day)]).daily_subtotal)
        elif day_of_week_for_prior == (date_of_interest.weekday()) == 5:
            yesterday = date_of_interest - datetime.timedelta(days=1)
            previous_year = yesterday.year
            previous_month = yesterday.month
            previous_day = yesterday.day
            #previous_subtotal = yesterday
            previous_subtotal = ((daily_df[(daily_df.year == previous_year) & (daily_df.month == previous_month) & (daily_df.day == previous_day)]).daily_subtotal)
        else:
            previous_subtotal = 0.0
    return (previous_subtotal)
     
datekey_list = []
daily_prior_list = []
yearly_prior_list = []
yesterday_prior_list = []
for daily_index, daily_row in daily_df.iterrows():
    date = datetime.date(int(daily_row['year']), int(daily_row['month']), int(daily_row['day']))
    daily_prior = prior(date)
    daily_prior_list.append(round(daily_prior,2))
    yearly_prior = yearly_median(date)
    yearly_prior_list.append(round(yearly_prior,2))
    yesterday_prior = previous_day(date)
    #print(yesterday_prior)
    if isinstance(yesterday_prior, pd.Series):
        #print('found series')
        if yesterday_prior.empty:
            yesterday_prior = 0.0
        else:
            yesterday_prior = float(yesterday_prior)
    yesterday_prior_list.append((yesterday_prior))
    datekey_list.append(int(str(int(daily_row['year']))+str(int(daily_row['month'])).zfill(2)+str(int(daily_row['day'])).zfill(2)))
daily_prior_db = {'daily_prior' : pd.Series(daily_prior_list, index=datekey_list),
                 'yearly_prior' : pd.Series(yearly_prior_list, index=datekey_list),
                 'yesterday_prior' : pd.Series(yesterday_prior_list, index=datekey_list)}
daily_prior_df = pd.DataFrame(daily_prior_db)



#make smarter bands columns
datekey_list = []
band_list = []
band_fans_list = []
for datekey, band_row in band_food_bartender_special_events.iterrows():
    band = 1
    if band_row['band'] == 'none':
        band = 0
    band_list.append(band)
    band_fans_list.append(band_row['band_fans'])
    datekey_list.append(datekey)        
band_db = {'band' : pd.Series(band_list, index=datekey_list),
                'band_fans' : pd.Series(band_fans_list, index=datekey_list),}
band_df = pd.DataFrame(band_db)



#Special events, this overlaps some with "brewery events" which could easily be a problem
datekey_list = []
special_event_list = []
counter = 0
for line in band_food_bartender_special_events.index.values:
    special_event = 1
    if ((band_food_bartender_special_events.iloc[counter])['special_event']) == 'none':
        special_event = 0
    datekey_list.append(line)
    special_event_list.append(special_event)
    counter +=1
special_event_db = {'special_event' : pd.Series(special_event_list, index=all_datekey_list)}
special_event_df = pd.DataFrame(special_event_db)



#Pull in the sports data grabbed from the 12thman.com website
sports_cal = pd.DataFrame.from_csv('/Users/jimmy/Downloads/TAMU_Sports_Calendar.txt', sep='\t', header=0)
football_dates = ((sports_cal[sports_cal['Category']=='Football'])['Start Date']).values
football_locations = ((sports_cal[sports_cal['Category']=='Football'])['Location']).values
mens_basketball_dates = ((sports_cal[sports_cal['Category']=="Men's Basketball"])['Start Date']).values
mens_basketball_locations = ((sports_cal[sports_cal['Category']=="Men's Basketball"])['Location']).values
baseball_dates = ((sports_cal[sports_cal['Category']=='Baseball'])['Start Date']).values
baseball_locations = ((sports_cal[sports_cal['Category']=='Baseball'])['Location']).values
all_sports_datekey_list = []
all_sports_games_list = []
all_sports_home_away_list = []
football_datekey_list = []
football_games_list = []
football_home_away_list = []
for football_index, football_date in enumerate(football_dates):
    football_year = (football_date.split('/'))[2]
    football_month = (football_date.split('/'))[0]
    football_day = (football_date.split('/'))[1]
    football_datekey = str(football_year)+str(football_month).zfill(2)+str(football_day).zfill(2)
    football_datekey_list.append(int(football_datekey))
    football_games_list.append(1)
    all_sports_datekey_list.append(int(football_datekey))
    all_sports_games_list.append(1)
    if (football_locations[football_index]) == 'College Station':
        football_home_away_list.append(1)
        all_sports_home_away_list.append(1)
    else:
        football_home_away_list.append(0.5)
        all_sports_home_away_list.append(0.5)
football_dates_db = {'football_games' : pd.Series(football_games_list, index=football_datekey_list),
                  'football_home_away' : pd.Series(football_home_away_list, index=football_datekey_list)}
football_dates_df = pd.DataFrame(football_dates_db)
    
mens_basketball_datekey_list = []
mens_basketball_games_list = []
mens_basketball_home_away_list = []
for mens_basketball_index, mens_basketball_date in enumerate(mens_basketball_dates):
    mens_basketball_year = (mens_basketball_date.split('/'))[2]
    mens_basketball_month = (mens_basketball_date.split('/'))[0]
    mens_basketball_day = (mens_basketball_date.split('/'))[1]
    mens_basketball_datekey = str(mens_basketball_year)+str(mens_basketball_month).zfill(2)+str(mens_basketball_day).zfill(2)
    mens_basketball_datekey_list.append(int(mens_basketball_datekey))
    mens_basketball_games_list.append(1)
    all_sports_datekey_list.append(int(mens_basketball_datekey))
    all_sports_games_list.append(1)
    if (mens_basketball_locations[mens_basketball_index]) == 'College Station':
        mens_basketball_home_away_list.append(1)
        all_sports_home_away_list.append(1)
    else:
        mens_basketball_home_away_list.append(0.5)
        all_sports_home_away_list.append(0.5)
mens_basketball_dates_db = {'mens_basketball_games' : pd.Series(mens_basketball_games_list, index=mens_basketball_datekey_list),
                  'mens_basketball_home_away' : pd.Series(mens_basketball_home_away_list, index=mens_basketball_datekey_list)}
mens_basketball_dates_df = pd.DataFrame(mens_basketball_dates_db)

baseball_datekey_list = []
baseball_games_list = []
baseball_home_away_list = []
for baseball_index, baseball_date in enumerate(baseball_dates):
    baseball_year = (baseball_date.split('/'))[2]
    baseball_month = (baseball_date.split('/'))[0]
    baseball_day = (baseball_date.split('/'))[1]
    baseball_datekey = str(baseball_year)+str(baseball_month).zfill(2)+str(baseball_day).zfill(2)
    baseball_datekey_list.append(int(baseball_datekey))
    baseball_games_list.append(1)
    all_sports_datekey_list.append(int(baseball_datekey))
    all_sports_games_list.append(1)
    if (baseball_locations[baseball_index]) == 'College Station':
        baseball_home_away_list.append(1)
        all_sports_home_away_list.append(1)
    else:
        baseball_home_away_list.append(0.5)
        all_sports_home_away_list.append(0.5)
baseball_dates_db = {'baseball_games' : pd.Series(baseball_games_list, index=baseball_datekey_list),
                  'baseball_home_away' : pd.Series(baseball_home_away_list, index=baseball_datekey_list)}
baseball_dates_df = pd.DataFrame(baseball_dates_db)

all_sports_dates_db = {'all_sports_games' : pd.Series(all_sports_games_list, index=all_sports_datekey_list),
                  'all_sports_home_away' : pd.Series(all_sports_home_away_list, index=all_sports_datekey_list)}
all_sports_dates_df = pd.DataFrame(all_sports_dates_db)

all_sports_dates_df = all_sports_dates_df.join(football_dates_df)
all_sports_dates_df = all_sports_dates_df.join(baseball_dates_df)
all_sports_dates_df = all_sports_dates_df.join(mens_basketball_dates_df)



#Bring all the dataframes defined above together, and onehot a few more and throw them in too
pandas_weather_df = weather_df.set_index('datekey')
pandas_daily_df = daily_df.set_index('datekey')
combined = pandas_daily_df.join(pandas_weather_df)
combined = combined.join(weather_events_df)
combined = combined.join(school_df)
combined = combined.join(days_since_open_df)
combined = combined.join(brewery_events_df)
combined = combined.join(days_since_school_year_start_df)
combined = combined.join(week_of_month_df)
combined = combined.join(food_trucks)
combined = combined.join(band_df)
combined = combined.join(special_event_df)
combined = combined.join(number_of_bartenders_df)
combined = combined.join(daily_prior_df)
combined = combined.join(all_sports_dates_df)
combined = combined.join(first_friday_df)
combined = combined.join(holidays_df)
combined.fillna(0, inplace=True)
month_one_hot = pd.get_dummies(combined['month'])
combined['in_january'] = month_one_hot[1]
combined['in_february'] = month_one_hot[2]
combined['in_march'] = month_one_hot[3]
combined['in_april'] = month_one_hot[4]
combined['in_may'] = month_one_hot[5]
combined['in_june'] = month_one_hot[6]
combined['in_july'] = month_one_hot[7]
combined['in_august'] = month_one_hot[8]
combined['in_september'] = month_one_hot[9]
combined['in_october'] = month_one_hot[10]
combined['in_november'] = month_one_hot[11]
combined['in_december'] = month_one_hot[12]
year_one_hot = pd.get_dummies(combined['year'])
combined['in_2013'] = year_one_hot[2013]
combined['in_2014'] = year_one_hot[2014]
combined['in_2015'] = year_one_hot[2015]
combined['in_2016'] = year_one_hot[2016]
combined = combined[combined.index != 20140503]
combined = combined[combined.index != 20150502]
combined = combined[combined.index != 20160507]



#Let's try rescalling everything to be between 0 and 1!
combined_dataframe_columns = list(combined.columns.values)
rescaled = pd.DataFrame()
maxes = pd.DataFrame()
for column in combined_dataframe_columns:
	if column != 'events':
		rescaled[column] = (combined[column]-combined[column].min())/(combined[column].max()-combined[column].min())
		maxes[column] = np.array([combined[column].max()])
		#print(combined[column].max())

#print(maxes)
maxes.to_csv('maxes.csv')

#make sure we're only doing friday and saturday
clean_combined = combined[(combined['day_of_week']==4) | (combined['day_of_week']==5)]
rescaled_clean_combined = rescaled[(combined['day_of_week']==4) | (combined['day_of_week']==5)]
working_df = rescaled_clean_combined
#working_df = clean_combined
working_df.fillna(0, inplace=True)



#Let's do the actual model building
output_summary = 'clf_summary.txt'
if isfile(output_summary):
    destination = (str(datetime.datetime.today())+'_'+output_summary)
    move(output_summary, destination)
f = open(output_summary, 'w')
N = len(working_df[['day_of_week']])
#hand picked
#features = ['is_friday', 'is_saturday', 'week_of_year', 'mean_humidity', 'precipitation', 'mtd_precipitation', 'mean_temp_deviation_from_75', 'max_temp_deviation_from_75', 'heat_index', 'dew_point_high', 'fog_event', 'no_adverse_weather_event', 'rain_event', 'thunderstorm_event', 'in_school', 'days_since_open', 'brewery_events', 'days_since_school_year_start', 'any_truck', 'band', 'band_fans', 'special_event', 'daily_prior', 'yearly_prior', 'yesterday_prior', 'all_sports_games', 'all_sports_home_away', 'football_games', 'football_home_away', 'baseball_games', 'baseball_home_away', 'mens_basketball_games', 'mens_basketball_home_away', 'first_friday', 'holidays', 'in_january', 'in_february', 'in_march', 'in_april', 'in_may', 'in_june', 'in_july', 'in_august', 'in_september', 'in_october', 'in_november', 'in_december', 'in_2013', 'in_2014', 'in_2015', 'in_2016']
#hand picked
features = ['is_friday', 'is_saturday', 'week_of_year', 'mean_humidity', 'precipitation', 'mtd_precipitation', 'mean_temp_deviation_from_75', 'max_temp_deviation_from_75', 'heat_index', 'dew_point_high', 'fog_event', 'no_adverse_weather_event', 'rain_event', 'thunderstorm_event', 'in_school', 'days_since_open', 'brewery_events', 'days_since_school_year_start', 'any_truck', 'band', 'band_fans', 'daily_prior', 'yearly_prior', 'yesterday_prior', 'all_sports_games', 'all_sports_home_away', 'football_games', 'football_home_away', 'baseball_games', 'baseball_home_away', 'mens_basketball_games', 'mens_basketball_home_away', 'first_friday', 'holidays', 'in_january', 'in_february', 'in_march', 'in_april', 'in_may', 'in_june', 'in_july', 'in_august', 'in_september', 'in_october', 'in_november', 'in_december', 'in_2013', 'in_2014', 'in_2015', 'in_2016']

#ALL THE FEATURES!!!! Except 'daily_subtotal', 'daily_tax', 'daily_gratuity', 'daily_grand_total', 'number_of_customers'
# features = []
# for feature in list(rescaled.columns.values):
#     #these are the things we're trying to predict, so cut them out.
#     if (feature != 'events') & (feature != 'daily_subtotal') & (feature != 'daily_tax') & (feature != 'daily_gratuity') & (feature != 'daily_grand_total') & (feature != 'number_of_customers') & (feature != 'number_of_bartenders'):
#         #these features have got to be crap, might as well throw them away now.
#         if (feature != 'month') & (feature != 'day') & (feature != 'year') & (feature != 'month') & (feature != 'avg_mean_temp') & (feature != 'avg_min_temp') & (feature != 'avg_max_temp') & (feature != 'heating_degree_days') & (feature !=  'avg_heating_degree_days') & (feature != 'mtd_heating_degree_days') & (feature != 'avg_mtd_heating_degree_days') & (feature != 'july_one_heating_degree_days') & (feature != 'avg_july_one_heating_degree_days') & (feature != 'cooling_degree_days') & (feature != 'avg_cooling_degree_days') & (feature != 'mtd_cooling_degree_days') & (feature != 'avg_mtd_cooling_degree_days') & (feature != 'ytd_cooling_degree_days') & (feature != 'avg_ytd_cooling_degree_days') & (feature != 'avg_precipitation') & (feature != 'avg_mtd_precipitation') & (feature != 'avg_ytd_precipitation') & (feature != 'cumulative_precipitation'):
#             features.append(feature)
        
#optimal features via univariate feature selection
#features = ['brewery_events', 'daily_prior', 'yearly_prior', 'year', 'days_since_open', 'in_2016', 'band', 'in_april']
#or
#features = ['yearly_prior', 'daily_prior', 'in_2014', 'yesterday_prior', 'in_2013', 'brewery_events', 'ytd_cooling_degree_days', 'mean_humidity', 'in_april', 'min_humidity', 'days_since_school_year_start', 'band', 'none', 'baseball_games', 'football_home_away', 'max_gust_speed', 'avg_july_one_heating_degree_days', 'baseball_home_away', 'band_fans', 'day', 'any_truck', 'first_week_of_month', 'avg_ytd_cooling_degree_days', 'temp_max_minus_mean', 'year', 'in_2016', 'days_since_open']

#optimal features via rfecv
#features = ['day', 'mean_humidity', 'precipitation', 'max_gust_speed', 'july_one_heating_degree_days', 'avg_july_one_heating_degree_days', 'avg_mtd_precipitation', 'ytd_precipitation', 'visibility', 'fog_event', 'brewery_events', 'fourth_week_of_month', 'Goats Catering', 'Many', "Mickey's Sliders", 'Napa Flats', 'Potato Shack', 'Wafology', 'band', 'daily_prior', 'football_home_away', 'in_june', 'in_2016']
#this looks like crap, I'm going to prune it by hand and see if that improves things
#features = ['mean_humidity', 'precipitation', 'max_gust_speed', 'fog_event', 'brewery_events', 'fourth_week_of_month', 'none', 'band', 'daily_prior', 'football_home_away', 'in_june', 'in_2016']

number_of_features = len(features)
#print('Initial number of features: '+str(number_of_features))
X = np.zeros((N,number_of_features))
for index, feature in enumerate(features):
    X[:,index] = ((working_df[[feature]].values.reshape(1,-1))[0])

z = ((working_df[['daily_subtotal']].values.reshape(1,-1))[0]) #revenue

min_rms = 1000
for dice_roll in xrange(1000):
    Xtrain, Xtest, ztrain, ztest = train_test_split(X, z, test_size=0.7)
    clf = Lasso(alpha=0.005, fit_intercept=False, normalize=True, max_iter=100000, tol=0.000001, selection='random') #190
    clf.fit(Xtrain, ztrain)
    zpred = clf.predict(Xtest)
    model = SelectFromModel(clf, prefit=True)
    Xtrain_new = model.transform(Xtrain)
    Xtest_new = model.transform(Xtest)
    features_new = model.transform(features)
    clf_two = Lasso(alpha=0.005, fit_intercept=False, normalize=True, max_iter=100000, tol=0.000001, selection='random') #190
    clf_two = ElasticNet(alpha=0.005, fit_intercept=False, normalize=True, max_iter=10000, tol=0.000001, selection='random') #180
    #clf_two = SVR(kernel='linear') #this seems to error most often the way I want it to
    clf_two.fit(Xtrain_new, ztrain)
    zpred = clf_two.predict(Xtest_new)

    rms = np.sqrt(np.mean((ztest - zpred) ** 2))
    unscaler = 1
    if rms < 1:
        unscaler = combined['daily_subtotal'].max()
    if rms < min_rms:
        min_rms = rms
        min_model = model
        min_clf = clf_two
        min_zpred = zpred
        min_ztest = ztest
        min_Xtrain = Xtrain_new
        min_Xtest = Xtest_new
        min_features = features_new
 
print(min_features)
f.write('[')
#for selected in (min_features):
for selected in np.array(min_model.get_support(indices=True)):
	f.write("'")
	f.write(features[selected])
	f.write("', ")
f.write(']\n')
f.write('RMS: '+str(min_rms*unscaler)+'\n')
#f.write('Features being used: \n')
#for selected in np.array(min_model.get_support(indices=True)):
#    f.write(features[selected]+'\n')

slop = 0
correct_guess = 0

better_than_100 = 0
worse_than_100 = 0
for z_index, test_value in enumerate(min_ztest):
    difference = abs(min_ztest[z_index] - min_zpred[z_index])*unscaler
    if difference < 100:
        better_than_100 += 1
    else:
        worse_than_100 += 1
    if min_ztest[z_index]*unscaler < bartender_cutoff+slop:
        if min_zpred[z_index]*unscaler < bartender_cutoff+slop:
            correct_guess += 1 
    if min_ztest[z_index]*unscaler > bartender_cutoff-slop:
        if min_zpred[z_index]*unscaler > bartender_cutoff-slop:
            correct_guess += 1 
            
f.write('Percent better within $100: '+str(round(100*float(better_than_100)/(better_than_100+worse_than_100),2))+'\n')
f.write('Percent of predictions consistent with actually needed number of bartenders: '+str(round(100*float(correct_guess)/(better_than_100+worse_than_100),2))+'\n')
print(min_Xtest[0])

plt.scatter(ztest*unscaler, zpred*unscaler)
plt.plot(ztest.max()/(xrange(1000))*unscaler,ztest.max()/(xrange(1000))*unscaler)
plt.plot([0,bartender_cutoff],[bartender_cutoff,bartender_cutoff], color='green')
plt.plot([bartender_cutoff,bartender_cutoff],[0,bartender_cutoff], color='green')
plt.plot([0,0],[0,bartender_cutoff], color='green')
plt.plot([0,bartender_cutoff],[0,0], color='green')
plt.plot([ztest.max()*unscaler,bartender_cutoff],[bartender_cutoff,bartender_cutoff], color='green')
plt.plot([bartender_cutoff,bartender_cutoff],[ztest.max()*unscaler,bartender_cutoff], color='green')
plt.plot([ztest.max()*unscaler,ztest.max()*unscaler],[ztest.max()*unscaler,bartender_cutoff], color='green')
plt.plot([ztest.max()*unscaler,bartender_cutoff],[ztest.max()*unscaler,ztest.max()*unscaler], color='green') 
plt.xlabel("Truth")
plt.ylabel("Prediction")
plt.title("Visualizing predicted vs true values")
plt.xlim(-10,ztest.max()*unscaler+10)
plt.ylim(-10,ztest.max()*unscaler+10)

check_figure = 'clf_results.png'
if isfile(check_figure):
    destination = (str(datetime.datetime.today())+'_'+check_figure)
    move(check_figure, destination)
plt.savefig(check_figure)

#good_model = pickle.dumps(min_clf)
##Impliment a feature where it checks if a good model already exists, and if it does, it renames it, and then saves a new one
good_classifier = 'good_clf.p'
if isfile(good_classifier):
    destination = (str(datetime.datetime.today())+'_'+good_classifier)
    move(good_classifier, destination)
pickle.dump(min_clf, open(good_classifier, "wb"))