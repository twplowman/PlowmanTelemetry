from geopy.geocoders import Nominatim
import folium
import matplotlib.pyplot as plt
import app as telemetry
from datetime import datetime, timedelta
import os

import branca
import branca.colormap as cm

geolocator = Nominatim(user_agent="geoapiExercises")

def test():
  config = telemetry.MysqlConfig()
  mydb = telemetry.mysql.connector.connect(**config)
  cursor = mydb.cursor()
  query = "SELECT BoxNumber FROM PBL_Telemetry_Summary;"
  cursor.execute(query)
  livestockBoxes = []
  for BoxNumber in cursor:
    livestockBoxes.append(BoxNumber[0])
  return livestockBoxes




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