#!/usr/bin/python3
#
# Author: Willy

from google.transit import gtfs_realtime_pb2
from protobuf_to_dict import protobuf_to_dict
import requests
import datetime
import sys
from datetime import datetime
import time
import pandas as pd


walk = 5  #don't show train times lower than this
cutoff = 40 #don't show train times higher than this

#Lookups for Stations

path= 'stopcrosswalk.csv' #Stop Crosswalk Path
df= pd.DataFrame(pd.read_csv(path),
                 columns= ['Markx','StationLines','subway','BannerFileName','TrainsbyStopID','Boro','StopID']) #Data Frame for CSV

Station_Name = df.loc[(df['Markx'] == 'x'),['subway']]
Banner = df.loc[(df['Markx'] == 'x'),['BannerFileName']]
StopID = df.loc[(df['Markx'] == 'x'),['StopID']]
Lines = df.loc[(df['Markx'] == 'x'),['TrainsbyStopID']]

BackupBanner = df.loc[(df['Markx'] == 'x'),['subway']]

u_station = StopID.iat[0,0]  # Uptown Line ID #1
u_station2 = '' if StopID.size<2 else StopID.iat[1,0] # Uptown Line ID #2 (if applicable)
u_station3 = '' if StopID.size<3 else StopID.iat[2,0] # Uptown Line ID #3 (if applicable)
u_station4 = '' if StopID.size<4 else StopID.iat[3,0] # Uptown Line ID #4 (if applicable)

d_station = u_station[0:len(u_station)-1]+'S'# Downtown Line ID #1
d_station2 = '' if StopID.size<2 else u_station2[0:len(u_station)-1]+'S' # Downtown Line ID #2 (if applicable)
d_station3 = '' if StopID.size<3 else u_station3[0:len(u_station)-1]+'S' # Downtown Line ID #3 (if applicable)
d_station4 = '' if StopID.size<4 else u_station4[0:len(u_station)-1]+'S' # Downtown Line ID #4 (if applicable)




# MTA Feed URLs
NQRWfeed = 'https://api-endpoint.mta.info/Dataservice/mtagtfsfeeds/nyct%2Fgtfs-nqrw'  # N,Q,R,W
BDFMfeed = 'https://api-endpoint.mta.info/Dataservice/mtagtfsfeeds/nyct%2Fgtfs-bdfm'  # B,D,F,M
S123456feed = 'https://api-endpoint.mta.info/Dataservice/mtagtfsfeeds/nyct%2Fgtfs'  # S,1,2,3,4,5,6
ACEHfeed = 'https://api-endpoint.mta.info/Dataservice/mtagtfsfeeds/nyct%2Fgtfs-ace'  # A,C,E,H
Lfeed = 'https://api-endpoint.mta.info/Dataservice/mtagtfsfeeds/nyct%2Fgtfs-l'  # L
Gfeed = 'https://api-endpoint.mta.info/Dataservice/mtagtfsfeeds/nyct%2Fgtfs-g'  # G
JZfeed = 'https://api-endpoint.mta.info/Dataservice/mtagtfsfeeds/nyct%2Fgtfs-jz'  # JZ




