import json
import os
import sqlite3 as lite
import urllib.request
import tweepy
import TwitterMiner_settings
from TwitterMiner_Keys import *
from TwitterMiner_settings import *
from TwitterMiner_validate import dump_hash

#---------
#---------
#--------- Be sure to enter a unique case name
#---------
#---------

casename = CASE_NAME

dbname = casename + ".db"

conn = lite.connect(dbname)

c = conn.cursor()

c.execute('''
    CREATE TABLE IF NOT EXISTS Live_Searches (
                                            tweet_id INTEGER NOT NULL PRIMARY KEY, 
                                            screen_name TEXT, 
                                            user_id INTEGER, 
                                            users_name TEXT, 
                                            created_at TEXT,
                                            created_date_UTC TEXT, 
                                            is_retweet TEXT,
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
                                            media_id INTEGER, 
                                            posted_video_dest TEXT,
                                            tweeted_video BLOB, 
                                            video_hash TEXT,
                                            video_type TEXT, 
                                            video_url TEXT,
                                            url_in_tweet TEXT,
                                            coordinates TEXT, 
                                            terms TEXT,
                                            status BLOB, 
                                            status_hash TEXT,
                                            bookmark TEXT)''')

conn.commit()

class StreamListener(tweepy.StreamListener):

    def on_status(self, status):
        
        Tweetid = status.id
        geo = status.geo
        coords = status.coordinates
        re_tweet = status.retweeted
        screenname = status.user.screen_name
        userid = status.user.id
        createdat = status.timestamp_ms
        createddate = status.created_at
        usersname = status.user.name
        
        if hasattr(status, 'retweeted_status'):
            is_retweet = True
        else:
            is_retweet = False        
        
        Amp_text = status.text
        tweet = Amp_text.replace('&amp;','&')   
        
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
        
        
        source = status.source
        reply_to_screen_name = status.in_reply_to_screen_name
        replystatusid = status.in_reply_to_status_id
        terms = str(Twitter_settings.TRACK_TERMS)
        #Begin new code
        #Checks for Media in the Tweet and downloads it
        
        if 'media' in status.entities:
            image_posted = status.entities['media'][0]['media_url']
            remove_tweet_url = image_posted.split('/')[-1]
            
            posted_image_dest = os.path.join("Case_Attachments/" + casename + "/live_search/images/" + screenname + "---" + remove_tweet_url)
            
            image_path = "Case_Attachments/" + casename + "/live_search/images/"
            
            if not os.path.exists(image_path):
                os.makedirs(image_path)
            
            # urllib.request.urlretrieve(image_posted, filename = posted_image_dest)
            
            try:
                urllib.request.urlretrieve(image_posted, filename = posted_image_dest)
                
                tweeted_image = open(posted_image_dest, "rb").read()
            
                image_hash = dump_hash(tweeted_image)                
        
            except urllib.error.URLError as e:
                posted_image_dest = "ERROR DOWNLOADING FILE"
                tweeted_image = None
                image_hash = None
                pass
            except:
                print("Error downloading file... %s ... from TweetID: %s" % (posted_image_dest, str(Tweetid)))
                posted_image_dest = "ERROR DOWNLOADING FILE"
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
                posted_video_dest = os.path.join("Case_Attachments/" + casename + "/live_search/videos/" + screenname + "---" + remove_video_url)
                video_path = "Case_Attachments/" + casename + "/live_search/videos/"
                
                if not os.path.exists(video_path):
                    os.makedirs(video_path)
            
                # urllib.request.urlretrieve(videourl, filename = posted_video_dest)
                
                try:
                    urllib.request.urlretrieve(videourl, filename = posted_video_dest)
                    
                    tweeted_video = open(posted_video_dest, "rb").read()
                
                    video_hash = dump_hash(tweeted_video)                    
            
                except urllib.error.URLError as e:
                    posted_video_dest = "ERROR DOWNLOADING FILE"
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
        
        if not status.entities['urls']:
            url_in_tweet = None

        else:
            url_in_tweet = str(status.entities['urls'][0]['url'])        
        

        if geo is not None:
            geo = json.dumps(geo)

        if coords is not None:
            coords = json.dumps(coords)
            
        bookmark = None
        
        status_encode = str(status).encode('utf-8')
    
        status_hash = dump_hash(status_encode)        

        
        try:
            c.execute('''INSERT INTO Live_Searches (
                                                    tweet_id, 
                                                    screen_name, 
                                                    user_id, 
                                                    users_name, 
                                                    created_at, 
                                                    created_date_UTC,
                                                    is_retweet,
                                                    text,
                                                    place_name,
                                                    country_code,
                                                    country,
                                                    bounding_box,
                                                    source_tweeted, 
                                                    geo,
                                                    in_reply_to_user,
                                                    inreply_statusid, 
                                                    posted_image_dest, 
                                                    tweeted_image,
                                                    image_hash,
                                                    media_type, 
                                                    media_url, 
                                                    media_id, 
                                                    posted_video_dest,
                                                    tweeted_video, 
                                                    video_hash,
                                                    video_type,
                                                    video_url,
                                                    url_in_tweet,
                                                    coordinates, 
                                                    terms,
                                                    status, 
                                                    status_hash,
                                                    bookmark)
                        VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)''' , 
                                                        (Tweetid, 
                                                         screenname, 
                                                         userid, 
                                                         usersname, 
                                                         createdat, 
                                                         createddate, 
                                                         is_retweet,
                                                         tweet,
                                                         placename,
                                                         countrycode,
                                                         country,
                                                         boundingbox,
                                                         source,
                                                         geo, 
                                                         reply_to_screen_name,
                                                         replystatusid, 
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
                                                         coords, 
                                                         terms,
                                                         str(status), 
                                                         status_hash,                                                         
                                                         bookmark))
            conn.commit()
            print(" ")
            print(str(createddate))
            print(screenname)
            print(str(tweet))
            print(" ")
                   
        except lite.IntegrityError:
            print(str(tweetid), "--- Record already Exists")
            
               

    def on_error(self, status_code):
        if status_code == 420:
            print('rate limit')
            return False

auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token, access_token_secret)
api = tweepy.API(auth)

stream_listener = StreamListener()
stream = tweepy.Stream(auth=api.auth, listener=stream_listener)
stream.filter(track=Twitter_settings.TRACK_TERMS)
#stream.filter(locations=[-82.265659,41.373736,-82.164579,41.426754]
#stream.filter(locations=Twitter_settings.BOUNDING_BOX)