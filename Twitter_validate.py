import hashlib
import sqlite3 as lite
import os
import time
from Twitter_settings import *

now = time.strftime("%Y-%m-%d %H.%M.%S.%Z")

def dump_hash(twitter_dump):
    data_hash = None
    dump = hashlib.sha1()
    dump.update(twitter_dump)
    data_hash = dump.hexdigest()
    return data_hash

def sha1(fname):
    hash_sha1 = hashlib.sha1()
    with open(fname, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_sha1.update(chunk)   
    return hash_sha1.hexdigest()

def extract_image_blob(posted_image_dest):
    temp_hash_location = "attachments/temp/"
    if not os.path.exists(temp_hash_location):
        os.makedirs(temp_hash_location)    
    with open("attachments/temp/Kevin.jpg", "wb") as image_file:
        c.execute("SELECT tweeted_image FROM T_Tweets WHERE posted_image_dest is '%s'" % posted_image_dest)
        ablob = c.fetchone()
        image_file.write(ablob[0])

def extract_video_blob(posted_video_dest):
    temp_hash_location = "attachments/temp/"
    if not os.path.exists(temp_hash_location):
        os.makedirs(temp_hash_location)    
    with open("attachments/temp/Kevin.mp4", "wb") as video_file:
        c.execute("SELECT tweeted_video FROM T_Tweets WHERE posted_video_dest is '%s'" % posted_video_dest)
        ablob = c.fetchone()
        video_file.write(ablob[0])

def validate_image():
    tables =[]
    
    alltables = c.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables.extend(alltables)
    
    for table in tables:
    
        try:
            c.execute('SELECT posted_image_dest, image_hash, tweeted_image, Tweet_id FROM ' + table[0])
            print(" ")
            print("Validating Hashes for IMAGES on table " + table[0])
            
        except:
            print(" ")
            print("No 'image' column found to verify in " + table[0])
            pass 
        
        for row in c:
            if row[0] != "ERROR DOWNLOADING FILE" and row[0] != None:
                posted_image_dest = row[0]
                remove_tweet_url = posted_image_dest #.split('/')[-1]
                image_hash = row[1]
                tweeted_image = row[2]
                tweet_id = row[3]
                compare_local_hash = sha1(posted_image_dest)
                compare_db_hash = dump_hash(tweeted_image)
                
                if compare_local_hash == image_hash and compare_db_hash == image_hash:
                    with open ("logs/" + CASE_NAME + " log %s.txt" % now, "a") as log_file:
                        print(" ", file=log_file)
                        print("Hashes match for IMAGES in " + table[0], file=log_file)
                        print("Hashing TweetID: %s" % tweet_id, file=log_file)
                        print(remove_tweet_url, "hash value   == ", compare_local_hash, file=log_file)
                        print("Database stored image hash value == ", compare_db_hash, file=log_file)
                        print("Both equal the stored hash value == ", image_hash, file=log_file)
                        print("MATCH!", file=log_file)
                        print(" ", file=log_file)
                elif compare_db_hash != image_hash:
                    with open ("logs/" + CASE_NAME + " log %s.txt" % now, "a") as log_file:
                        print(" ")
                        print(" ", file=log_file)
                        print("********************************-ERROR", file=log_file)                        
                        print(" ", file=log_file)
                        print("The database stored file at", posted_image_dest, " in " + table[0] + " hashed a value of ", compare_db_hash)
                        print("The database stored file at", posted_image_dest, " in " + table[0] + " hashed a value of ", compare_db_hash, file=log_file)
                        print(" ")
                        print(" ", file=log_file)
                        print("It should have has a value of ", image_hash)
                        print("It should have has a value of ", image_hash, file=log_file)
                        print(" ")
                        print(" ", file=log_file) 
                elif compare_local_hash != image_hash:
                    with open ("logs/" +CASE_NAME + " log %s.txt" % now, "a") as log_file:
                        print(" ")
                        print(" ", file=log_file)
                        print("********************************-ERROR", file=log_file)                        
                        print(" ", file=log_file)
                        print("The local file ", posted_image_dest, " hashed a value of ", compare_local_hash)
                        print("The local file ", posted_image_dest, " hashed a value of ", compare_local_hash, file=log_file)
                        print(" ")
                        print(" ", file=log_file)
                        print("It should have has a value of ", image_hash)
                        print("It should have has a value of ", image_hash, file=log_file)
                        print(" ")
                        print(" ", file=log_file)
                                
    print(" ")
    print("Image validation complete, please see log file")
        
def validate_video():
    tables =[]
    
    alltables = c.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables.extend(alltables)
    
    for table in tables:
        try:
            c.execute('SELECT posted_video_dest, video_hash, tweeted_video, Tweet_id FROM ' + table[0])
            print("Validating Hashes for VIDEOS in " + table[0] + "...")
        except:
            print(" ")
            print("No 'video' column found to verify in " + table[0])
            pass        
            
        for row in c:
            if row[0] != "ERROR DOWNLOADING FILE" and row[0] != None:
                posted_video_dest = row[0]
                remove_tweet_url = posted_video_dest #.split('/')[-1]
                video_hash = row[1]
                tweeted_video = row[2]
                tweet_id = row[3]
                compare_local_hash = sha1(posted_video_dest)
                compare_db_hash = dump_hash(tweeted_video)
            
                if compare_local_hash == video_hash and compare_db_hash == video_hash:
                    with open ("logs/" + CASE_NAME + " log %s.txt" % now, "a") as log_file:
                        print(" ", file=log_file)
                        print("Hashes match for VIDEOS in " + table[0], file=log_file)
                        print("Hashing TweetID: %s" % tweet_id, file=log_file)
                        print(remove_tweet_url, "hash value   == ", compare_local_hash, file=log_file)
                        print("Database stored image hash value == ", compare_db_hash, file=log_file)
                        print("Both equal the stored hash value == ", video_hash, file=log_file)
                        print("MATCH!", file=log_file)
                        print(" ", file=log_file)
                    
                elif compare_local_hash != image_hash:
                    with open ("logs/" + CASE_NAME + " log %s.txt" % now, "a") as log_file:
                        print(" ", file=log_file)
                        print("********************************-ERROR", file=log_file)                        
                        print(" ")
                        print("The local file ", posted_video_dest, " hashed a value of ", compare_local_hash)
                        print(" ")
                        print("It should have has a value of ", video_hash,)
                        print(" ")                        
                        print(" ", file=log_file)
                        print("The local file ", posted_video_dest, " hashed a value of ", compare_local_hash, file=log_file)
                        print(" ", file=log_file)
                        print("It should have has a value of ", video_hash, file=log_file)
                        print(" ", file=log_file)
                elif compare_db_hash != video_hash:
                    with open ("logs/" + CASE_NAME + " log %s.txt" % now, "a") as log_file:
                        print(" ", file=log_file)
                        print("********************************-ERROR", file=log_file)                        
                        print(" ", file=log_file)
                        print("The database stored file at ", posted_video_dest, " in " + table[0] + " hashed a value of ", compare_db_hash, file=log_file)
                        print(" ", file=log_file)
                        print("It should have has a value of ", video_hash, file=log_file)
                        print(" ", file=log_file)                
                        
                        print(" ")
                        print("The database stored file at ", posted_video_dest, " in " + table[0] + " hashed a value of ", compare_db_hash)
                        print(" ")
                        print("It should have has a value of ", video_hash)
                        print(" ")                
    print(" ")
    print("Video validation complete, please see log file")
    
def validate_status():
    tables =[]
    
    alltables = c.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables.extend(alltables)
    
    for table in tables:
        
        try: 
            c.execute("SELECT status, status_hash, Tweet_id FROM " + table[0] +";")
            print("Validating Hashes for STATUS in " + table[0] + "...")
        except:
            print(" ")
            print("No 'status' column found to verify in " + table[0])
            pass
        
        for row in c:
            if row[0] is not None:
                status = row[0]
                status_hash = row[1]
                tweet_id = row[2]
                compare_db_hash = dump_hash(str(status).encode('utf-8'))
            
                if compare_db_hash == status_hash:
                    with open ("logs/"+ CASE_NAME + " log %s.txt" % now, "a") as log_file:
                        print(" ", file=log_file)
                        print("Hashes match for STATUS in " + table[0], file=log_file)
                        print("Hashing TweetID: %s" % tweet_id, file=log_file)
                        print("RAW status dump hash value    == ", compare_db_hash, file=log_file)
                        print("Stored hash value is equal to == ", status_hash, file=log_file)
                        print("MATCH!", file=log_file)
                        print(" ", file=log_file)
                    
                elif compare_db_hash != status_hash:
                    with open ("logs/"+ CASE_NAME + " log %s.txt" % now, "a") as log_file:
                        print(" ", file=log_file)
                        print("********************************-ERROR", file=log_file)
                        print(" ", file=log_file)
                        print("The RAW tweet stored at TweetID: %s in " % tweet_id + table[0] + " Does not match the stored Hash!", file=log_file)
                        print(" ", file=log_file)
                        print("New RAW Hash is %s , but is should be %s" % (compare_db_hash, status_hash), file=log_file)
                        print(" ", file=log_file)
                        print(" ")
                        print("The RAW tweet stored at TweetID: %s in " % tweet_id + table[0] + " Does not match the stored Hash!")
                        print(" ")
                        print("New RAW Hash is %s , but is should be %s" % (compare_db_hash, status_hash))
                        print(" ")                    
                         
    print(" ")
    print("Status validation complete, please see log file")
            
try:
    conn = lite.connect(CASE_NAME + '.db')
except:
    print(" ")
    print("No database/case with that name found")
    exit()

c = conn.cursor()

log_location = "logs/"
if not os.path.exists(log_location):
    os.makedirs(log_location)
    
#print(" ")
#print("Validating storted data from case - " + CASE_NAME)
    
#validate_profile() ---- I need to create this for images and content
#validate_image() 
#validate_video()
#validate_status()

#print(" ")
#print("Case validation for case - " + CASE_NAME + " has been completed.")
#print("See the log located at " + log_location + CASE_NAME + " log " + now + ".txt")