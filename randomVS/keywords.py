# -*- coding: utf-8 -*-
import datetime
import httplib2
import os
import sys
import csv
import time

reload(sys);
sys.setdefaultencoding("utf8")


from apiclient.discovery import build
from apiclient.errors import HttpError
from oauth2client.client import flow_from_clientsecrets
from oauth2client.file import Storage
from oauth2client.tools import argparser, run_flow


# The CLIENT_SECRETS_FILE variable specifies the name of a file that contains
# the OAuth 2.0 information for this application, including its client_id and
# client_secret. You can acquire an OAuth 2.0 client ID and client secret from
# the {{ Google Cloud Console }} at
# {{ https://cloud.google.com/console }}.
# Please ensure that you have enabled the YouTube Data and YouTube Analytics
# APIs for your project.
# For more information about using OAuth2 to access the YouTube Data API, see:
#   https://developers.google.com/youtube/v3/guides/authentication
# For more information about the client_secrets.json file format, see:
YOUTUBE_API_SERVICE_NAME = "youtube"
YOUTUBE_API_VERSION = "v3"
DEVELOPER_KEY = 'AIzaSyCVOXKDj8abR6rifF8UsKcnGBzHdtwl_OQ'

# The CLIENT_SECRETS_FILE variable specifies the name of a file that contains
# the OAuth 2.0 information for this application, including its client_id and
# client_secret.
CLIENT_SECRETS_FILE = "client_secret.json"

# This OAuth 2.0 access scope allows for full read/write access to the
# authenticated user's account and requires requests to use an SSL connection.
YOUTUBE_READ_WRITE_SSL_SCOPE = "https://www.googleapis.com/auth/youtube.readonly"
API_SERVICE_NAME = "youtube"
API_VERSION = "v3"

# This variable defines a message to display if the CLIENT_SECRETS_FILE is
# missing.
MISSING_CLIENT_SECRETS_MESSAGE = "WARNING: Please configure OAuth 2.0"

# This variable defines a message to display if the CLIENT_SECRETS_FILE is
# missing.
MISSING_CLIENT_SECRETS_MESSAGE = """
WARNING: Please configure OAuth 2.0

To make this sample run you will need to populate the client_secrets.json file
found at:

   %s

with information from the {{ Cloud Console }}
{{ https://cloud.google.com/console }}

For more information about the client_secrets.json file format, please visit:
https://developers.google.com/api-client-library/python/guide/aaa_client_secrets
""" % os.path.abspath(os.path.join(os.path.dirname(__file__),
                                   CLIENT_SECRETS_FILE))


service = build(YOUTUBE_API_SERVICE_NAME, YOUTUBE_API_VERSION, developerKey=DEVELOPER_KEY)

def getAllVideos(service):
  startTime = time.time()
  request = service.search().list(part='snippet',channelId='UCaWd5_7JhbQBe4dknZhsHJg', maxResults=50, type='video', q="WatchMojo")
  with open("videolist.csv", 'wb') as results:
    writer = csv.writer(results)
    count = 0
    count2 = 0
    while request:

      response = request.execute()
      print "New page"
      
      for result in response.get("items",[]):
        count2 +=1
        pair =[]
        pair.append(result['id']['videoId'])
        writer.writerow(pair)
        print result['id']['videoId']


      count += 1 
      print count   
      request = service.search().list_next(request, response)
  print 'Request took', time.time()-startTime,'seconds.'        

def getKeywordsCount(service, videolist):
  startTime = time.time()
  keyworddict = {}
  with open(videolist+'.csv', 'r') as csvlist:
    reader = csv.reader(csvlist)
    id_list = []
    for row in reader:
      id_list.append(row)
    #print id_list
  with open('keywordsCount.txt','wb') as output:
    count = 1
    for item in id_list:
      sys.stdout.write('\rCurrently getting tags for: %s Progress: %i/%i' % (str(item[0]), int(count), int(len(id_list))))
      sys.stdout.flush()
      response = service.videos().list(
        id=item[0],
        part='snippet').execute()
      tags = response["items"][0]["snippet"]["tags"]
      #print tags
      for tag in tags:
        keyworddict[tag] = keyworddict.get(tag,0) + 1
      count += 1  
    for item in keyworddict:
      output.write(item+' '+str(keyworddict[item])+'\n')    
  print ''    
  print 'Request took', time.time()-startTime,'seconds.'

def getKeywords(service, videolist):
  startTime = time.time()
  keyworddict = {}
  with open(videolist+'.csv', 'r') as csvlist:
    reader = csv.reader(csvlist)
    id_list = []
    for row in reader:
      id_list.append(row)
    #print id_list
  with open('keywords.txt','wb') as output:
    count = 1
    for item in id_list:
      sys.stdout.write('\rCurrently getting tags for: %s Progress: %i/%i' % (str(item[0]), int(count), int(len(id_list))))
      sys.stdout.flush()
      response = service.videos().list(
        id=item[0],
        part='snippet').execute()
      tags = response["items"][0]["snippet"]["tags"]
      #print tags
      for tag in tags:
      	tag = tag.lower()
        keyworddict[tag] = keyworddict.get(tag,0) + 1
      count += 1  
    for item in keyworddict:
      output.write(item+'\n')    
  print ''    
  print 'Request took', time.time()-startTime,'seconds.'          

#getAllVideos(service)
getKeywords(service,'videolist')
