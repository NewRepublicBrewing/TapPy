import datetime
import pickle
import numpy as np
import urllib2
from bs4 import BeautifulSoup
#from create_classifier import heat_index_calculator
import pandas as pd
import json
import tappy_settings
import tappy_sql_connection

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

    

all_possible_variables = [ 'mean_temp', 'avg_mean_temp', 'min_temp', 'avg_min_temp', 'max_temp', 'avg_max_temp', 'mean_humidity', 'min_humidity', 'max_humidity', 'dew_point', 'precipitation', 'wind_speed', 'max_wind_speed', 'max_gust_speed', 'heating_degree_days', 'avg_heating_degree_days', 'mtd_heating_degree_days', 'avg_mtd_heating_degree_days', 'july_one_heating_degree_days', 'avg_july_one_heating_degree_days', 'cooling_degree_days', 'avg_cooling_degree_days', 'mtd_cooling_degree_days', 'avg_mtd_cooling_degree_days', 'ytd_cooling_degree_days', 'avg_ytd_cooling_degree_days', 'avg_precipitation', 'mtd_precipitation', 'avg_mtd_precipitation', 'ytd_precipitation', 'avg_ytd_precipitation', 'sea_level_pressure', 'visibility', 'problem_flag', 'temp_deviation_from_avg', 'mean_temp_deviation_from_75', 'max_temp_deviation_from_75', 'heat_index', 'temp_max_minus_mean', 'dew_point_high', 'cumulative_precipitation', 'fog_event', 'no_adverse_weather_event', 'rain_event', 'snow_event', 'thunderstorm_event', 'in_school', 'days_since_open', 'brewery_events', 'days_since_school_year_start', 'first_week_of_month', 'fourth_week_of_month', 'second_week_of_month', 'third_week_of_month', 'Big Daddy Zs', 'DBQ', 'Fusion Peru', 'Goats Catering', 'In-between girls', 'Into the Fire Pizza', 'Many', "Mickey's Sliders", 'Napa Flats', 'Pik Pak Push', 'Pin-Toh Thai', 'Potato Shack', 'Raspas', 'Ronin Cooking', 'Sugba', 'Taz', 'Wafology', 'none', 'any_truck', 'band', 'band_fans', 'special_event', 'number_of_bartenders', 'daily_prior', 'yearly_prior', 'yesterday_prior', 'all_sports_games', 'all_sports_home_away', 'football_games', 'football_home_away', 'baseball_games', 'baseball_home_away', 'mens_basketball_games', 'mens_basketball_home_away', 'first_friday', 'holidays', 'in_january', 'in_february', 'in_march', 'in_april', 'in_may', 'in_june', 'in_july', 'in_august', 'in_september', 'in_october', 'in_november', 'in_december', 'in_2013', 'in_2014', 'in_2015', 'in_2016']

