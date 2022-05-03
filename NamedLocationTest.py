from geopy.geocoders import Nominatim
import folium
import matplotlib.pyplot as plt
import app as telemetry
from datetime import datetime, timedelta
import os

import branca
import branca.colormap as cm

geolocator = Nominatim(user_agent="geoapiExercises")
def city_state_country(coord):
    locator = Nominatim(user_agent="myGeocoder")
    coordinates = "55.70051, -2.51572"
    location = locator.reverse(coordinates)
    name = location.raw["display_name"]
    print(name)

        
def RenderMap(dateTimeNow,dateTimeSart,BoxNumber,filename):

    currentLocation, dataRange, TempRange = PlotLivestockRoute(boxNumber,dateTimeNow,dateTimeStart)
    my_map = folium.Map(currentLocation, zoom_start=12)
    folium.PolyLine(dataRange, color="#0e4a99", weight=6, opacity=1).add_to(my_map)
    colorlist = []
    i = 0
    switch = 1
    while i < (len(dataRange)-1):
        if switch == 1:
            colorlist.append('green')
            switch = 2
        elif switch ==2:
            colorlist.append('red')
            switch = 3
        elif switch == 3:
            colorlist.append('blue')
            switch = 4
        else:
            colorlist.append("yellow")
            switch = 1
        i = i+1
    print(len(dataRange))
    colormap = plt.get_cmap('hsv', 256)
    colormap = cm.LinearColormap(
                                (   "#ffff00",
                                    "#00ff00",
                                    "#00ffff",
                                    "#0000ff",
                                    "#ff00ff",
                                    "#ff0000"   )
                                ,index=None,vmin=0,vmax=20)
    folium.ColorLine(positions=dataRange, colors=TempRange,colormap=colormap,nb_steps=80,weight=4,opacity=0.9).add_to(my_map)
    folium.CircleMarker(currentLocation,radius=12,fill=True,opacity=1,popup="hello",color="green").add_to(my_map)
    my_map.save(filename)
    os.system("mv "+ filename+" ~/flaskapp/static/maps/")




def rainbow():
  r, g, b = 255, 0, 0
  for g in range(256):
    yield r, g, b
  for r in range(255, -1, -1):
    yield r, g, b
  for b in range(256):
    yield r, g, b
  for g in range(255, -1, -1):
    yield r, g, b
  for r in range(256):
    yield r, g, b
  for b in range(255, -1, -1):
    yield r, g, b

folium_map()
rainbow()