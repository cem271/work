#!/usr/bin/python
# -*- coding: utf-8 -*-

import datetime
import httplib2
import os
import sys
import csv
import time

#Could be improved. Been having trouble with encoding for some reason.
reload(sys)
sys.setdefaultencoding('utf-8')

from apiclient.discovery import build
from apiclient.errors import HttpError
from oauth2client.client import flow_from_clientsecrets
from oauth2client.file import Storage
from oauth2client.tools import argparser, run_flow
startTime = time.time() #I wanted to measure how many seconds it took for this code to run
                        #That's why we start timing here at the very beginning.

# YouTube block
CLIENT_SECRETS_FILE = "client_secrets.json"
YOUTUBE_SCOPES = ["https://www.googleapis.com/auth/youtube.readonly",
  "https://www.googleapis.com/auth/yt-analytics.readonly"]
YOUTUBE_API_SERVICE_NAME = "youtube"
YOUTUBE_API_VERSION = "v3"
YOUTUBE_ANALYTICS_API_SERVICE_NAME = "youtubeAnalytics"
YOUTUBE_ANALYTICS_API_VERSION = "v1"
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

#With this function, we can go through a whole list of videos, regardless of channel.
def authenticate_on_the_spot(channel):
  flow = flow_from_clientsecrets(CLIENT_SECRETS_FILE,
    scope=" ".join(YOUTUBE_SCOPES),
    message=MISSING_CLIENT_SECRETS_MESSAGE)

  storage = Storage("%s-oauth2.json" % channel)
  credentials = storage.get()

  if credentials is None or credentials.invalid:
    credentials = run_flow(flow, storage, args)

  http = credentials.authorize(httplib2.Http())
  youtube = build(YOUTUBE_API_SERVICE_NAME, YOUTUBE_API_VERSION,
    http=http)
  youtube_analytics = build(YOUTUBE_ANALYTICS_API_SERVICE_NAME,
    YOUTUBE_ANALYTICS_API_VERSION, http=http)

  return (youtube, youtube_analytics)

#Returns the publishing DateTime of a video. Returns in GMT and in the format: 
#YYYY-MM-DDT-HH:MM:SS.MMMZ
def getPubdatetime(youtube, videoid):
	pubdatetime = datetime.datetime.now()
	video_response = youtube.videos().list(
		id=videoid,
		part='snippet'
		).execute()
	try:
		pubdatetime = video_response["items"][0]["snippet"]["publishedAt"]
	except:
		return
	return pubdatetime

#Similar to getPubdatetime(). 
#This one extracts the publishing date in the format:
#YYYY-MM-DD
def getPubDate(youtube, videoid):
  pubDate = datetime.datetime.now()
  video_response = youtube.videos().list(
    id=videoid,
    part='snippet'
    ).execute()
  try:
    pubDate = video_response["items"][0]["snippet"]["publishedAt"]
    pubDate = pubDate[0:10]
  except:
    return
  #print pubDate
  return pubDate

#Similar to getPubdatetime(). 
#This one extracts the publishing hour in the format:
#HH:MM:SS and returns in GMT.
def getPubHour(youtube, videoid):
  pubDate = datetime.datetime.now()
  video_response = youtube.videos().list(
    id=videoid,
    part='snippet'
    ).execute()

  try:
    pubHour = video_response["items"][0]["snippet"]["publishedAt"]
    pubHour = pubHour[11:19]
  except:
    return
  #print pubDate
  return pubHour

#Returns the name of the video.
def getName(youtube,videoid):
  videoname=''
  response = youtube.videos().list(
    id=videoid,
    part='snippet'
    ).execute()
  try:
    videoname = response["items"][0]["snippet"]["title"]
  except IndexError:
    return "Video not public."
  return videoname

#Returns the channel on which the video was published.
def getChannel(youtube,videoid):
    channel=''
    response=youtube.videos().list(
    id=videoid,
    part='snippet'
    ).execute()
    try:
      channel = response["items"][0]["snippet"]["channelId"]
    except IndexError:
      return "Video not public."
    return channel