def predict_by_weekday(day_name):
	maxes = pd.read_csv('maxes.csv')
	test_day = {}
	if day_name == 'friday':
		day_number = 4
	if day_name == 'saturday':
		day_number = 5
	#given todays date, find the datekey for the upcoming friday and saturday
	day_of_week_today = (datetime.datetime.today().weekday())
	days_until = day_number-day_of_week_today
	upcoming_day = ((datetime.date.today() + datetime.timedelta(days=days_until)))
	week_of_year_today = datetime.datetime.today().isocalendar()[1]

	day = upcoming_day.day
	month = upcoming_day.month
	year = upcoming_day.year
	
	if datetime.date(int(year), int(month), int(day)) == datetime.date.today():
		today = 1
	else:
		today = 0

	test_day['month'] = month
	test_day['day'] = day
	test_day['year'] = year
	test_day['day_of_week'] = datetime.date(year, month, day).weekday()
	test_day['day_of_year'] = datetime.date((year), (month), (day)).timetuple().tm_yday
	test_day['week_of_year'] = datetime.date(year, month, day).isocalendar()[1]
	if test_day['day_of_week'] == 4:
		test_day['is_friday'] = 1
	else:
		test_day['is_friday'] = 0
	if test_day['day_of_week'] == 5:
		test_day['is_saturday'] = 1
	else:
		test_day['is_saturday'] = 0
	
	url = 'http://www.wunderground.com/history/airport/KCLL/'+str(year)+'/'+str(month)+'/'+str(day)+'/DailyHistory.html'
	page = urllib2.urlopen(url)

	#print(url)

	# Get temperature from page
	###soup = BeautifulSoup(page, "html.parser")

	#working
	test_day['days_since_open'] = ((datetime.date(year, month, day)-datetime.date(2013, 9, 6)).days)
	test_day['days_since_school_year_start'] = (datetime.date(year, month, day) - datetime.date(2015,8,31)).days
	if month == 4:
		test_day['in_april'] = 1
	else:
		test_day['in_april'] = 0
	if year == 2016:
		test_day['in_2016'] = 1
	else:
		test_day['in_2016'] = 0
	f = urllib2.urlopen('http://api.wunderground.com/api/'+tappy_settings.wunderground_key+'/forecast10day/q/TX/College_Station.json')
	json_string = f.read()
	parsed_json = json.loads(json_string)
	for forecast in (parsed_json['forecast']['simpleforecast']['forecastday']):
		if (forecast['date']['day'] == day) & (forecast['date']['month'] == month) & (forecast['date']['year'] == year):
			test_day['min_temp'] = int(forecast['low']['fahrenheit'])
			test_day['max_temp'] = int(forecast['high']['fahrenheit'])
			test_day['mean_temp'] = (test_day['min_temp']+test_day['max_temp'])/2
			test_day['mean_humidity'] = (forecast['avehumidity'])
			test_day['no_adverse_weather_event'] = 1
			if (forecast['conditions'] != 'Clear') & (forecast['conditions'] != 'Partly Cloudy'):
				test_day['no_adverse_weather_event'] = 0
			test_day['thunderstorm_event'] = 0
			if (forecast['conditions'] == 'Chance of a Thunderstorm'):
				test_day['thunderstorm_event'] = 1
			test_day['in_school'] = 0
			#Fall 2016 schedule
    		beginning_range = datetime.date(2016, 8, 29)
    		end_range = datetime.date(2016, 12, 14)
    		if beginning_range <= upcoming_day <= end_range:
        		test_day['in_school'] = 1
	f.close()
	
	#currently assuming there will always be a band
	test_day['band'] = 1
	#currently assuming there will not be a special event
	test_day['brewery_events'] = 0
	#currently assuming there will be a food truck
	test_day['any_truck'] = 1
	#currently assuming there will not be a football game
	test_day['football_games'] = 0
	
	sql_query = """
		SELECT * FROM daily_summary;
		"""
	daily_df = pd.read_sql_query(sql_query,tappy_sql_connection.conn)
	day_array = np.array([])
	for prior_index, row in daily_df.iterrows():
		if row['week_of_year'] == test_day['week_of_year']:
			if row['day_of_week'] == test_day['day_of_week']:
				day_array = np.append(day_array,row['daily_subtotal'])
	test_day['daily_prior'] = np.median(day_array)
	
	day_array = np.array([])
	for prior_index, row in daily_df.iterrows():
		if row['year'] == year:
			day_array = np.append(day_array,row['daily_subtotal'])
	test_day['yearly_prior'] = np.median(day_array)

    
	test_day['mean_temp_deviation_from_75'] = np.abs(test_day['mean_temp'] - 75)
	test_day['max_temp_deviation_from_75'] = np.abs(test_day['max_temp'] - 75)
	test_day['heat_index'] = heat_index_calculator(test_day['mean_temp'], test_day['mean_humidity'] )
    

	#features = ['is_friday', 'no_adverse_weather_event', 'thunderstorm_event', 'days_since_open', 'brewery_events', 'days_since_school_year_start', 'any_truck', 'band', 'daily_prior', 'football_home_away', 'in_april', 'in_2016']
	#features = ['is_friday', 'is_saturday', 'week_of_year', 'mean_humidity', 'precipitation', 'mtd_precipitation', 'mean_temp_deviation_from_75', 'max_temp_deviation_from_75', 'heat_index', 'dew_point_high', 'fog_event', 'no_adverse_weather_event', 'rain_event', 'thunderstorm_event', 'in_school', 'days_since_open', 'brewery_events', 'days_since_school_year_start', 'any_truck', 'band', 'band_fans', 'special_event', 'daily_prior', 'yearly_prior', 'yesterday_prior', 'all_sports_games', 'all_sports_home_away', 'football_games', 'football_home_away', 'baseball_games', 'baseball_home_away', 'mens_basketball_games', 'mens_basketball_home_away', 'first_friday', 'in_february', 'in_march', 'in_april', 'in_may', 'in_june', 'in_july', 'in_august', 'in_september', 'in_october', 'in_november', 'in_december', 'in_2013', 'in_2014', 'in_2015', 'in_2016', ]
	#features = ['is_friday', 'no_adverse_weather_event', 'thunderstorm_event', 'in_school', 'days_since_open', 'brewery_events', 'band', 'daily_prior', 'yearly_prior', 'in_april', 'in_2016', ]
	features = ['is_friday', 'no_adverse_weather_event', 'thunderstorm_event', 'in_school', 'days_since_open', 'brewery_events', 'days_since_school_year_start', 'any_truck', 'band', 'daily_prior', 'yearly_prior', 'football_games', 'in_april', 'in_2016', ]

	

	test_day_list = []
	for index, feature in enumerate(features):
		#print(test_day[feature])
		test_day_list.append(test_day[feature]/maxes[feature])

	#date_of_interest = np.array([(datetime.date(2016, 6, 10).weekday()),(datetime.date(2016, 6, 10).isocalendar()[1]),85])
	clf = pickle.load( open( "good_clf.p", "rb" ) )
	tomorrow_pred = clf.predict(np.array(test_day_list).reshape(1, -1))
	#print(np.array(test_day_list).reshape(1, -1))
	return (upcoming_day, round(tomorrow_pred[0]*(maxes['daily_subtotal'])[0],2))

print(predict_by_weekday('friday'))
print(predict_by_weekday('saturday'))