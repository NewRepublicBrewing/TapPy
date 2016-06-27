import tappy_sql_connection
import pandas as pd
import urllib2
from bs4 import BeautifulSoup

sql_query = """
SELECT * FROM transactions;
"""
individual_sales_df = pd.read_sql_query(sql_query,tappy_sql_connection.conn)

tappy_sql_connection.cur.execute(" CREATE TABLE weather \
(datekey INT PRIMARY KEY, mean_temp INT, avg_mean_temp INT, min_temp INT, avg_min_temp INT,\
 max_temp INT, avg_max_temp INT, mean_humidity INT,\
 min_humidity INT, max_humidity INT, dew_point INT, precipitation REAL, wind_speed INT,\
 max_wind_speed INT, max_gust_speed INT, events text[], heating_degree_days INT, \
 avg_heating_degree_days INT, mtd_heating_degree_days INT, avg_mtd_heating_degree_days INT,\
 july_one_heating_degree_days INT, avg_july_one_heating_degree_days INT, cooling_degree_days INT,\
 avg_cooling_degree_days INT, mtd_cooling_degree_days INT, avg_mtd_cooling_degree_days INT,\
 ytd_cooling_degree_days INT, avg_ytd_cooling_degree_days INT, avg_precipitation REAL,\
 mtd_precipitation REAL, avg_mtd_precipitation REAL, ytd_precipitation REAL, \
 avg_ytd_precipitation REAL, sea_level_pressure REAL, visibility INT, problem_flag INT);")
 
