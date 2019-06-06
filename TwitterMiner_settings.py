
#General Case Data

CASE_NAME = "casenamehere" #name of your case - This will be the database name too

USER_NAME = "justnameno@symbol" #just the twitter handle with NO @ symbol

#Twitter Historical Search Settings

    #GEO_DATA = "40.4406,-79.9909,3mi" #Pittsburg, PA

    #GEO_DATA = "33.7988,-117.9190,3mi" # Format = "Lat,Long,radius im miles #Anaheim, CA Marriott Convention

    #GEO_DATA = "33.693335,-78.896299,1mi" #Myrtle Beach, SC

GEO_DATA = "41.4993,-81.6944,2mi" #Lat, long, radius

KEYWORDS = ""

DATE_START = ""

DATE_END = ""

ID_MAX = ""

INCLUDE_RETWEETS = False

# Twitter_Live_Geo Settings

BOUNDING_BOX = [-83.2,39.90,-82.9,40.1] #Southwest corner of bounding (long, lat), northeast corner (long,lat)

#BOUNDING_BOX = [-83.85190,40.75035,-83.79928,40.78259] #Ada, OH

#BOUNDING_BOX = [-117.9739,33.722,-117.8063,33.8954] #Anaheim CA
#BOUNDING_BOX = [-78.9830,33.597,-78.7850,33.785] #Myrtle Beach, SC

# Twitter_Live_Search Settings

TRACK_TERMS = ["#technosecuritymb"] #terms, hashtags that you want to watch in the live search, separate by comman




try:
    from private import *
except Exception:
    pass
