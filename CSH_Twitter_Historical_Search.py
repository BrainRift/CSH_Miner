#!/usr/bin/env python
# encoding: utf-8
# Author: Kevin DeLong
# Feel free to modify and make it awesome! Please just give me credit

import os
import json
import sqlite3 as lite
import sys
import time
import urllib.request
import tweepy
from Twitter_Keys import *
from Twitter_settings import *
from tweepy import OAuthHandler
import hashlib
from Twitter_validate import dump_hash

def file_hash(fname):
    file_md5 = hashlib.md5()
    with open(fname, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            file_md5.update(chunk)   
    return file_md5.hexdigest()

def extract_image_blob(tweet_id):
    with open("Kevin.jpg", "wb") as image_file:
        c.execute("SELECT tweeted_image FROM T_Tweets WHERE Tweet_id = " + str(tweet_id))
        ablob = c.fetchone()
        image_file.write(ablob[0])

def extract_video_blob(tweet_id):
    with open("Kevin.jpg", "wb") as video_file:
        c.execute("SELECT tweeted_video FROM T_Tweets WHERE Tweet_id = " + str(tweet_id))
        ablob = c.fetchone()
        video_file.write(ablob[0])
        
# Creates the database and table if it does not exist

def create_db():

    c.execute('''
        CREATE TABLE IF NOT EXISTS T_Hist_Search(
                                                tweet_id INTEGER NOT NULL PRIMARY KEY, 
                                                date_mined TEXT, 
                                                screen_name TEXT, 
                                                user_id INTEGER,
                                                users_name TEXT, 
                                                created_at_UTC TEXT, 
                                                is_retweet TEXT, 
                                                retweeted_times TEXT, 
                                                text TEXT,
                                                place_name TEXT, 
                                                country_code TEXT, 
                                                country TEXT,
                                                bounding_box TEXT, 
                                                source_tweeted TEXT,
                                                geo TEXT,
                                                in_reply_to_user TEXT,
                                                inreply_statusid TEXT, 
                                                posted_image_dest TEXT,
                                                tweeted_image BLOB, 
                                                image_hash TEXT,
                                                media_type TEXT, 
                                                media_url TEXT,
                                                media_id TEXT, 
                                                posted_video_dest TEXT,
                                                tweeted_video BLOB, 
                                                video_hash TEXT,
                                                video_type TEXT, 
                                                video_url TEXT, 
                                                url_in_tweet TEXT,
                                                user_search_terms TEXT, 
                                                user_locations TEXT, 
                                                user_start_date TEXT, 
                                                user_end_date TEXT, 
                                                status BLOB,
                                                status_hash TEXT, 
                                                bookmark TEXT)''')
    
    conn.commit()


def get_all_tweets(search_terms, locations, start_date, end_date, max_id):
    #Get 3240 Tweets 
    #Twitter keeps records two weeks
    #Twitter can and does block out events of National Security (ie Ft Lauderdale incident blocked 18 hours)

    # This list will hold the tweets collected and is global to pass between functions
    alltweets = []	

    # Will try to make initial request for most recent tweets (200 is the maximum allowed count)
    #print(api.rate_limit_status())
    try:
        search = api.search_tweets(q=search_terms, geocode=locations, count=200, since=start_date, until=end_date, max_id=max_id)
        
    except tweepy.errors as err:
        print("Failed")
        print(err)
    
    
    #except tweepy.TweepError as err:
        #print("Failed to pull the tweets specified.")
        #print(err)
        #print("Exiting...")
        #sys.exit()
        
    #except tweepy.RateLimitError as err:
        #print("Failed to pull the tweets due to a Twitter Rate Limit error.")
        #print("Please wait 15 min and try again...")
        #sys.exit()

    #save most recent tweets
    alltweets.extend(search)

    #save the id of the oldest tweet less one
    try:
        oldest = alltweets[-1].id - 1
        
    except IndexError as err:
        print(" ")
        print("Search Parameters not found in Tweets")
        print("Exiting...")
        sys.exit()

    #keep grabbing tweets until there are no tweets left to grab within the 2 week period or 4000 tweets are grabbed
    len_alltweets = len(alltweets)
    while len(search) > 0 and len_alltweets < 4001:

        print("getting tweets before %s" % (oldest))

        #all subsiquent requests use the max_id param to prevent duplicates
        try:
            search = api.search_tweets(q=search_terms, geocode=locations, count=200, max_id=oldest, since=start_date, until=end_date)
            #save most recent tweets
            alltweets.extend(search)
        
            #update the id of the oldest tweet less one
            oldest = alltweets[-1].id - 1
        
            print("...%s tweets downloaded so far" % (len(alltweets)))
            len_alltweets = len(alltweets)
            
        except tweepy.errors as err:
            print("Failed to continue to pull the tweets specified.")
            print(err)
            print("Stopping pull and beginning to parse...")
            len_alltweets = 5000
            pass
            
        except tweepy.RateLimitError as err:
            print("Failed to pull the tweets due to a Twitter Rate Limit error.")
            print("Please wait 15 min and try again...")
            print("Print moving to parse collected tweets")
            len_alltweets = 5000
            pass             
    
    for status in alltweets:
        # Pull the pieces of the tweet and put them in a variable
    
        Tweetid = status.id
        screenname = status.user.screen_name
        userid = status.user.id
        usersname = status.user.name
        tweettime = status.created_at
    
        # Checks to see if status has the attribute of status.retweeted_status, then assigns is_retweet a value
        if hasattr(status, 'retweeted_status'):
            is_retweet = True
        else:
            is_retweet = False
    
        retweeted_times = status.retweet_count
        Amp_text = status.text
        Tweet_text = Amp_text.replace('&amp;','&')
    
        if status.place is not None:
            placename = status.place.full_name
            countrycode = status.place.country_code
            country = status.place.country
            boundingbox = str(status.place.bounding_box.coordinates)
    
        else:
            placename = None
            countrycode = None
            country = None
            boundingbox = None
    
        Tweet_source = status.source
        
        geo = status.geo
        
        if geo is not None:
            geo = json.dumps(geo)
            
        inreplytouser = status.in_reply_to_screen_name
        inreply_tostatus = status.in_reply_to_status_id_str
    
        #Checks for Media in the Tweet and downloads it
    
        if 'media' in status.entities:
            image_posted = status.entities['media'][0]['media_url']
            remove_tweet_url = image_posted.split('/')[-1]
            posted_image_dest = os.path.join("Case_Attachments/" + casename + "/Hist_Search/images/" + screenname + "---" + remove_tweet_url)
            image_path = "Case_Attachments/" + casename + "/Hist_Search/images/"
    
            if not os.path.exists(image_path):
                os.makedirs(image_path)
    
            try:
                print("Downloading... %s" % posted_image_dest)
                urllib.request.urlretrieve(image_posted, filename = posted_image_dest)
                
                tweeted_image = open(posted_image_dest, "rb").read()
            
                image_hash = dump_hash(tweeted_image)                
                
    
            except urllib.error.URLError as e:
                posted_image_dest = "ERROR DOWNLOADING FILE"
                tweeted_image = None
                image_hash = None                
                pass
            
            except:
                posted_image_dest = "ERROR DOWNLOADING FILE"
                print("Error downloading file... %s" % posted_image_dest)
                tweeted_image = None
                image_hash = None                
                pass            
    
            mediatype = status.entities['media'][0]['type']
            mediaurl = status.entities['media'][0]['media_url']
            mediaid = status.entities['media'][0]['id']        
    
        else:
            posted_image_dest = None
            mediatype = None
            mediaurl = None
            mediaid = None
            tweeted_image = None
            image_hash = None            
    
        # Checks for Video in the tweets and downloads it
    
        if hasattr(status, 'extended_entities'):
            if 'video_info' in status.extended_entities['media'][0]:
    
                # This section checks the number of dictionaries are in the variants
                # It then looks at the bitrate of the variants and determines the highest value
                # Once the highest value is determined, it extracts that video.
    
                variant_times = len(status.extended_entities['media'][0]['video_info']['variants']) # Gets the number of variants
    
                bit_rate = -1
    
                for variant_count in range(0, variant_times): #iterates through all the variants in that tweets
    
    
                    if 'bitrate' in status.extended_entities['media'][0]['video_info']['variants'][variant_count] and \
                       bit_rate < status.extended_entities['media'][0]['video_info']['variants'][variant_count]['bitrate']:
                        bit_rate = status.extended_entities['media'][0]['video_info']['variants'][variant_count]['bitrate']
                        videourl = status.extended_entities['media'][0]['video_info']['variants'][variant_count]['url']
                        videotype = status.extended_entities['media'][0]['video_info']['variants'][variant_count]['content_type']
    
    
                remove_video_url = videourl.split('/')[-1]
                posted_video_dest = os.path.join( "Case_Attachments/" + casename + "/Hist_Search/videos/" + screenname + "---" + remove_video_url)
                video_path = "Case_Attachments/" + casename + "/Hist_Search/videos/"
    
                if not os.path.exists(video_path):
                    os.makedirs(video_path)
    
                try:
                    print("Downloading... %s" % posted_video_dest)
                    urllib.request.urlretrieve(videourl, filename = posted_video_dest)
                    
                    tweeted_video = open(posted_video_dest, "rb").read()
                
                    video_hash = dump_hash(tweeted_video)                    
                    
                except urllib.error.URLError as e:
                    posted_video_dest = "ERROR DOWNLOADING FILE"
                    tweeted_video = None
                    video_hash = None                    
                    pass
                
                except:
                    posted_video_dest = "ERROR DOWNLOADING FILE - Unknown Error"
                    print("Error downloading file... %s" % posted_video_dest)
                    tweeted_video = None
                    video_hash = None                    
                    pass                
    
            else:
                posted_video_dest = None
                videotype= None
                videourl= None 
                tweeted_video = None
                video_hash = None                
        else:
            posted_video_dest = None
            videotype= None
            videourl= None 
            tweeted_video = None
            video_hash = None            
    
        # End Video Check       
    
        if not status.entities['urls']:
            url_in_tweet = None
    
        else:
            url_in_tweet = str(status.entities['urls'][0]['url'])
    
        #Grab the current date and time
    
        now = time.strftime("%c")
        
        # Starts the row hash process
    
        status_dump = str(status).encode('utf-8')
    
        status_hash = dump_hash(status_dump)
        
        print(" ")
        print(status_hash)
    
        bookmark = None
    
        try:
            c.execute('''INSERT INTO T_Hist_Search (tweet_id, date_mined, screen_name, user_id, users_name, created_at_UTC, is_retweet, retweeted_times,
                                                        text, place_name, country_code, country, bounding_box,
                                                        source_tweeted, geo, in_reply_to_user, inreply_statusid, posted_image_dest, 
                                                        tweeted_image, image_hash, media_type,
                                                        media_url, media_id, posted_video_dest, 
                                                        tweeted_video, video_hash, video_type, video_url, url_in_tweet,
                                                        user_search_terms, user_locations, user_start_date, user_end_date, status, status_hash, bookmark)
            VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)''' , (Tweetid, now, screenname, userid, usersname, tweettime, is_retweet, retweeted_times, 
                                                                                        Tweet_text, placename, countrycode, country, boundingbox, 
                                                                                        Tweet_source, geo, inreplytouser, inreply_tostatus, posted_image_dest,
                                                                                        tweeted_image, image_hash, mediatype, 
                                                                                        mediaurl, mediaid, posted_video_dest, 
                                                                                        tweeted_video, video_hash, videotype, videourl, url_in_tweet,
                                                                                        search_terms, locations, start_date, end_date, str(status), status_hash, bookmark))
            conn.commit()
            print(str(Tweetid), "--- Successfully added to the Database")
    
        except lite.IntegrityError:
            print(str(Tweetid), "--- Record already Exists")		


if __name__ == '__main__':
    
    auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(access_token, access_token_secret)
    api = tweepy.API(auth)    
    
    # Adds the conditions for the search
    
        #locations="41.40000,-82.22611,1mi" #Geo for Amherst, OH "41.40000,-82.22611,1mi"
    
        #locations="39.109808,-84.437571,5mi"
    
        #locations="40.716932,-74.000130,1mi" # Geo for New York City
    
        #locations="40.4406,-79.9909,3mi" # Geo for Pittsburg PA
    
    locations = GEO_DATA
    
        #locations="51.499479,-0.124809,1mi" # Geo for Parliment in London
    
        #locations="36.863140,-76.015778,1mi" # Virginia Beach, Virginia
    
        #locations="41.40000,-82.22611,1mi" # Geo for Fort Lauderdale Airport 26.071488,-80.147796,1mi
    
    start_date = DATE_START # Date format should be "2017-01-12"
    end_date = DATE_END
    
    search_terms = KEYWORDS # Search Terms - Does not support lists.  If two words are used, 'and' is implied
    
    max_id = ID_MAX
    
    is_retweet = INCLUDE_RETWEETS
    
    #---------
    #---------
    # Be sure to enter a unique case name
    #---------
    #---------
    
    casename = CASE_NAME
    
    dbname = casename + ".db"
    
    conn = lite.connect(dbname) # Name of the database to store the data
    
    c = conn.cursor()    
    
    create_db()
    
    if locations =="":
        locations = None
        
    if start_date == "":
        start_date = None
        
    if end_date == "":
        end_date = None
        
    if search_terms == "":
        search_terms = None
    
    if max_id =="":
        max_id = None
    
    get_all_tweets(search_terms, locations, start_date, end_date, max_id)
    
    
    
    print("\n Finished pulling the Historical Twitter Feed for conditions SEARCH TERMS = %s, LOCATIONS = %s, START DATE = %s, END DATE = %s, MAX TWEET ID == %s" % (search_terms, locations, start_date, end_date, max_id))