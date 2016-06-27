import psycopg2

#pull in important variables stored in the local settings file
import tappy_settings
#Need to have at least these defined: host, user, password, database

#check to see if the database exists for the project, if not, make it.
## 'engine' is a connection to a database
## Here, we're using postgres, but sqlalchemy can connect to other things too.
#engine = create_engine('postgresql://%s:%s@localhost/%s'%(user,password,database))
#print(engine.url)

## create a database (if it doesn't exist)
#if not database_exists(engine.url):
#    create_database(engine.url)
#print('Able to connect to database?: '+str(database_exists(engine.url)))

#print(tappy_settings.user)

#Try connecting to the database, if it fails, report that something isn't working
try:
    conn = psycopg2.connect(database = tappy_settings.database, user = tappy_settings.user, host=tappy_settings.host, password=tappy_settings.password)
except:
    print("I am unable to connect to the database")
    
cur = conn.cursor()