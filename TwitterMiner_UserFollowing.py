import os
import sqlite3 as lite
import sys
import time
import urllib.request
from TwitterMiner_Keys import *
from TwitterMiner_settings import *
from twitter import *
from TwitterMiner_validate import dump_hash

twitter = Twitter(auth = OAuth(access_token, access_token_secret, consumer_key, consumer_secret))

screen_name = USER_NAME

try:
    friends = twitter.friends.ids(screen_name = screen_name)
except TwitterError:
    print("Failed to pull profile from %s." % screen_name)
    print("User may be protected/private.")
    print("Exiting...")
    sys.exit()


now = time.strftime("%c")

#---------
#---------
# Be sure to enter a unique case name in settings
#---------
#---------

casename = CASE_NAME

dbname = casename + ".db"

conn = lite.connect(dbname)

table_name = screen_name + "_following"

c = conn.cursor()

c.execute("CREATE TABLE IF NOT EXISTS " + table_name + "(user_id INTEGER NOT NULL PRIMARY KEY, date_mined_local TEXT, screen_name TEXT, name TEXT, \
                                        is_protected BOOLEAN, description TEXT, profile_created_UTC TEXT, user_dump BLOB, user_hash TEXT, bookmark TEXT )")

conn.commit()

print(" ")
print("%s is following %s users" % (screen_name, len(friends["ids"])))

'''For some reason, twitter api is not proccessing the first and last entry in any page sent to the user.lookup
        so, this next block of code only grabs 98 of the allowed 100 entries, but then appends bad_value1 to the beginning
        and bad_value2 to the end of the list, equalling 100.  Since the first and last entries are ignored, twitter does not
        process them.  The results are the entire friends list is processsed.'''
for friend_id in range(0, len(friends['ids']), 98):
    bad_value1 = 1
    bad_value2 = 2
    #print(friend_id)
    ids = friends["ids"][friend_id:friend_id+98]
    #print(ids)
    ids1 = [bad_value1] + ids + [bad_value2]
    
    ids_lookup = twitter.users.lookup(user_id = ids1)
    bookmark = None
    #print(ids_lookup)
    for usernames in ids_lookup:
        is_protected = usernames["protected"]
        
        user_hash = dump_hash(str(usernames).encode('utf-8'))
        
        #print("%s -- %s -- %s -- %s -- %s" % (usernames["id"], usernames["screen_name"], usernames["name"], usernames["description"], usernames["created_at"]))
        try:
            c.execute("INSERT INTO " + table_name + "(user_id, date_mined_local, screen_name, name, is_protected, description, profile_created_UTC, user_dump, user_hash, bookmark) VALUES(?,?,?,?,?,?,?,?,?,?)" , \
                      (usernames["id"], now, usernames["screen_name"], usernames["name"], is_protected, usernames["description"], usernames["created_at"], str(usernames), user_hash, bookmark ))
            conn.commit()
            print(str(usernames['id']), "--- Successfully added to the Database")
                   
        except lite.IntegrityError:
            print(str(usernames['id']), "--- Record already Exists")
            
print()
print("Finished collecting who user -- %s is following..." % screen_name)