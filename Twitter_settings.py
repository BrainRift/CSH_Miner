
#General Case Data

CASE_NAME = "HubCast2022"

USER_NAME = "kevindelong" #target

#Twitter Historical Search Settings

    #GEO_DATA = "40.4406,-79.9909,3mi" #Pittsburg, PA

    #GEO_DATA = "33.7988,-117.9190,3mi" # Format = "Lat,Long,radius im miles #Anaheim, CA Marriott Convention

    #GEO_DATA = "33.693335,-78.896299,1mi" #Myrtle Beach, SC

GEO_DATA = "40.748156769161156,-73.98563561720309,2mi" #New York

KEYWORDS = ""

DATE_START = ""

DATE_END = ""

ID_MAX = ""

INCLUDE_RETWEETS = False

# Twitter_Live_Geo Settings

BOUNDING_BOX = [-117.9739,33.722,-117.8063,33.8954] #Anaheim CA (lower left coordinate - upper right coordinate ) 47.3592239527105, -64.95507114463506

#BOUNDING_BOX = [-83.2,39.90,-82.9,40.1] # Columbus, Ohio (bottom left coordinate - upper right coordinate )

#BOUNDING_BOX = [-83.85190,40.75035,-83.79928,40.78259] #Ada, OH

#BOUNDING_BOX = [-117.9739,33.722,-117.8063,33.8954] #Anaheim CA
#BOUNDING_BOX = [-78.9830,33.597,-78.7850,33.785] #Myrtle Beach, SC

# Twitter_Live_Search Settings

TRACK_TERMS = ["Cybersocial_Techo"]




try:
    from private import *
except Exception:
    pass
