from slackclient import SlackClient
import tappy_settings

slack_client = SlackClient(tappy_settings.SLACK_TOKEN)

channel_id = 'C1L28ETUH'

def send_message(message, username, emoji):
    slack_client.api_call(
    "chat.postMessage",
    channel=channel_id,
    text=message,
    username=username,
    icon_emoji=emoji)
    
message = "I use the ice chest this morning. Left it open to dry out.  If still wet when you open today then put it in the sun(open) to dry.  Put it back under the stairs when dry. Thanks."
username = 'Dean'
emoji = ':full_moon_with_face:'
send_message(message, username, emoji)

message = "I'm stil going to open just no food. Band wants to play anyways I spoke to them last night. And I know a few folks who are coming to see the band so hopefully a litle bit of sales"
username = 'Kaleigh'
emoji = ':japanese_ogre:'
send_message(message, username, emoji)

message = "@jimmy is predicting 80-90 people for sour night.  That's total, so I think selling a max of 70 8oz packages is the way to go."
username = 'John'
emoji = ':alien:'
send_message(message, username, emoji)

message = "A couple things that need to happen before we start the sours. Are there checkins for each of the beers on untappd yet? If there are not sheets printed out explaining the event/beers/pricing I can try and whip something up quick before I open at 2. Also I heard talk about having different release times for the beers? If I'm forgetting something let me know"
username = 'Aaron'
emoji = ':ghost:'
send_message(message, username, emoji)

message = "Also need to talk about staff drinking. While I would love to drink the sours all night, the event is to make money. So we need to discuss how much staff can drink since it will directly affect how much we have for sale.  (The small batches do have a couple extra gallons but it's still something to keep in mind)"
username = 'John'
emoji = ':alien:'
send_message(message, username, emoji)

message = 'How did we do on Saturday?'
username = 'Aaron'
emoji = ':ghost:'
send_message(message, username, emoji)

message = 'Something around $1,500 I think.'
username = 'John'
emoji = ':alien:'
send_message(message, username, emoji)

message = 'Nice! We need to do more events like that.'
username = 'Aaron'
emoji = ':ghost:'
send_message(message, username, emoji)
    
message = 'I am having a very hard time getting a food truck saturday!'
username = 'Kaleigh'
emoji = ':japanese_ogre:'
send_message(message, username, emoji)

message = 'Ok. Would you figure out what we need to do to pull a temporary food permit? May have to just sell pizza'
username = 'Dean'
emoji = ':full_moon_with_face:'
send_message(message, username, emoji)

message = 'I got contacted by the comedy group. Do we want to open on a thrusday night for it or a regular friday?'
username = 'Kaleigh'
emoji = ':japanese_ogre:'
send_message(message, username, emoji)

message = 'Sure.  Is this the person Nick knows or someone else?  Maybe we do comedy Thursdays twice a month?'
username = 'John'
emoji = ':alien:'
send_message(message, username, emoji)

message = 'Anyone opposed if I stay late tomorrow night at the brewery and let some alcoholic firefighters come buy pints and hangout? All on me to open and close?'
username = 'Aaron'
emoji = ':ghost:'
send_message(message, username, emoji)

message = "Beer drinking firefighters are fine with me.  If they're alcoholic, they probably should meet somewhere else with sponsors and tokens."
username = 'John'
emoji = ':alien:'
send_message(message, username, emoji)

message = "Do we have a prediction for how much we're going to do on Friday?"
username = 'Dean'
emoji = ':full_moon_with_face:'
send_message(message, username, emoji)