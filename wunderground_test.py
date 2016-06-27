import urllib2
import json
from bs4 import BeautifulSoup
import datetime
import tappy_settings

month = 6
day = 28
year = 2016


if datetime.date(int(year), int(month), int(day)) == datetime.date.today():
	today = 1
else:
	today = 0

#Predicted values
f = urllib2.urlopen('http://api.wunderground.com/api/'+tappy_settings.wunderground_key+'/forecast10day/q/TX/College_Station.json')
json_string = f.read()
parsed_json = json.loads(json_string)
for forecast in (parsed_json['forecast']['simpleforecast']['forecastday']):
	if (forecast['conditions'] != 'Clear') & (forecast['conditions'] != 'Partly Cloudy'):
		print(forecast['conditions'])
	if (forecast['date']['day'] == day) & (forecast['date']['month'] == month) & (forecast['date']['year'] == year):
		mean_humidity = (forecast['avehumidity'])
		period = forecast['period']
		max_humidity = (forecast['maxhumidity'])
		wind_speed = (forecast['avewind'])
		#predicted_snow = (forecast['snow_allday'])
		max_wind_speed = (forecast['maxwind'])
		min_humidity = (forecast['minhumidity'])
		max_temp = (forecast['high'])
		precipitation = (forecast['qpf_allday'])
		min_temp = (forecast['low'])
		#mean_temp = (min_temp+max_temp)/2
f.close()
#print(period)


#Predicted values
f = urllib2.urlopen('http://api.wunderground.com/api/'+tappy_settings.wunderground_key+'/hourly10day/q/TX/College_Station.json')
json_string = f.read()
parsed_json = json.loads(json_string)
for forecast in (parsed_json['hourly_forecast']):
	if (forecast['FCTTIME']['mday'] == str(day)) & (forecast['FCTTIME']['mon'] == str(month)) & (forecast['FCTTIME']['year'] == str(year)) & (forecast['FCTTIME']['hour'] == str(19)):
		dew_point = (forecast['dewpoint']['english'])
		max_gust_speed = (forecast['wspd']['english'])*2 #cheat and hack, probably don't need this variable anyways
f.close()
#print(period)

#Historical values
#this should work, but the API seems to choke on historical data for future events.
#f = urllib2.urlopen('http://api.wunderground.com/api/'+tappy_settings.wunderground_key+'/history_'+str(year)+str(month).zfill(2)+str(day).zfill(2)+'/q/TX/College_Station.json')
#json_string = f.read()
#parsed_json = json.loads(json_string)
##print(parsed_json)
#for forecast in (parsed_json['history']['dailysummary']):
#	print(forecast['monthtodatecoolingdegreedays'])
#	print(forecast['monthtodatecoolingdegreedaysnormal'])



if datetime.date(int(year), int(month), int(day)) == datetime.date.today():
	today = 1
else:
	today = 0

#shitty thing is that this will need to change depending on whether or not the future date is today...
url = 'http://www.wunderground.com/history/airport/KCLL/'+str(year)+'/'+str(month).zfill(2)+'/'+str(day).zfill(2)+'/DailyHistory.html'
#print(url)
page = urllib2.urlopen(url)
soup = BeautifulSoup(page, "html.parser")

if today:
	avg_mean_temp = soup.find("span", text="Mean Temperature").parent.find_next_sibling("td").find_next_sibling("td").get_text(strip=True)
	avg_min_temp = soup.find("span", text="Min Temperature").parent.find_next_sibling("td").find_next_sibling("td").get_text(strip=True)
	avg_max_temp = soup.find("span", text="Max Temperature").parent.find_next_sibling("td").find_next_sibling("td").get_text(strip=True)
	avg_precipitation = soup.find("span", text="Precipitation").parent.find_next_sibling("td").find_next_sibling("td").get_text(strip=True)

else:
	avg_mean_temp = soup.find("span", text="Mean Temperature").parent.find_next_sibling("td").get_text(strip=True)
	avg_min_temp = soup.find("span", text="Min Temperature").parent.find_next_sibling("td").get_text(strip=True)
	avg_max_temp = soup.find("span", text="Max Temperature").parent.find_next_sibling("td").get_text(strip=True)
	avg_precipitation = soup.find("span", text="Precipitation").parent.find_next_sibling("td").get_text(strip=True)

#print(avg_precipitation)


#'mtd_precipitation'
#'avg_mtd_precipitation'
#'ytd_precipitation'
#'avg_ytd_precipitation'
#'sea_level_pressure'
#'visibility'
#'temp_deviation_from_avg'
#'mean_temp_deviation_from_75'
#'max_temp_deviation_from_75'
#'heat_index'
#'temp_max_minus_mean'
#'dew_point_high'
#'fog_event'
#'no_adverse_weather_event'
#'rain_event'
#'snow_event'
#'thunderstorm_event'

