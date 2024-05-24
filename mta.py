
#!/usr/bin/python3
#
# Author: Willy

from google.transit import gtfs_realtime_pb2
from protobuf_to_dict import protobuf_to_dict
import requests
import datetime
import time
import sys
from datetime import datetime
from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont
import time
import json
import os
import pandas as pd
from rgbmatrix import RGBMatrix, RGBMatrixOptions, graphics


walk = 5  #don't show train times lower than this
cutoff = 40 #don't show train times higher than this



splash_directory = 'sudo /home/willy/subwaybuddy/rpi-rgb-led-matrix/utils/led-image-viewer'
splash_command = ' --led-pixel-mapper="Rotate:180" --led-rows=32 --led-cols=64 --led-slowdown-gpio=2 --led-gpio-mapping=adafruit-hat-pwm --led-no-hardware-pulse --led-pwm-lsb-nanoseconds=200 --led-no-drop-privs -t12 /home/willy/subwaybuddy/splash/Splash_V2.gif'

#Run Splash
os.system(splash_directory+splash_command)


#RGB Matrix Settings
options = RGBMatrixOptions()
options.rows = 32
options.cols = 64
options.chain_length = 1
options.parallel = 1
options.hardware_mapping = 'adafruit-hat-pwm'
options.gpio_slowdown = 3
options.pixel_mapper_config = 'Rotate:180'
options.disable_hardware_pulsing = True
options.brightness = 100
matrix = RGBMatrix(options = options)

#DrawImage Function

def drawimage(path, x, y):
    image = Image.open(path).convert('RGB')
    image.load()
    matrix.SetImage(image, x, y)



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
    
    print("Uptown - ",u)
    print("Downtown -", d)
    
#Matrix Output--------------------------------------

#Clear Matrix:---------------
    drawimage(r'icons/other_icons/' + 'blackbox' + '.png', 0, 0)

#Banner Info ----------------
    uy = 13
    dy=23
    drawimage(r'icons/stops/' + Banner.iat[0,0] + '.png', 0, 0)
    drawimage(r'icons/other_icons/' + '2up' + '.png', 0, uy)
    drawimage(r'icons/other_icons/' + '2down' + '.png', 0, dy)
    drawimage(r'icons/other_icons/' + 'blueline' + '.png', 0, 22)

#Uptown Trains -------------
 
    #First Uptown Train --------------
    try:
        drawimage('icons/trains/' + str(u[0][0])+ 'TT' + '.png', 5, uy) #top left train
        if len(str(u[0][1])) == 1:
            drawimage('icons/numbers/' + str(u[0][1]) + '.png', 15, uy) #1 digit num 
        elif str(u[0][1])[0] == '1':
            drawimage('icons/numbers/' + str(u[0][1])[0] + '.png', 14, uy) #2 digit num, shifts second number to left if first # is 1
            drawimage('icons/numbers/' + str(u[0][1])[1] + '.png', 17, uy) 
        else:
            drawimage('icons/numbers/' + str(u[0][1])[0] + '.png', 14, uy) #2 digit num beginning with 2+
            drawimage('icons/numbers/' + str(u[0][1])[1] + '.png', 19, uy)
    except:
        print("no trains i guess")
        
    #Second Uptown Train --------------
    try:
        drawimage('icons/trains/' + str(u[1][0])+ 'TT' + '.png', 25, uy) #top middle train
        if len(str(u[1][1])) == 1:
            drawimage('icons/numbers/' + str(u[1][1]) + '.png', 35, uy) 
        elif str(u[1][1])[0] == '1':
            drawimage('icons/numbers/' + str(u[1][1])[0] + '.png', 34, uy) 
            drawimage('icons/numbers/' + str(u[1][1])[1] + '.png', 37, uy) 
        else:
            drawimage('icons/numbers/' + str(u[1][1])[0] + '.png', 34, uy) 
            drawimage('icons/numbers/' + str(u[1][1])[1] + '.png', 39, uy)  
    except:
        print("only one train at this station")
        
    #Third Uptown Train -------------- 
    try:
        drawimage('icons/trains/' + str(u[2][0])+ 'TT' + '.png', 45, uy) #top right train
        if len(str(u[2][1])) == 1:
            drawimage('icons/numbers/' + str(u[2][1]) + '.png', 55, uy) 
        elif str(u[2][1])[0] == '1':
            drawimage('icons/numbers/' + str(u[2][1])[0] + '.png', 54, uy) 
            drawimage('icons/numbers/' + str(u[2][1])[1] + '.png', 57, uy) 
        else:
            drawimage('icons/numbers/' + str(u[2][1])[0] + '.png', 54, uy) 
            drawimage('icons/numbers/' + str(u[2][1])[1] + '.png', 59, uy) 
    except:
        print("only two trains at this station")
          
