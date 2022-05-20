from turtle import pos
from unicodedata import name
import matplotlib.pyplot as plt
import matplotlib
import folium
import branca.colormap as cm
from geopy import Nominatim
import mysql.connector
from numpy import tile
import sqlconnect as sql
import os
import shutil
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
    colourMap = GetColourMap(min(TempRange),max(TempRange))
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


# https://colorbrewer2.org/#type=diverging&scheme=Spectral&n=9
def GetColourMap(min,max):
    if min < 0:
        min = 0
    if max > 30:
        max = 30
    colormap = cm.LinearColormap(
                               
                                ( '#3288bd','#66c2a5','#abdda4','#e6f598','#ffffbf','#fee08b','#fdae61','#f46d43','#d53e4f')
                                
                                ,index=None,vmin=min,vmax=max)
    return colormap


# Creates a Temperature graph based upon dateTime and boxNumber from SQL database
# Uses SQL database: plowmantelemetryschema.PBL_Telemetry_2
# Finds temperature and ID in range and plots these on a graph
# TODO - add a few days before? or all day ranges.
# Saves file to same place this code executes then file is moved to correct folder
#
# dateTime = datetime in format of YYYY-MM-DD HH/MM/SS
# boxNumber = string that is specific to livestock box. e.g. 'PBL v0.4.9' no checks if this is wrong!
# filename = name to save temperature (usually same as box number)
def sqlGenerateTempGraph(dateTime, timeRange, filename):
    config = sql.MysqlConfig()
    mydb = mysql.connector.connect(**config)
    TemperatureID = "T1"
    cursor = mydb.cursor()  # define cursor
    query = "SELECT DateTime,T1,T2,T3,T4,T5,T6,T7,T8 FROM PBL_Uploaded_Data WHERE DateTime BETWEEN %s AND %s;"  # AND `Box Number` = %s;") #construct query
    cursor.execute(
        query,
        (
            timeRange,
            dateTime,
        ),
    )  # execute query using time range and box number
    # define array
    ID = []
    T1 = []
    T2 = []
    T3 = []
    T4 = []
    T5 = []
    T6 = []
    T7 = []
    T8 = []

    for (
        Identifier,
        Temp1,
        Temp2,
        Temp3,
        Temp4,
        Temp5,
        Temp6,
        Temp7,
        Temp8,
    ) in cursor:  # loop through each row and store longitude and latitude under cursor
        if Temp1 != -127 and Temp1 != 85:
            T1.append(Temp1)
        else:
            T1.append(float("NaN"))
        if Temp2 != -127 and Temp2 != 85:
            T2.append(Temp2)
        else:
            T2.append(float("NaN"))
        if Temp3 != -127 and Temp3 != 85:
            T3.append(Temp3)
        else:
            T3.append(float("NaN"))
        if Temp4 != -127 and Temp4 != 85:
            T4.append(Temp4)
        else:
            T4.append(float("NaN"))
        if Temp5 != -127 and Temp5 != 85:
            T5.append(Temp5)
        else:
            T5.append(float("NaN"))
        if Temp6 != -127 and Temp6 != 85:
            T6.append(Temp6)
        else:
            T6.append(float("NaN"))
        if Temp7 != -127 and Temp7 != 85:
            T7.append(Temp7)
        else:
            T7.append(float("NaN"))
        if Temp8 != -127 and Temp8 != 85:
            T8.append(Temp8)
        else:
            T8.append(float("NaN"))
        ID.append(Identifier)
    if not T1:
        return

    plt.plot(
        ID, T1, ID, T2, ID, T3, ID, T4, ID, T5, ID, T6, ID, T7, ID, T8
    )  # plot graph - wants to be in own function.
    plt.xticks(rotation=45)
    plt.grid()
    plt.title("Livestock Internal Temperature")
    plt.xlabel("Time || days/hrs")
    plt.ylabel("Temperature ˚C")
    plt.savefig(filename, bbox_inches="tight")
    os.system(
        "mv " + filename + " ~/flaskapp/static/maps/"
    )  # move to correct folder so server can find the file
    plt.clf()


def LatLonNamedLocation(latitude,longitude):
    geolocator = Nominatim(user_agent="geoapiExercises")
    coords = str(latitude) + "," + str(longitude)
    location = geolocator.reverse(coords, exactly_one=True)
    name = location.raw["display_name"]
    return name