#                avg_mean_temp = soup.find("span", text="Mean Temperature").parent.find_next_sibling("td").find_next_sibling("td").get_text(strip=True)
#                min_temp = soup.find("span", text="Min Temperature").parent.find_next_sibling("td").get_text(strip=True)
#                avg_min_temp = soup.find("span", text="Min Temperature").parent.find_next_sibling("td").find_next_sibling("td").get_text(strip=True)
#                max_temp = soup.find("span", text="Max Temperature").parent.find_next_sibling("td").get_text(strip=True)
#                avg_max_temp = soup.find("span", text="Max Temperature").parent.find_next_sibling("td").find_next_sibling("td").get_text(strip=True)
#                mean_humidity = soup.find("span", text="Average Humidity").parent.find_next_sibling("td").get_text(strip=True)
#                min_humidity = soup.find("span", text="Minimum Humidity").parent.find_next_sibling("td").get_text(strip=True)
#                max_humidity = soup.find("span", text="Maximum Humidity").parent.find_next_sibling("td").get_text(strip=True)
#                dew_point = soup.find("span", text="Dew Point").parent.find_next_sibling("td").get_text(strip=True)
#                precipitation = soup.find("span", text="Precipitation").parent.find_next_sibling("td").get_text(strip=True)
#                wind_speed = soup.find("span", text="Wind Speed").parent.find_next_sibling("td").get_text(strip=True)
#                max_wind_speed = soup.find("span", text="Max Wind Speed").parent.find_next_sibling("td").get_text(strip=True)
#                max_gust_speed = soup.find("span", text="Max Gust Speed").parent.find_next_sibling("td").get_text(strip=True)
#                events = soup.find("span", text="Events").parent.find_next_sibling("td").get_text(strip=True)
#                heating_degree_days = soup.find("span", text="Heating Degree Days").parent.find_next_sibling("td").get_text(strip=True)
#                avg_heating_degree_days = soup.find("span", text="Heating Degree Days").parent.find_next_sibling("td").find_next_sibling("td").get_text(strip=True)
#                mtd_heating_degree_days = soup.find("span", text="Month to date heating degree days").parent.find_next_sibling("td").get_text(strip=True)
#                avg_mtd_heating_degree_days = soup.find("span", text="Month to date heating degree days").parent.find_next_sibling("td").find_next_sibling("td").get_text(strip=True)
#                july_one_heating_degree_days = soup.find("span", text="Since 1 July heating degree days").parent.find_next_sibling("td").get_text(strip=True)
#                avg_july_one_heating_degree_days = soup.find("span", text="Since 1 July heating degree days").parent.find_next_sibling("td").find_next_sibling("td").get_text(strip=True)
#                cooling_degree_days = soup.find("span", text="Cooling Degree Days").parent.find_next_sibling("td").get_text(strip=True)
#                avg_cooling_degree_days = soup.find("span", text="Cooling Degree Days").parent.find_next_sibling("td").find_next_sibling("td").get_text(strip=True)
#                mtd_cooling_degree_days = soup.find("span", text="Month to date cooling degree days").parent.find_next_sibling("td").get_text(strip=True)
#                avg_mtd_cooling_degree_days = soup.find("span", text="Month to date cooling degree days").parent.find_next_sibling("td").find_next_sibling("td").get_text(strip=True)
#                ytd_cooling_degree_days = soup.find("span", text="Year to date cooling degree days").parent.find_next_sibling("td").get_text(strip=True)
#                avg_ytd_cooling_degree_days = soup.find("span", text="Year to date cooling degree days").parent.find_next_sibling("td").find_next_sibling("td").get_text(strip=True)
#                #growing_degree_days = soup.find("span", text="Growing Degree Days").parent.find_next_sibling("td").get_text(strip=True)
#                avg_precipitation = soup.find("span", text="Precipitation").parent.find_next_sibling("td").find_next_sibling("td").get_text(strip=True)
#                mtd_precipitation = soup.find("span", text="Month to date precipitation").parent.find_next_sibling("td").get_text(strip=True)
#                avg_mtd_precipitation = soup.find("span", text="Month to date precipitation").parent.find_next_sibling("td").find_next_sibling("td").get_text(strip=True)
#                ytd_precipitation = soup.find("span", text="Year to date precipitation").parent.find_next_sibling("td").get_text(strip=True)
#                avg_ytd_precipitation = soup.find("span", text="Year to date precipitation").parent.find_next_sibling("td").find_next_sibling("td").get_text(strip=True)
#                sea_level_pressure = soup.find("span", text="Sea Level Pressure").parent.find_next_sibling("td").get_text(strip=True)
#                visibility = soup.find("span", text="Visibility").parent.find_next_sibling("td").get_text(strip=True)