#Downtown Trains --------

    #First Downtown Train --------------
    try:
        drawimage('icons/trains/' + str(d[0][0])+ 'TT' + '.png', 5, dy) #bottom left train
        if len(str(d[0][1])) == 1:
            drawimage('icons/numbers/' + str(d[0][1]) + '.png', 15, dy)
        elif str(d[0][1])[0] == '1':
            drawimage('icons/numbers/' + str(d[0][1])[0] + '.png', 14, dy) 
            drawimage('icons/numbers/' + str(d[0][1])[1] + '.png', 17, dy) 
        else:
            drawimage('icons/numbers/' + str(d[0][1])[0] + '.png', 14, dy) 
            drawimage('icons/numbers/' + str(d[0][1])[1] + '.png', 19, dy) 
    except:
        print("no trains i guess")
        
    #Second Downtown Train --------------
    try:
        drawimage('icons/trains/' + str(d[1][0])+ 'TT' + '.png', 25, dy) #bottom middle train
        if len(str(d[1][1])) == 1:
            drawimage('icons/numbers/' + str(d[1][1]) + '.png', 35, dy) 
        elif str(d[1][1])[0] == '1':
            drawimage('icons/numbers/' + str(d[1][1])[0] + '.png', 34, dy) 
            drawimage('icons/numbers/' + str(d[1][1])[1] + '.png', 37, dy)  
        else:
            drawimage('icons/numbers/' + str(d[1][1])[0] + '.png', 34, dy) 
            drawimage('icons/numbers/' + str(d[1][1])[1] + '.png', 39, dy)    
    except:
        print("only one train i guess")
        
    #Third Downtown Train -------------- 
    try:
        drawimage('icons/trains/' + str(d[2][0])+ 'TT' + '.png', 45, dy) #bottom right train
        if len(str(d[2][1])) == 1:
            drawimage('icons/numbers/' + str(d[2][1]) + '.png', 55, dy) 
        elif str(d[2][1])[0] == '1':
            drawimage('icons/numbers/' + str(d[2][1])[0] + '.png', 54, dy) 
            drawimage('icons/numbers/' + str(d[2][1])[1] + '.png', 57, dy) 
        else:
            drawimage('icons/numbers/' + str(d[2][1])[0] + '.png', 54, dy)
            drawimage('icons/numbers/' + str(d[2][1])[1] + '.png', 59, dy)

    except:
        print("only two trains i guess")

#Timer/Train Ticker Function
def linetime():
    ty=9
    i= -18
    drawimage('icons/other_icons/' + 'redlight' + '.png', 61, ty) #red stop light
 
    while i < 1:
        drawimage('icons/other_icons/' + 'traintick2' + '.png', i-199, ty) #fast approach
        time.sleep(0.09)
        i+=1    
    
    while i >0 and i < 31:
        drawimage('icons/other_icons/' + 'traintick2' + '.png', i-199, ty) #gradual slow
        time.sleep(i/125)
        i+=1
    while i > 30 and i < 57:
        drawimage('icons/other_icons/' + 'traintick2' + '.png', i-199, ty) #even slower
        time.sleep(i/75)
        i+=1


    drawimage('icons/other_icons/' + 'traintick2' + '.png', 57-199, ty) #last tick of train
    time.sleep(1)
    drawimage('icons/other_icons/' + 'traintick2' + '.png', 58-199, ty) #actually this is last tick of the train
    time.sleep(5)
    drawimage('icons/other_icons/' + 'greenlight' + '.png', 61, ty) #green light
    time.sleep(1)
    i=57
    while i >56 and i <70:
        drawimage('icons/other_icons/' + 'traintick2' + '.png', i-199, ty) #train leaving the station
        time.sleep(.1)
        i+=1
    i=70
    while i >69 and i <175:
        drawimage('icons/other_icons/' + 'traintick2' + '.png', i-199, ty) #zoom zoom
        time.sleep(.05)
        i+=1
    i=0


fetch()
linetime()

#Run Program
while True:
    try:
        fetch()
        linetime()
    except:
        print("Oops broken...")
        time.sleep(5)
