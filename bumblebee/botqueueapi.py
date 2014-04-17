import json
import hive
import logging
import time
from oauth_hook import OAuthHook
import socket
import requests
import urlparse

class NetworkError(Exception):
  pass

class ServerError(Exception):
  pass
  
class AuthError(Exception):
  pass

class BotQueueAPI():
  
  version = '0.4'
  name = 'Bumblebee'
  localip = None
  
  def __init__(self):
    self.log = logging.getLogger('botqueue')
    self.config = hive.config.get()
    self.netStatus = False
    self.netErrors = 0

    #pull in our endpoint urls
    self.authorize_url = self.config['api']['authorize_url']
    self.endpoint_url = self.config['api']['endpoint_url']
    
    # this is helpful for raspberry pi and future websockets stuff
    self.localip = self.getLocalIPAddress()
    
    #create our requests session.
    self.session = requests.session()
    
    # self.consumer = oauth.Consumer(self.config['app']['consumer_key'], self.config['app']['consumer_secret'])
    if 'token_key' in self.config['app'] and self.config['app']['token_key']:
      self.setToken(self.config['app']['token_key'], self.config['app']['token_secret'])
    else:
      self.authorize()

  def setToken(self, token_key, token_secret):
    self.token_key = token_key
    self.token_secret = token_secret
    self.my_oauth_hook = OAuthHook(access_token = token_key, access_token_secret = token_secret, consumer_key=self.config['app']['consumer_key'], consumer_secret=self.config['app']['consumer_secret'])
    
  def apiCall(self, call, parameters = {}, url = False, method = "POST", retries = 999999, filepath = None, ignoreInvalid = False):
    #what url to use?
    if (url == False):
        url = self.endpoint_url
  
    #add in our special variables
    parameters['_client_version'] = self.version
    parameters['_client_name'] = self.name
    parameters['_uid'] = self.config['uid']

    self.localip = self.getLocalIPAddress()
    if self.localip:
      parameters['_local_ip'] = self.localip
    parameters['api_call'] = call
    parameters['api_output'] = 'json'   

    # make the call for as long as it takes.
    while retries > 0:
      respdata = None
      result = None
      try:
        #self.log.debug("Calling %s - %s (%d tries remaining)" % (url, call, retries))
        
        #single file?
        if isinstance(filepath, basestring):
          files = {'file': (filepath, open(filepath, 'rb'))}
        #multiple files?
        elif isinstance(filepath, dict):
          files = {}
          for idx, val in filepath.iteritems():
            files[idx] = (val, open(val, 'rb'))
        elif isinstance(filepath, list):
          files = {}
          for idx, val in enumerate(filepath):
            files[idx] = (val, open(val, 'rb'))
        else:
          files = None

        #prepare and make our request now.
        request = requests.Request('POST', url, data=parameters, files=files)
        request = self.my_oauth_hook(request)
        response = self.session.send(request.prepare(), timeout=600)
        result = response.json()

        #sweet, our request must have gone through.
        self.netStatus = True

        #did we get the right http response code?
        if response.status_code != 200:
          raise ServerError("Bad response code (%s)" % response.status_code)
        
        #did the api itself return an error?
        if result['status'] == 'error':
          self.log.error("API: %s" % result['error'])
          self.log.error(parameters);
          
          #is the site database down?
          if result['error'] == "Failed to connect to database!":
            raise ServerError("Database is down.")
          #shit, de-authed?  re-auth!
          if result['error'] == "Invalid token" and not ignoreInvalid:
            raise AuthError("Token invalid, re-authorizing.")

        return result
        
      #we need to re-auth, do it.
      except AuthError as ex:
        self.log.error(ex)
        self.authorize()
      #these are our known errors that typically mean the network is down.
      except (requests.ConnectionError, requests.Timeout, ServerError) as ex:
        #raise NetworkError(str(ex))
        self.log.error("%s call failed: internet connection is down: %s" % (call, ex))
        self.netError()
        retries = retries - 1
      #unknown exceptions... get a stacktrace for debugging.
      except ValueError as ex:
        self.log.error("%s call failed: value error" % call)
        self.log.exception(ex)
        self.netError(True)
        retries = retries - 1
      except Exception as ex:
        self.log.error("%s call failed: unknown API error: %s" % (call, ex))
        self.log.error("exception: %s.%s" % (ex.__class__, ex.__class__.__name__))
        self.log.exception(ex)
        self.netError()
        retries = retries - 1
    #something bad happened.
    return False
  
  def netError(self, netStatus = False):
    self.netStatus = netStatus
    if not netStatus:
      self.netErrors = self.netErrors + 1
    time.sleep(10)
    
  def requestToken(self):
    #make our token request call or error
    result = self.apiCall('requesttoken', ignoreInvalid = True)

    if result['status'] == 'success':
      self.setToken(result['data']['oauth_token'], result['data']['oauth_token_secret'])
      return result['data']
    else:
      raise Exception("Error getting token: %s" % result['error'])

  def getAuthorizeUrl(self):
    return self.authorize_url + "?oauth_token=" + self.token_key 

  def convertToken(self):
    #switch our temporary auth token for our real credentials
    result = self.apiCall('accesstoken', ignoreInvalid = True)
    if result['status'] == 'success':
      self.setToken(result['data']['oauth_token'], result['data']['oauth_token_secret'])
      return result['data']
    else:
      raise Exception("Error converting token: %s" % result['error'])

  def authorize(self):
    try:
      #Step 0: Initialize to just our consumer key and secret.
      self.my_oauth_hook = OAuthHook(consumer_key=self.config['app']['consumer_key'], consumer_secret=self.config['app']['consumer_secret'])
      
      # Step 1: Get a request token. This is a temporary token that is used for 
      # having the user authorize an access token and to sign the request to obtain 
      # said access token.
      result = self.requestToken();

      # Step 2: Redirect to the provider. Since this is a CLI script we do not 
      # redirect. In a web application you would redirect the user to the URL
      # below.
      print
      print "Please visit BotQueue.com or simply visit this URL to authenticate Bumblebee: %s" % self.getAuthorizeUrl()
      print 
      #webbrowser.open_new(self.getAuthorizeUrl())
  
      authorized = False
      while not authorized:
        try:
          # After the user has granted access to you, the consumer, the provider will
          # redirect you to whatever URL you have told them to redirect to. You can 
          # usually define this in the oauth_callback argument as well.
          #oauth_verifier = raw_input('What is the PIN? ')

          # Step 3: Once the consumer has redirected the user back to the oauth_callback
          # URL you can request the access token the user has approved. You use the 
          # request token to sign this request. After this is done you throw away the
          # request token and use the access token returned. You should store this 
          # access token somewhere safe, like a database, for future use.
          self.convertToken()
          authorized = True

        #we're basically polling the convert function until the user approves it.
        #throwing the exception is totally normal.
        except Exception as ex:
          time.sleep(10)

      #record the key in our config
      self.config['app']['token_key'] = self.token_key
      self.config['app']['token_secret'] = self.token_secret
      hive.config.save(self.config)

    except Exception as ex:
      self.log.exception(ex)
      print "There was a problem authorizing the app: %s" % (ex)
      raise RuntimeError("There was a problem authorizing the app: %s" % (ex))

  def listQueues(self):
    return self.apiCall('listqueues')
    
  def listJobs(self, queue_id):
    return self.apiCall('listjobs', {'queue_id' : queue_id});
    
  def grabJob(self, bot_id, job_id, can_slice):
    return self.apiCall('grabjob', {'bot_id' : bot_id, 'job_id' : job_id, 'can_slice' : can_slice})

  def dropJob(self, job_id, error = False):
    return self.apiCall('dropjob', {'job_id' : job_id, 'error' : error})

  def cancelJob(self, job_id):
    return self.apiCall('canceljob', {'job_id' : job_id})

  def failJob(self, job_id):
    return self.apiCall('failjob', {'job_id' : job_id})

  def createJobFromJob(self, job_id, quantity = 1, queue_id = 0, name = None):
    params = {'job_id' : job_id, 'queue_id' : queue_id, 'quantity': quantity}
    if name:
      params['name'] = name
      
    return self.apiCall('createjob', params)

  def createJobFromURL(self, url, quantity = 1, queue_id = 0, name = None):
    params = {'job_url' : url, 'queue_id' : queue_id, 'quantity': quantity}
    if name:
      params['name'] = name
      
    return self.apiCall('createjob', params)

  def createJobFromFile(self, filename, quantity = 1, queue_id = 0, name = None):
    params = {'quantity': quantity, 'queue_id' : queue_id}
    if name:
      params['name'] = name
      
    return self.apiUploadCall('createjob', params, filepath=filename)
      
  def downloadedJob(self, job_id):
    return self.apiCall('downloadedjob', {'job_id' : job_id})
    
  def completeJob(self, job_id):
    return self.apiCall('completejob', {'job_id' : job_id})
  
  def updateJobProgress(self, job_id, progress, temps = {}):
    return self.apiCall('updatejobprogress', {'job_id' : job_id, 'progress' : progress, 'temperatures' : json.dumps(temps)}, retries = 1)

  def webcamUpdate(self, filename, bot_id = None, job_id = None, progress = None, temps = None):
    return self.apiCall('webcamupdate', {'job_id' : job_id, 'bot_id' : bot_id, 'progress' : progress, 'temperatures' : json.dumps(temps)}, filepath=filename, retries=1)

  def jobInfo(self, job_id):
    return self.apiCall('jobinfo', {'job_id' : job_id})
  
  def listBots(self):
    return self.apiCall('listbots', retries = 1)

  def getMyBots(self):
    return self.apiCall('getmybots', retries = 1)
    
  def sendDeviceScanResults(self, scan_data, camera_files):
    return self.apiCall('devicescanresults', {'scan_data' : json.dumps(scan_data)}, filepath=camera_files)
    
  def findNewJob(self, bot_id, can_slice):
    return self.apiCall('findnewjob', {'bot_id' : bot_id, 'can_slice' : can_slice})
    
  def getBotInfo(self, bot_id):
    return self.apiCall('botinfo', {'bot_id' : bot_id})
    
  def updateBotInfo(self, data):
    return self.apiCall('updatebot', data)
    
  def updateSliceJob(self, job_id=0, status="", output="", errors="", filename=""):
    return self.apiCall('updateslicejob', {'job_id':job_id, 'status':status, 'output':output, 'errors':errors}, filepath=filename)

  def getLocalIPAddress(self):
    try:
      s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
      s.connect(("8.8.8.8",80))
      ip = s.getsockname()[0]
      s.close()
    except socket.error as ex:
      ip = None
    return ip