#Returns the YouTube category of the video that was published.
def getCategory(youtube,videoid):
	categoryDict = {
		'1': 'Film & Animation',
		'2': 'Autos & Vehicles',
		'10': 'Music',
		'15': 'Pets & Animals',
		'17': 'Sports',
		'18': 'Short Movies',
		'19': 'Travel & Events',
		'20': 'Gaming',
		'21': 'Videoblogging',
		'22': 'People & Blogs',
		'23': 'Comedy',
		'24': 'Entertainment',
		'25': 'News & Politics',
		'26': 'Howto & Styles',
		'27': 'Education',
		'28': 'Science & Technology',
		'29': 'Nonprofits & Activism',
		'30': 'Movies',
		'31': 'Anime/Animation',
		'32': 'Action/Adventure',
		'33': 'Classics',
		'34': 'Comedy',
		'35': 'Documentary',
		'36': 'Drama',
		'37': 'Family',
		'38': 'Foreign',
		'39': 'Horror',
		'40': 'Sci-Fi/Fantasy',
		'41': 'Thriller',
		'42': 'Shorts',
		'43': 'Shows',
		'44': 'Trailers'}
	categoryid=''
	response = youtube.videos().list(
		id=videoid,
		part='snippet'
		).execute()
	try:
		categoryid = str(response["items"][0]["snippet"]["categoryId"])
		category = categoryDict[categoryid]
	except:
		return
	return category

#Returns the raw filename of the video.
#YouTube is not very good at keeping track of this. So older videos
#do not have raw filenames.
def getFilename(youtube, videoid):
    file_response = youtube.videos().list(
    id=videoid,
    part='fileDetails').execute()
    try:
      filename = file_response["items"][0]["fileDetails"]["fileName"]
    except IndexError:
      return "Video not public."
    return filename

#The main function that unites all the functions above and
#outputs them in a CSV file.
def doTheThing():
  (youtube, youtube_analytics) = authenticate_on_the_spot('master') #Need this to get channel ID. Can be a generic account.
  with open (args.source) as allvids: #You feed the video IDs into the code in the
    reader = csv.DictReader(allvids)  #form of a CSV file: videolist.csv.
    videos = []
    for row in reader:
      videos.append(row['ID'])

  with open (args.name, 'wb') as output: #We create the output CSV file.
    writer = csv.writer(output)          #By default it's called output.csv
    i = 0

    #Modify the code below to change what parameters you wish to return.
    headers = ['video','PubDateTime','Title','filename','category','PubDate','PubHour']
    writer.writerow(headers)
    for video in videos:
      channel = getChannel(youtube, video)
      (auth, auth_analytics) = authenticate_on_the_spot(channel)
      sys.stdout.write('\rCurrently getting information for: %s Progress: %i/%i' % (str(video), int(i), int(len(videos))))
      sys.stdout.flush()

      videoid = video
      videoname = getName(auth, videoid)
      pubdatetime = getPubdatetime(auth,videoid)
      category = getCategory(auth,videoid)
      pubDate = getPubDate(auth, videoid)
      pubHour = getPubHour(auth, videoid)
      filename = getFilename(auth,videoid)


      rows =[]
      rows.append(video)
      rows.append(pubdatetime)
      rows.append(videoname)
      rows.append(filename)
      rows.append(category)
      rows.append(pubDate)
      rows.append(pubHour)
      writer.writerow(rows)
      #print result
      i +=1

    print "\nDone."
    print "It took", time.time()-startTime, 'seconds to get data from', i, 'videos.'


# Runs the code.
if __name__ == "__main__":
  argparser.add_argument("--source", help="Set source of video Ids. Default is videolist.csv", default='videolist.csv')
  argparser.add_argument("--name", help="Set output filename. Default is output.csv", default='output.csv')

  args = argparser.parse_args()

  try:
    doTheThing()

  except KeyboardInterrupt:
    print ''
    print "User aborted."
    print "You waited", time.time()-startTime, 'seconds before giving up.'
  except HttpError, e:
    print ''
    print "An HTTP error %d occurred:\n%s" % (e.resp.status, e.content)
