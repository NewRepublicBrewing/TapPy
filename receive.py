import os
from flask import Flask, request, Response
from slackclient import SlackClient
import random
from make_prediction import predict_by_weekday
import tappy_settings
#import tappy_sql_connection


#SLACK_TOKEN = os.environ.get('SLACK_TOKEN')


slack_client = SlackClient(tappy_settings.SLACK_TOKEN)

app = Flask(__name__)

#SLACK_WEBHOOK_SECRET = os.environ.get('SLACK_WEBHOOK_SECRET') #webhook integration



####
def channel_info(channel_id):
	channel_info = slack_client.api_call("channels.info", channel=channel_id)
	print(channel_info)
	return None
def send_message(channel_id, message):
	slack_client.api_call(
		"chat.postMessage",
		channel=channel_id,
		text=message,
		username='Project-Delta-Night',
		icon_emoji=':unicorn_face:'
	)

@app.route('/slack', methods=['POST'])
def inbound():
	if request.form.get('token') == tappy_settings.SLACK_WEBHOOK_SECRET:
		beers = ['Dammit Jim!', 'Kadigan', 'Whipsaw', 'Marlinspike', 'Skylight']
		random_beer = random.choice(beers)
		channel = request.form.get('channel_name')
		username = request.form.get('user_name')
		text = request.form.get('text')
		inbound_message = username + " in " + channel + " says: " + text
		print(inbound_message)
		channel_id = request.form.get('channel_id')
		if text == 'ping':
			message = "Pong"
			message = '-Input command: "'+text+'" by '+username+'-'+'\n'+message
			send_message(channel_id, message)
		elif text.lower() == 'friday':
			date, value = predict_by_weekday(text.lower())
			number_of_bartenders = 1
			if value > 600:
				number_of_bartenders = 2
			message = "For this "+date.strftime("%A")+", "+date.strftime("%B")+" "+str(date.day)+"th "+str(date.year)+", I predict we will do $"+str(value)+" in tap room sales.  Therefore I recommend scheduling "+str(number_of_bartenders)+" bartender(s)."
			message = '-Input command: "'+text+'" by '+username+'-'+'\n'+message
			send_message(channel_id, message)
		elif text.lower() == 'saturday':
			date, value = predict_by_weekday(text.lower())
			number_of_bartenders = 1
			if value > 600:
				number_of_bartenders = 2
			message = "For this "+date.strftime("%A")+", "+date.strftime("%B")+" "+str(date.day)+"th "+str(date.year)+", I predict we will do $"+str(value)+" in tap room sales.  Therefore I recommend scheduling "+str(number_of_bartenders)+" bartender(s)."
			message = '-Input command: "'+text+'" by '+username+'-'+'\n'+message
			send_message(channel_id, message)
		elif text.lower() == 'can we fuck sheep?':
			message = "No, sheep have standards."
			message = '-Input command: "'+text+'" by '+username+'-'+'\n'+message
			send_message(channel_id, message)
		elif text.lower() == 'can we fuck sheep':
			message = "No, sheep have standards."
			message = '-Input command: "'+text+'" by '+username+'-'+'\n'+message
			send_message(channel_id, message)
		else:
			#message = "I don't know what the fuck you're talking about."
			message = "Sorry, I don't understand what that means.  Why not relax and have a delicious "+random_beer+" while my programmer considers your question, "+username+"?"
			message = '-Input command: "'+text+'" by '+username+'-'+'\n'+message
			if username == 'jfbg':
				message = '-Input command: "'+text+'" by '+username+'-'+'\n'+"Why are you trying to break me JF?"
			send_message(channel_id, message)
	return Response(), 200

@app.route('/', methods=['GET'])
def test():
	return Response('It works!')

if __name__ == "__main__":
	app.run(debug=True)