def gettimes(feed, s1, s3, s5, s7, s2, s4, s6, s8):
    uptownTimes = []
    downtownTimes = []
    uptownTrainIDs = []
    downtownTrainIDs = []
    route_id = ""

    # Request parameters
    headers = {}

    # Get the train data from the MTA
    response = requests.get(feed, headers=headers, timeout=30)

    # Parse the protocol buffer that is returned
    feed = gtfs_realtime_pb2.FeedMessage()
    feed.ParseFromString(response.content)

    # Get a list of all the train data
    subway_feed = protobuf_to_dict(feed)  # subway_feed is a dictionary
    realtime_data = subway_feed['entity']  # train_data is a list

    # A list of all the arrivals we found for our station in the given feed
    arrivals = []

    # Iterate over each train arrival
    for train in realtime_data:
        # If there is a trip update with a stop time update
        if train.get('trip_update'):
            if (train['trip_update'].get('stop_time_update')):
                # get for each stop time update that is at our stop
                for update in train['trip_update'].get('stop_time_update'):
                    stop_id = update['stop_id']

                    if (stop_id in [s1, s3, s5, s7, s2, s4, s6, s8]):

                        # Get the number of seconds from now to the arrival time
                        elapsed = update['arrival']['time'] - time.mktime(datetime.now().timetuple())

                        # If we alredy missed it, skip it
                        if (elapsed < 0):
                            continue

                        route_id = (train['trip_update']['trip']['route_id'])[0]

                        # Calculate minutes and seconds until arrival
                        mins = int(elapsed / 60)
                        secs = int(elapsed % 60)

                        # Round to nearest minute
                        if (secs >= 30):
                            mins = mins + 1

                        # Skips zeros
                        if (mins == 0):
                            continue

                        if (stop_id in [s1, s3, s5, s7]):
                            uptownTimes.append(mins)
                            uptownTrainIDs.append(route_id)

                        if (stop_id in [s2, s4, s6, s8]):
                            downtownTimes.append(mins)
                            downtownTrainIDs.append(route_id)

    # Sort the results
    if (len(uptownTimes) != 0):
        [uptownTimes, uptownTrainIDs] = zip(*sorted(zip(uptownTimes, uptownTrainIDs), key=lambda p: p[0]))

    if (len(downtownTimes) != 0):
        [downtownTimes, downtownTrainIDs] = zip(*sorted(zip(downtownTimes, downtownTrainIDs), key=lambda p: p[0]))

    # Return our results as a tuple
    return list(uptownTrainIDs), list(uptownTimes), list(downtownTrainIDs), list(downtownTimes)


#Function to fetch fresh times

def fetch():
    NQRW_list = list(gettimes(NQRWfeed, u_station, u_station2,u_station3,u_station4,d_station,d_station2,d_station3,d_station4))
    BDFM_list = list(gettimes(BDFMfeed, u_station, u_station2,u_station3,u_station4,d_station,d_station2,d_station3,d_station4))
    ACEH_list = list(gettimes(ACEHfeed, u_station, u_station2,u_station3,u_station4,d_station,d_station2,d_station3,d_station4))
    S123456_list = list(gettimes(S123456feed, u_station, u_station2,u_station3,u_station4,d_station,d_station2,d_station3,d_station4))
    L_list = list(gettimes(Lfeed, u_station, u_station2,u_station3,u_station4,d_station,d_station2,d_station3,d_station4))
    G_list = list(gettimes(Gfeed, u_station, u_station2,u_station3,u_station4,d_station,d_station2,d_station3,d_station4))
    JZ_list = list(gettimes(JZfeed, u_station, u_station2,u_station3,u_station4,d_station,d_station2,d_station3,d_station4))

    u_trains = NQRW_list[0] + BDFM_list[0] + S123456_list[0] + L_list[0] + G_list[0] + JZ_list[0] + ACEH_list[0]
    u_times = NQRW_list[1] + BDFM_list[1] + S123456_list[1] + L_list[1] + G_list[1] + JZ_list[1] + ACEH_list[1]

    d_trains = NQRW_list[2] + BDFM_list[2] + S123456_list[2] + L_list[2] + G_list[2] + JZ_list[2] + ACEH_list[2]
    d_times = NQRW_list[3] + BDFM_list[3] + S123456_list[3] + L_list[3] + G_list[3] + JZ_list[3] + ACEH_list[3]


    u_list = sorted(list(map(list, (zip(u_trains, u_times)))), key=lambda p: p[1])[0:20]
    d_list = sorted(list(map(list, (zip(d_trains, d_times)))), key=lambda p: p[1])[0:20]

    All_Uptown= []
    All_Downtown= []

    for i in range(len(u_list)):
        if u_list[i][1] > walk and u_list[i][1] < cutoff:
            All_Uptown.append(u_list[i])

    for i in range(len(d_list)):
        if d_list[i][1] > walk and d_list[i][1] < cutoff:
            All_Downtown.append(d_list[i])
    
    
    u = All_Uptown    
    d = All_Downtown
    
    print(Station_Name.iat[0,0]+': Lines',Lines["TrainsbyStopID"].tolist())
    print("Station ID: "+u_station)
    print("Uptown - ",u)
    print("Downtown -", d)


#Run Program
while True:
    try:
        fetch()
        time.sleep(60)
    except:
        print("You pushed a button..")
        time.sleep(2)
        sys.exit("Bye")
