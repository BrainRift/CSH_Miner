import os
import sqlite3 as lite
import time
import urllib.request
from TwitterMiner_Keys import *
from TwitterMiner_settings import *
from tweepy import OAuthHandler
import tweepy

#---------
#---------
#--------- Be sure to enter a unique case name
#---------
#---------

casename = CASE_NAME

dbname = casename + ".db"


auth = OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token, access_token_secret)

api = tweepy.API(auth)

user = api.get_user(screen_name = USER_NAME)


now = time.strftime("%c")

conn = lite.connect(dbname)

c = conn.cursor()

# Create the Database if it doesn't exist

c.execute('''
    CREATE TABLE IF NOT EXISTS T_User_Profiles (userid INTEGER NOT NULL PRIMARY KEY, profile_mined_date TEXT, username TEXT, is_protected BOOLEAN, name TEXT, profile_created_date TEXT, 
    entered_location TEXT, description TEXT, countrycode TEXT, country TEXT, place_name TEXT, place_type TEXT, following_number TEXT, followers_number TEXT, 
    number_of_tweets TEXT, number_favorite TEXT, profile_thumbnail TEXT, profile_image TEXT, profile_image_location TEXT, 
    profile_banner_url TEXT, profile_banner_dest TEXT, expanded_url TEXT, utc_offset TEXT, time_zone TEXT, verified TEXT, bookmark TEXT)''')

# Separating individual values to individual variabales


user_id = user.id #User ID with Twitter
pulleddate = now
user_name = user.screen_name
is_protected = user.protected
name = user.name
profile_date = user.created_at
location = user.location
user_description = user.description

if user.profile_location is not None:
    country_code = user.profile_location['country_code']
    country = user.profile_location['country']
    placename = user.profile_location['name']
    placetype = user.profile_location['place_type']
       
else:
    country_code = None
    country = None
    placename = None
    placetype = None

following = user.friends_count
followers = user.followers_count
num_tweets = user.statuses_count
num_favorites = user.favourites_count
thumbnail = user.profile_image_url
largeprofileimage = user.profile_image_url_https #Pulls the URL for the 'normal' profile image
largeprofileimage = largeprofileimage.replace('_normal','') #Removes the word 'normal' to get large image URL

#This bit of code looks at a targeted image in a url and downloads it to a directory of the username
#test downloading image from url and placing it specifically

#will download images from the web

remove_profile_url = largeprofileimage.split('/')[-1]

profile_image_dest = os.path.join("Case_Attachments/" + casename + "/profile_pictures/" + user_name + "/" + remove_profile_url)

profile_path = "Case_Attachments/" + casename + "/profile_pictures/" + user_name + "/"

#destination = os.path.realpath(user_name)

if not os.path.exists(profile_path):
    os.makedirs(profile_path)

# urllib.request.urlretrieve(largeprofileimage, filename = profile_image_dest)

try:
    urllib.request.urlretrieve(largeprofileimage, filename = profile_image_dest)

except urllib.error.URLError as e:
    profile_image_dest = "ERROR DOWNLOADING FILE"
    ResponseData = e.read().decode("utf8", 'ignore')

# End the image download

# Pulls the profile banner aka background image if the attribute exists

if hasattr(user, 'profile_banner_url'):
    profile_banner_url = user.profile_banner_url
    remove_banner_url = profile_banner_url.split('/')[-1] + ".jpg" # Removes the entire URL and adds JPG to end of name
    profile_banner_dest = os.path.join("Case_Attachments/" + casename + "/profile_pictures/" + user_name + "/" + "banner---" + remove_banner_url)
    banner_path = "Case_Attachments/" + casename + "/profile_pictures/" + user_name + "/"
    
    if not os.path.exists(banner_path):
        os.makedirs(banner_path)
        
    try:
        print(profile_banner_url)
        urllib.request.urlretrieve(profile_banner_url, filename = profile_banner_dest)
    
    except urllib.error.URLError as e:
        profile_banner_dest = "ERROR DOWNLOADING FILE"
        ResponseData = e.read().decode("utf8", 'ignore')    
    
else:
    profile_banner_url = None
    profile_banner_dest = None
    banner_path = "Case_Attachments/" + casename + "/profile_pictures/" + user_name + "/"

 

# End profile banner code


if 'url' in user.entities:
    expandedurl = user.entities['url']['urls'][0]['expanded_url']
else:
    expandedurl = None

if user.utc_offset is not None:
    utcoffset = str(user.utc_offset/3600)[:2]
else:
    utcoffset = None

timezone = user.time_zone
verified = user.verified

bookmark = None

# Placing the variables in to db columns

try:
    c.execute('''INSERT INTO T_User_Profiles (userid, profile_mined_date, username, is_protected, name, profile_created_date, 
    entered_location, description, countrycode, country, place_name, place_type, following_number, followers_number, 
    number_of_tweets, number_favorite, profile_thumbnail, profile_image, profile_image_location, 
    profile_banner_url, profile_banner_dest, expanded_url, utc_offset, time_zone, verified, bookmark) 
    VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)''' , (user_id, pulleddate, user_name, is_protected, name, profile_date, location, user_description, 
                                                              country_code, country, placename, placetype, following, followers, num_tweets, 
                                                              num_favorites, thumbnail, largeprofileimage, profile_image_dest, profile_banner_url,
                                                              profile_banner_dest, expandedurl, utcoffset, timezone, verified, bookmark))
    
    conn.commit()
    print(str(user_name), "--- added")
           
except lite.IntegrityError:
    print(str(user_name), "--- Record already Exists") # This should never occur with the change of the schema to id primary to allow for multiple same entries

# Merry Christmas Nerd - This was a message to Isaac