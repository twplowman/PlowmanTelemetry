import matplotlib.pyplot as plt
import matplotlib
import folium
import branca.colormap as cm
from geopy import Nominatim
import mysql.connector
from pyparsing import col
import sqlconnect as sql
import os
import shutil
import plotly.express as px 
import matplotlib.dates as mdates

global developer
developer = False

class LivestockBox:
    boxNumber = "PBL003"

matplotlib.use("Agg")

# Creates a Map based upon dateTime and boxNumber from SQL database
# Uses SQL database: plowmantelemetryschema.PBL_Telemetry_2
# Finds latitude and longitude in range and plots these on a map
# TODO - add a few days before? or all day ranges.
# Saves file to same place this code executes then file is moved to correct folder
#
# dateTime = datetime in format of YYYY-MM-DD HH/MM/SS
# boxNumber = string that is specific to livestock box. e.g. 'PBL v0.4.9' no checks if this is wrong!
def PlotLivestockRoute(boxNumber, dateTime, TimeStart):

    config = sql.MysqlConfig()
    mydb = mysql.connector.connect(**config)
    cursor = mydb.cursor()  # define cursor
    query = (
        ("SELECT latitude, longitude, T3 FROM PBL_Uploaded_Data WHERE DateTime BETWEEN %s AND %s AND `Box Number` = %s ORDER BY DateTime;")
    )  # AND `Box Number` = %s;") #construct query
    cursor.execute(
        query,
        (
            TimeStart,
            dateTime,
            boxNumber
        ),
    )  # execute query using time range and box number
    print(dateTime, TimeStart)
    latitudeRange = []
    longitudeRange = []
    locationData = []
    TempRange = []
    for (
        latitude,
        longitude,
        tempIndex
    ) in cursor:  # loop through each row and store longitude and latitude under cursor
        latitudeRange.append(latitude)
        longitudeRange.append(longitude)
        locationData.append([latitude,longitude])
        TempRange.append(tempIndex)
    if not latitudeRange:
        return

    currentLocation = [latitude,longitude]

    return currentLocation, locationData, TempRange

#http://leaflet-extras.github.io/leaflet-providers/preview/#filter=Stadia.AlidadeSmooth
def RenderMap(dateTimeEnd,dateTimeStart,boxNumber,filename):

    currentLocation, dataRange, TempRange = PlotLivestockRoute(boxNumber,dateTimeEnd,dateTimeStart)
    
    my_map = folium.Map(currentLocation, zoom_start=12,tiles=None, tooltip = 'This tooltip will appear on hover')
    colourMap = GetColourMap(min(TempRange),max(TempRange),2)
    #colourMap = cm.linear.PuBuGn_09.scale(0,20).to_step(12)
    
    folium.TileLayer(tiles="https://tiles.stadiamaps.com/tiles/alidade_smooth/{z}/{x}/{y}{r}.png",attr="Stadia",name='Light').add_to(my_map)
    folium.TileLayer(name='Normal').add_to(my_map)
    
    folium.PolyLine(dataRange,color="#0e4a99",weight=4,opacity=0.9,name="Box Route").add_to(my_map)
    folium.ColorLine(positions=dataRange, colors=TempRange,colormap=colourMap,weight=5,opacity=1,name="Temperatures").add_to(my_map)
    
    folium.CircleMarker(currentLocation,radius=12,fill=True,opacity=1,popup="Current Location",color="green").add_to(my_map)

    #i=0
    #for val in dataRange:  
    #    
    #    my_map.add_child( 
    #        folium.CircleMarker(location=[val[0],val[1]],
    #                            radius = 10,
    #                            popup= TempRange[i],
    #                            fill_color=None,
    #                            color = 'clear',
    #                            fill_opacity=0,
    #                            ), name="Temperature Markers")
    #    i = i + 1

    my_map.add_child(colourMap)
    folium.LayerControl(position="bottomleft").add_to(my_map)

    my_map.save(filename)

    if developer is True:
        systemStatement = "mv "+ filename+" /Users/tom_p/Documents/Arduino/Github/PlowmanTelemetry/static/maps" #Mac
        os.system(systemStatement)
    else:
        shutil.move(os.path.join("/home/ubuntu/PlowmanTelemetry/",filename), os.path.join( "/home/ubuntu/PlowmanTelemetry/static/maps/",filename))