years_of_interest = individual_sales_df['year'].unique()
for year in years_of_interest:
    for month in ((individual_sales_df[individual_sales_df.year == year])['month'].unique()):
        #for month in [3]:
        for day in (((individual_sales_df[(individual_sales_df.year == year) & (individual_sales_df.month == month)])['day'].unique())):
            #for day in [13]:
            datekey = str(year)+str(month).zfill(2)+str(day).zfill(2)
            sql_query = """
                SELECT * FROM weather WHERE datekey=%s;
                """
            data = (datekey, )
            tappy_sql_connection.cur.execute(sql_query, data)
            rows = tappy_sql_connection.cur.fetchall()
            if (len(rows)) == 0:
                # Open wunderground.com url
                url = 'http://www.wunderground.com/history/airport/KCLL/'+str(year)+'/'+str(month).zfill(2)+'/'+str(day).zfill(2)+'/DailyHistory.html'
                print(url)
                page = urllib2.urlopen(url)

                # Get temperature from page
                soup = BeautifulSoup(page, "html.parser")

                ##
                ##Variables to Collect
                ##
                # dayTemp = soup.body.nobr.b.string
                mean_temp = soup.find("span", text="Mean Temperature").parent.find_next_sibling("td").get_text(strip=True)
                avg_mean_temp = soup.find("span", text="Mean Temperature").parent.find_next_sibling("td").find_next_sibling("td").get_text(strip=True)
                min_temp = soup.find("span", text="Min Temperature").parent.find_next_sibling("td").get_text(strip=True)
                avg_min_temp = soup.find("span", text="Min Temperature").parent.find_next_sibling("td").find_next_sibling("td").get_text(strip=True)
                max_temp = soup.find("span", text="Max Temperature").parent.find_next_sibling("td").get_text(strip=True)
                avg_max_temp = soup.find("span", text="Max Temperature").parent.find_next_sibling("td").find_next_sibling("td").get_text(strip=True)
                mean_humidity = soup.find("span", text="Average Humidity").parent.find_next_sibling("td").get_text(strip=True)
                min_humidity = soup.find("span", text="Minimum Humidity").parent.find_next_sibling("td").get_text(strip=True)
                max_humidity = soup.find("span", text="Maximum Humidity").parent.find_next_sibling("td").get_text(strip=True)
                dew_point = soup.find("span", text="Dew Point").parent.find_next_sibling("td").get_text(strip=True)
                precipitation = soup.find("span", text="Precipitation").parent.find_next_sibling("td").get_text(strip=True)
                wind_speed = soup.find("span", text="Wind Speed").parent.find_next_sibling("td").get_text(strip=True)
                max_wind_speed = soup.find("span", text="Max Wind Speed").parent.find_next_sibling("td").get_text(strip=True)
                max_gust_speed = soup.find("span", text="Max Gust Speed").parent.find_next_sibling("td").get_text(strip=True)
                events = soup.find("span", text="Events").parent.find_next_sibling("td").get_text(strip=True)
                heating_degree_days = soup.find("span", text="Heating Degree Days").parent.find_next_sibling("td").get_text(strip=True)
                avg_heating_degree_days = soup.find("span", text="Heating Degree Days").parent.find_next_sibling("td").find_next_sibling("td").get_text(strip=True)
                mtd_heating_degree_days = soup.find("span", text="Month to date heating degree days").parent.find_next_sibling("td").get_text(strip=True)
                avg_mtd_heating_degree_days = soup.find("span", text="Month to date heating degree days").parent.find_next_sibling("td").find_next_sibling("td").get_text(strip=True)
                july_one_heating_degree_days = soup.find("span", text="Since 1 July heating degree days").parent.find_next_sibling("td").get_text(strip=True)
                avg_july_one_heating_degree_days = soup.find("span", text="Since 1 July heating degree days").parent.find_next_sibling("td").find_next_sibling("td").get_text(strip=True)
                cooling_degree_days = soup.find("span", text="Cooling Degree Days").parent.find_next_sibling("td").get_text(strip=True)
                avg_cooling_degree_days = soup.find("span", text="Cooling Degree Days").parent.find_next_sibling("td").find_next_sibling("td").get_text(strip=True)
                mtd_cooling_degree_days = soup.find("span", text="Month to date cooling degree days").parent.find_next_sibling("td").get_text(strip=True)
                avg_mtd_cooling_degree_days = soup.find("span", text="Month to date cooling degree days").parent.find_next_sibling("td").find_next_sibling("td").get_text(strip=True)
                ytd_cooling_degree_days = soup.find("span", text="Year to date cooling degree days").parent.find_next_sibling("td").get_text(strip=True)
                avg_ytd_cooling_degree_days = soup.find("span", text="Year to date cooling degree days").parent.find_next_sibling("td").find_next_sibling("td").get_text(strip=True)
                #growing_degree_days = soup.find("span", text="Growing Degree Days").parent.find_next_sibling("td").get_text(strip=True)
                avg_precipitation = soup.find("span", text="Precipitation").parent.find_next_sibling("td").find_next_sibling("td").get_text(strip=True)
                mtd_precipitation = soup.find("span", text="Month to date precipitation").parent.find_next_sibling("td").get_text(strip=True)
                avg_mtd_precipitation = soup.find("span", text="Month to date precipitation").parent.find_next_sibling("td").find_next_sibling("td").get_text(strip=True)
                ytd_precipitation = soup.find("span", text="Year to date precipitation").parent.find_next_sibling("td").get_text(strip=True)
                avg_ytd_precipitation = soup.find("span", text="Year to date precipitation").parent.find_next_sibling("td").find_next_sibling("td").get_text(strip=True)
                sea_level_pressure = soup.find("span", text="Sea Level Pressure").parent.find_next_sibling("td").get_text(strip=True)
                visibility = soup.find("span", text="Visibility").parent.find_next_sibling("td").get_text(strip=True)

                problem_flag = 0
                
                if precipitation == 'Tin':
                    precipitation = '0.001in'
                if mtd_precipitation == 'T':
                    mtd_precipitation = 0.001
                if ytd_precipitation == 'T':
                    ytd_precipitation = 0.001
                if max_gust_speed == '-':
                    max_gust_speed = '0mph'
                if mtd_heating_degree_days == '':
                    mtd_heating_degree_days = 0
                    problem_flag = 1
                if july_one_heating_degree_days == '':
                    july_one_heating_degree_days = 0
                    problem_flag = 1
                if mtd_cooling_degree_days == '':
                    mtd_cooling_degree_days = 0
                    problem_flag = 1
                if ytd_cooling_degree_days == '':
                    ytd_cooling_degree_days = 0
                    problem_flag = 1
                if mtd_precipitation == '':
                    mtd_precipitation = 0
                    problem_flag = 1
                if ytd_precipitation == '':
                    ytd_precipitation = 0
                    problem_flag = 1
            
                
                query = 'INSERT INTO weather (datekey, mean_temp, avg_mean_temp, min_temp, avg_min_temp,\
                    max_temp, avg_max_temp, mean_humidity,\
                    min_humidity, max_humidity, dew_point, precipitation, wind_speed,\
                    max_wind_speed, max_gust_speed, events, heating_degree_days, \
                    avg_heating_degree_days, mtd_heating_degree_days, avg_mtd_heating_degree_days,\
                    july_one_heating_degree_days, avg_july_one_heating_degree_days, cooling_degree_days,\
                    avg_cooling_degree_days, mtd_cooling_degree_days, avg_mtd_cooling_degree_days,\
                    ytd_cooling_degree_days, avg_ytd_cooling_degree_days, avg_precipitation,\
                    mtd_precipitation, avg_mtd_precipitation, ytd_precipitation, \
                    avg_ytd_precipitation, sea_level_pressure, visibility, problem_flag) VALUES (%s, %s, %s, %s, %s, \
                    %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s);'
                data=( datekey, int(mean_temp[:-2]), int(avg_mean_temp[:-2]), int(min_temp[:-2]), int(avg_min_temp[:-2]), int(max_temp[:-2]), \
                    int(avg_max_temp[:-2]), int(mean_humidity), int(min_humidity), int(max_humidity), int(dew_point[:-2]), float(precipitation[:-2]), \
                    int((wind_speed.split('mph'))[0]), int((max_wind_speed.split('mph'))[0]), int((max_gust_speed.split('mph'))[0]), '{'+str(events)+'}', int(heating_degree_days), \
                    int(avg_heating_degree_days),  int(mtd_heating_degree_days), int(avg_mtd_heating_degree_days), int(july_one_heating_degree_days), \
                    int(avg_july_one_heating_degree_days), int(cooling_degree_days), int(avg_cooling_degree_days), int(mtd_cooling_degree_days), \
                    int(avg_mtd_cooling_degree_days), int(ytd_cooling_degree_days), int(avg_ytd_cooling_degree_days), float(avg_precipitation[:-2]), \
                    float(mtd_precipitation), float(avg_mtd_precipitation), float(ytd_precipitation), float(avg_ytd_precipitation), float(sea_level_pressure[:-2]), \
                    int(visibility[:-5]), int(problem_flag))

                try:
                    tappy_sql_connection.cur.execute(query,data)
                    tappy_sql_connection.conn.commit()
                except:
                    print('ERROR HAPPENED')
                    tappy_sql_connection.conn.rollback()