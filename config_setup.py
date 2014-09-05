import hashlib
import time
from bumblebee import botqueueapi
from bumblebee import hive

hive.loadLogger()
config = hive.config.get()

url = raw_input("Server URL: ")

if (url[len(url)-1] == '/'):
	url = url[:-1]

config['app_url'] = url
config['api']['authorize_url'] = url + '/app/authorize'
config['api']['endpoint_url'] = url + '/api/v1/endpoint'

consumer_key = raw_input("Consumer Key: ")
consumer_secret = raw_input("Consumer Secret: ")

config['app']['consumer_key'] = consumer_key
config['app']['consumer_secret'] = consumer_secret

# create a unique hash that will identify this computers requests
if 'uid' not in config or not config['uid']:
	config['uid'] = hashlib.sha1(str(time.time())).hexdigest()


# Save it before continuing
hive.config.save(config)


print "We're about to start the authorization process"

api = botqueueapi.BotQueueAPI()

print "All done!"
print ""
print "Next steps:"
print "Before registering your bot, run the client by using: "
print "python -m bumblebee"