# Creates a Temperature graph based upon dateTime and boxNumber from SQL database
# Uses SQL database: plowmantelemetryschema.PBL_Telemetry_2
# Finds temperature and ID in range and plots these on a graph
# TODO - add a few days before? or all day ranges.
# Saves file to same place this code executes then file is moved to correct folder
#
# dateTime = datetime in format of YYYY-MM-DD HH/MM/SS
# boxNumber = string that is specific to livestock box. e.g. 'PBL v0.4.9' no checks if this is wrong!
# filename = name to save temperature (usually same as box number)
def sqlGenerateTempGraph(boxNumber, dateTime, timeRange, filename):
    
    c = []
    c = GetGraphColours()
    T1,T2,T3,T4,T5,T6,T7,T8,ID = sql.sqlGetTemperaturesForGraph(boxNumber,dateTime,timeRange,filename)
    plt.plot(
        ID,T1, c[0], 
        ID,T2, c[1], 
        ID,T3, c[2],
        ID,T4, c[3],
        ID,T5, c[4],
        ID,T6, c[5],
        ID,T7, c[6],
        ID,T8, c[7]
    )  # plot graph - wants to be in own function.
    plt.legend(['T1', 'T2','T3', 'T4','T5', 'T6','T7', 'T8'],loc='upper right')
    myFmt = mdates.DateFormatter('%a %d %b - %-I%p ')
    locator = mdates.AutoDateLocator(minticks=0, maxticks=1, interval_multiples=True)
    formatter = mdates.ConciseDateFormatter(locator)
    formatter.formats = ['%y',  # ticks are mostly years
                         '%b',       # ticks are mostly months
                         '%d',       # ticks are mostly days
                         '%-I%p',    # hrs
                         '%H:%M',    # min
                         '%S.%f', ]  # secs
    formatter.zero_formats = ['%y',  # ticks are mostly years
                         '%y',       # ticks are mostly months
                         '%b',       # ticks are mostly days
                         '%a %d',    # hrs
                         '%H:%M',    # min
                         '%S.%f', ]   # secs
    formatter.offset_formats = ['()', '(%Y)', '(%b-%Y)', '(%d-%b-%Y)', '(%d-%b-%Y)', '(%d-%b-%Y %H:%M)']
    
    plt.gca().xaxis.set_major_formatter(formatter)
    
    plt.xticks(rotation=0)
    plt.grid()
    plt.title("Livestock Internal Temperature")
    plt.xlabel("Time")
    plt.ylabel("Temperature ˚C")
    
    plt.savefig(filename, bbox_inches="tight")
    
    
    if developer is True:
        systemStatement = "mv "+ filename+" /Users/tom_p/Documents/Arduino/Github/PlowmanTelemetry/static/maps" #Mac
        os.system(systemStatement)
    else:
        shutil.move(os.path.join("/home/ubuntu/PlowmanTelemetry/",filename), os.path.join( "/home/ubuntu/PlowmanTelemetry/static/maps/",filename))
    plt.clf()


def LatLonNamedLocation(latitude,longitude):
    geolocator = Nominatim(user_agent="geoapiExercises")
    coords = str(latitude) + "," + str(longitude)
    location = geolocator.reverse(coords, exactly_one=True)
    name = location.raw["display_name"]
    return name




# https://colorbrewer2.org/#type=diverging&scheme=Spectral&n=9
def GetColourMap(min,max,colourMapColours):
    if min < 0:
        min = 0
    if max > 30:
        max = 30
    if colourMapColours == 1:    
        colormap = cm.LinearColormap(
                                ( '#3288bd','#66c2a5','#abdda4','#e6f598','#ffffbf','#fee08b','#fdae61','#f46d43','#d53e4f')
                                ,index=None,vmin=min,vmax=max)
    if colourMapColours == 2:    
        colormap = cm.LinearColormap(
                                ( '#003f5c','#2f4b7c','#665191','#a05195','#d45087','#f95d6a','#ff7c43','#ffa600')
                                ,index=None,vmin=min,vmax=max)
    if colourMapColours == 3:    
        colormap = cm.LinearColormap(
                                ( '#3288bd','#66c2a5','#abdda4','#e6f598','#ffffbf','#fee08b','#fdae61','#f46d43','#d53e4f')
                                ,index=None,vmin=min,vmax=max)
    return colormap


def GetGraphColours():
    colourSet = []
    colourSet.append('#003f5c')
    colourSet.append('#2f4b7c')
    colourSet.append('#665191')
    colourSet.append('#a05195')
    colourSet.append('#d45087')
    colourSet.append('#f95d6a')
    colourSet.append('#ff7c43')
    colourSet.append('#ffa600')
    return colourSet


def AverageTemperatureColour(temperature):
    colourMap = GetColourMap(0,30,2)
    colour = colourMap(temperature)
    return colour




def suffix(d):
    return 'th' if 11<=d<=13 else {1:'st',2:'nd',3:'rd'}.get(d%10, 'th')

def custom_strftime(format, t):
    return t.strftime(format).replace('{S}', str(t.day) + suffix(t.day))    