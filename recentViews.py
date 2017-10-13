#!/usr/bin/python

# This script returns the 'views' metric for videos in a given CSV list.
# For each individual video, the script returns the aggregate values from 
# a set period of time the beginning date of which is a certain amount of days
# before the present day.

# You also need to create yourself a client_secrets.json using the Google Developers Dashboard.
# Follow the instructions on how to use the YouTube API to create one.

# By default the script reads from a file called 'videolist.csv' and outputs
# to a file called 'output.csv.' The names of these files can be changed using
# the arguments --source and --output, respectively. 

# Also by default, the script returns the last 7 day values. This can be changed
# with the argument --count. 


# Example usage:
# YourComputer:yourDirectory you$ python recentViews.py --source="myVids.csv" --output="myData.csv" --count=30

import datetime
import httplib2
import os
import sys
import csv
import time

from apiclient.discovery import build
from apiclient.errors import HttpError
from oauth2client.client import flow_from_clientsecrets
from oauth2client.file import Storage
from oauth2client.tools import argparser, run_flow
startTime = time.time()

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
#   https://developers.google.com/api-client-library/python/guide/aaa_client_secrets
CLIENT_SECRETS_FILE = "client_secrets.json"

# These OAuth 2.0 access scopes allow for read-only access to the authenticated
# user's account for both YouTube Data API resources and YouTube Analytics Data.
YOUTUBE_SCOPES = ["https://www.googleapis.com/auth/youtube.readonly",
  "https://www.googleapis.com/auth/yt-analytics.readonly"]
YOUTUBE_API_SERVICE_NAME = "youtube"
YOUTUBE_API_VERSION = "v3"
YOUTUBE_ANALYTICS_API_SERVICE_NAME = "youtubeAnalytics"
YOUTUBE_ANALYTICS_API_VERSION = "v1"

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


def get_authenticated_services(args):
  flow = flow_from_clientsecrets(CLIENT_SECRETS_FILE,
    scope=" ".join(YOUTUBE_SCOPES),
    message=MISSING_CLIENT_SECRETS_MESSAGE)

  storage = Storage("%s-oauth2.json" % sys.argv[0])
  credentials = storage.get()

  if credentials is None or credentials.invalid:
    credentials = run_flow(flow, storage, args)

  http = credentials.authorize(httplib2.Http())

  youtube = build(YOUTUBE_API_SERVICE_NAME, YOUTUBE_API_VERSION,
    http=http)
  youtube_analytics = build(YOUTUBE_ANALYTICS_API_SERVICE_NAME,
    YOUTUBE_ANALYTICS_API_VERSION, http=http)

  return (youtube, youtube_analytics)

def get_channel_id(youtube):
  channels_list_response = youtube.channels().list(
    mine=True,
    part="id"
  ).execute()

  return channels_list_response["items"][0]["id"]

def getLastDay():
  pubDate = str(datetime.datetime.now())
  pubDate = pubDate[0:10]
  return pubDate


def getName(youtube,videoid):
  videoname=''
  response = youtube.videos().list(
    id=videoid,
    part='snippet'
    ).execute()
  videoname = response["items"][0]["snippet"]["title"]
  return videoname

def queryVideo(youtube_analytics,channel_id, videoid,startdate,enddate):
  analytics_query_response = youtube_analytics.reports().query(
    ids="channel==%s" % channel_id,
    metrics="views",
    dimensions='video',
    start_date=startdate,
    end_date=enddate,
    max_results=10,
    sort='-views',
    filters='video==%s' % videoid
    ).execute()
  return analytics_query_response

def getFirstDay():
  count = int(args.count)-1
  endDate = datetime.datetime.now()
  endDate = (endDate - datetime.timedelta(days=count)).strftime("%Y-%m-%d")
  endDate = endDate[0:10]
  return endDate

def get_views(youtube_analytics, channel_id):                           
  with open (args.source) as allvids:
    reader = csv.DictReader(allvids)
    videos = []
    for row in reader:
      videos.append(row['ID'])

  with open (args.name, 'wb') as output:
    writer = csv.writer(output)
    i = 0
    headers = ['video','views']
    writer.writerow(headers)
    while i < len(videos):
      sys.stdout.write('\rGetting %i-day-views for %s. Progress: %i/%i' % (int(args.count), str(args.source), i+1, len(videos)))
      sys.stdout.flush()
      videoid = videos[i]
      videoname = getName(youtube, videoid)
      pubDate = getLastDay()
      endDate = getFirstDay()


      result = queryVideo(youtube_analytics,channel_id, videoid, endDate, pubDate)
      for row in result.get("rows",[]):
        rows =[]
        for value in row:
          rows.append(value)
        writer.writerow(rows)  

      i +=1
      
    print "\nDone."
    print "It took", time.time()-startTime, 'seconds to get data from', i, 'videos.'  

if __name__ == "__main__":
  now = datetime.datetime.now()
  one_day_ago = (now - datetime.timedelta(days=1)).strftime("%Y-%m-%d")
  one_week_ago = (now - datetime.timedelta(days=7)).strftime("%Y-%m-%d")

  argparser.add_argument("--count", help="Set range. Default brings 7 day views. ", default=7)
  argparser.add_argument("--name", help="Set output filename. Default is output.csv", default='output.csv')
  argparser.add_argument("--source", help="Set source of video Ids. Default is videolist.csv", default='videolist.csv')
  args = argparser.parse_args()


  (youtube, youtube_analytics) = get_authenticated_services(args)
  try:
    channel_id = get_channel_id(youtube)
    get_views(youtube_analytics, channel_id)
    
  except KeyboardInterrupt:
    print "User aborted."
    print "You waited", time.time()-startTime, 'seconds before giving up.'
  except HttpError, e:
    print "An HTTP error %d occurred:\n%s" % (e.resp.status, e.content)
