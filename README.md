# TapPy
A bot to predict tap room revenues for the upcoming weekend.

Built as part of the Insight Data Science 3 week project, this bot uses historical transaction data, weather data, and more to predict tap room revenue for a local micro-brewery.

Not included with this repo, but necessary for TapPy to work is a tappy_settings.py file.  This will contain all the important usernames, passwords, and api keys.

Should look something like this:

host = 'localhost'

user = 'username'

password = 'password'

database = 'tappy_db'

wunderground_key = 'keyhere'

SLACK_TOKEN = 'tokenhere'

SLACK_WEBHOOK_SECRET = 'webhookhere' 
