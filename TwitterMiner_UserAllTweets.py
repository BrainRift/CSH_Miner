#!/usr/bin/env python
# encoding: utf-8

import os
import sqlite3 as lite
import sys
import json
import time
import urllib.request
import tweepy
from TwitterMiner_Keys import *
from tweepy import OAuthHandler
from TwitterMiner_settings import *
import hashlib
#from Twitter_validate import validate_image


def dump_hash(twitter_dump):
    data_hash = None # Ensure the value starts with nothing
    dump = hashlib.sha1()
    dump.update(twitter_dump)
    data_hash = dump.hexdigest()
    return data_hash

def file_hash(point_to_file):
    hash_sha1 = hashlib.sha1()
    with open(point_to_file, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_sha1.update(chunk)
    print(hash_sha1.hexdigest())
    return hash_sha1.hexdigest()

def extract_image_blob(posted_image_dest):
    with open("test.jpg", "wb") as image_file:
        c.execute("SELECT tweeted_image FROM T_Tweets WHERE Tweet_id = " + str(tweet_id))
        ablob = c.fetchone()
        image_file.write(ablob[0])
    
def create_db(table_name):
    
    c.execute("PRAGMA journal_mode = WAL")
    
    c.execute("CREATE TABLE IF NOT EXISTS " + table_name + "(tweet_id INTEGER NOT NULL PRIMARY KEY, date_mined TEXT, screen_name TEXT, \
                                                            user_id INTEGER, users_name TEXT, created_at_UTC TEXT, is_retweet TEXT, \
                                                            retweeted_times TEXT, text TEXT, place_name TEXT, country_code TEXT, country TEXT, \
                                                            bounding_box TEXT, source_tweeted TEXT, geo TEXT, in_reply_to_user TEXT, \
                                                            inreply_statusid TEXT, posted_image_dest TEXT, tweeted_image BLOB, image_hash TEXT, \
                                                            media_type TEXT, media_url TEXT, media_id TEXT, posted_video_dest TEXT, \
                                                            tweeted_video BLOB, video_hash TEXT, video_type TEXT, video_url TEXT, \
                                                            url_in_tweet TEXT, status BLOB, status_hash TEXT, bookmark TEXT)")

    conn.commit()

def get_all_tweets(screen_name):
    #Twitter only allows access to a users most recent 3240 tweets with this method
    #initialize a list to hold all the tweepy Tweets

    alltweets = []

    #make initial request for most recent tweets (200 is the maximum allowed count)

    try:
        new_tweets = api.user_timeline(screen_name = screen_name, count=200)
    except tweepy.TweepError:
        print("Failed to pull tweets from %s" % screen_name)
        print("User may be protected/private.")
        print("Exiting...")
        sys.exit()
    except tweepy.RateLimitError:  # I want to add code here to switch creds if a Rate limit occurs
        print("Failed to pull the tweets due to a Twitter Rate Limit error.")
        print("Please wait 15 min and try again...")
        sys.exit()    

    #save most recent tweets
    alltweets.extend(new_tweets)

    #save the id of the oldest tweet less one
    oldest = alltweets[-1].id - 1

    #keep grabbing tweets until there are no tweets left to grab
    while len(new_tweets) > 0:
        print("getting tweets before %s" % (oldest))

        #all subsiquent requests use the max_id param to prevent duplicates
        new_tweets = api.user_timeline(screen_name = screen_name,count=200,max_id=oldest)

        #save most recent tweets
        alltweets.extend(new_tweets)

        #update the id of the oldest tweet less one
        oldest = alltweets[-1].id - 1

        print("...%s tweets downloaded so far" % (len(alltweets)))

    #transform the tweepy tweets into a 2D array that will populate the csv	
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
            posted_image_dest = os.path.join("Case_Attachments/" + casename + "/tweets/" + screenname + "/tweeted_image/" + remove_tweet_url)
            image_path = "Case_Attachments/" + casename + "/tweets/" + screenname + "/tweeted_image/"

            if not os.path.exists(image_path):
                os.makedirs(image_path)
            try:
                print("Downloading... %s" % posted_image_dest)
                urllib.request.urlretrieve(image_posted, filename = posted_image_dest)
                
                tweeted_image = open(posted_image_dest, "rb").read()
                
                image_hash = dump_hash(tweeted_image)

            except urllib.error.URLError as e:
                print("Error downloading file... %s ... from TweetID: %s" % (posted_image_dest, str(Tweetid)))
                posted_image_dest = "ERROR DOWNLOADING FILE"
                tweeted_image = None
                image_hash = None                
                pass

            except:
                print("Error downloading file... %s ... from TweetID: %s" % (posted_image_dest, str(Tweetid)))
                posted_image_dest = "ERROR DOWNLOADING FILE - Unknown Error"
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

        # New video Code
        #Checks for Video in the tweets and downloads it

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
                        posted_video_dest = os.path.join("Case_Attachments/" + casename + "/tweets/" + screenname + "/tweeted_video/" + remove_video_url)
                        video_path = "Case_Attachments/" + casename + "/tweets/" + screenname + "/tweeted_video/"

                        if not os.path.exists(video_path):
                            os.makedirs(video_path)

                        try:
                            print("Downloading... %s" % posted_video_dest)
                            urllib.request.urlretrieve(videourl, filename = posted_video_dest)
                            
                            tweeted_video = open(posted_video_dest, "rb").read()
                            
                            video_hash = dump_hash(tweeted_video)

                        except urllib.error.URLError as e:
                            print("Error downloading file... %s ... from TweetID: %s" % (posted_video_dest, str(Tweetid)))
                            posted_image_dest = "ERROR DOWNLOADING FILE"
                            tweeted_video = None
                            video_hash = None                            
                            pass

                        except:
                            print("Error downloading file... %s ... from TweetID: %s" % (posted_video_dest, str(Tweetid)))
                            posted_image_dest = "ERROR DOWNLOADING FILE"
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


        # End new video Code    

        if not status.entities['urls']:
            url_in_tweet = None

        else:
            url_in_tweet = str(status.entities['urls'][0]['url'])

        #Grab the current date and time

        now = time.strftime("%c")
        # Starts the raw hash process
    
        status_dump = str(status).encode('utf-8')
    
        status_hash = dump_hash(status_dump)
    
        bookmark = None
    
        # Writes the data collected in the variables to the database
    
        try:
            c.execute("INSERT INTO " + table_name + "(tweet_id, date_mined, screen_name, user_id, users_name, \
                                                    created_at_UTC, is_retweet, retweeted_times,text, place_name, \
                                                    country_code, country, bounding_box, source_tweeted, geo, \
                                                    in_reply_to_user, inreply_statusid, posted_image_dest, \
                                                    tweeted_image, image_hash, media_type, media_url, media_id, \
                                                    posted_video_dest, tweeted_video, video_hash, video_type, \
                                                    video_url, url_in_tweet, status, status_hash, bookmark) \
                                                    VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)" , \
                                                (Tweetid, 
                                                 now, 
                                                 screenname, 
                                                 userid, 
                                                 usersname, 
                                                 tweettime, 
                                                 is_retweet, 
                                                 retweeted_times, 
                                                 Tweet_text, 
                                                 placename, 
                                                 countrycode, 
                                                 country, 
                                                 boundingbox, 
                                                 Tweet_source, 
                                                 geo, 
                                                 inreplytouser, 
                                                 inreply_tostatus, 
                                                 posted_image_dest, 
                                                 tweeted_image,
                                                 image_hash, 
                                                 mediatype, 
                                                 mediaurl, 
                                                 mediaid, 
                                                 posted_video_dest, 
                                                 tweeted_video, 
                                                 video_hash, 
                                                 videotype,
                                                 videourl, 
                                                 url_in_tweet, 
                                                 str(status), 
                                                 status_hash, 
                                                 bookmark))
            conn.commit()
            print(str(Tweetid), "--- Successfully added to the Database")
    
        except lite.IntegrityError:
            print(str(Tweetid), "--- Record already Exists")		


if __name__ == '__main__':
    
    auth = OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(access_token, access_token_secret)
    api = tweepy.API(auth)
    
    #---------
    #---------
    #--------- Be sure to enter a unique case name -- This is handled in TwitterMiner_settings now
    #---------
    #---------
    
    casename = CASE_NAME
    
    dbname = casename + ".db"    

    conn = lite.connect(dbname)

    c = conn.cursor()
    
    screenname = USER_NAME
    
    table_name = USER_NAME + "_Tweets"
    
    create_db(table_name)
    
    get_all_tweets(screenname)
    
    print("\n Finished collecting Tweets from user --- %s" % screenname)
    
    #validate_image('T_Tweets')