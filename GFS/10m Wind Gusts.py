#import necessary libraries
import cartopy.crs as ccrs
import cartopy.feature as cfeat
import matplotlib.pyplot as plt
import matplotlib.colors as col
import matplotlib.patheffects as path_effects
import xarray as xr
import numpy as np
from datetime import datetime, timedelta
from scipy.ndimage.filters import maximum_filter, minimum_filter
import datetime as dt
import pandas as pd

from metpy.units import units
import metpy.calc as mpcalc


#To allow multiple files to run
plt.rcParams.update({'figure.max_open_warning': 0})

#Find the closest date and time
time = dt.datetime.now()
year = time.year
month = time.month
day = time.day
hour = time.hour
    
if day >= 10 and month >= 10:
    run_date = str(year) + str(month) + str(day)
elif month <= 10 or day <= 10:
    if month <= 10 and 10 <= day:
        run_date = str(year) + str(0) + str(month) + str(day)
    elif day <= 10 and 10 <= month:
        run_date = str(year) + str(month) + str(0) + str(day)
    elif day <= 10 and month <= 10:
        run_date = str(year) + str(0) + str(month) + str(0) + str(day)

if hour in range(0,7):
    run_hour = "0000"
elif hour in range(7,13):
    run_hour = "0600"
elif hour in range(13,19):
    run_hour = "1200"
elif hour in range(19,24):
    run_hour = "1800"

#Set dataset name
dataset = f"https://thredds-test.unidata.ucar.edu/thredds/dodsC/grib/NCEP/GFS/Global_0p25deg/GFS_Global_0p25deg_{run_date}_{run_hour}.grib2"

#Select regions to slice from dataset to make it faster
lat_north = 55
lat_south = -10
lon_west = 360
lon_east = 250
#Define data
data = xr.open_dataset(dataset)
#Slice data
data = data.sel(lat=slice(lat_north,lat_south), lon=slice(lon_east,lon_west))

#Select starting hour
hour = 35

#Select variables from dataset
lon = data["lon"]
lat = data["lat"]
Gust = data["Wind_speed_gust_surface"][hour] * 2.23694

#assign time variables
time1 = datetime.strptime(str(data.time.data[hour].astype('datetime64[ms]')),
                          '%Y-%m-%dT%H:%M:%S.%f')
time2 = datetime.strftime(time1, "%Y-%m-%d %H00 UCT")

#Create figure
fig = plt.figure(figsize=(14,9))
ax = fig.add_axes([1,1,1,1],projection=ccrs.Miller())

#List map Coordinates
Lat_west = -105
Lat_east =-55
Lon_south = 15
Lon_north = 38

#Plot extent
ax.set_extent([Lat_east, Lat_west, Lon_north, Lon_south])

#add landforms
ax.add_feature(cfeat.LAKES.with_scale('50m'), facecolor='white')
ax.add_feature(cfeat.STATES.with_scale('50m'), linewidth=0.4, zorder=7)
ax.add_feature(cfeat.COASTLINE.with_scale('50m'), edgecolor='#4F5457', zorder=6)
ax.add_feature(cfeat.BORDERS.with_scale('50m'), edgecolor='#4F5457', zorder=8)

#define times
if run_hour == "0600" or "1800":
    Init1 = datetime.strptime(str(data.time.data[0].astype('datetime64[ms]')),
                            '%Y-%m-%dT%H:%M:%S.%f')  -timedelta(hours=3)
    Init = datetime.strftime(Init1, "%Y-%m-%d %Hz")
else:
    Init1 = datetime.strptime(str(data.time.data[0].astype('datetime64[ms]')),
                            '%Y-%m-%dT%H:%M:%S.%f') 
    Init = datetime.strftime(Init1, "%Y-%m-%d %Hz")
    
Valid1 = datetime.strptime(str(data.time1.data[hour].astype('datetime64[ms]')),
                          '%Y-%m-%dT%H:%M:%S.%f')
Valid = datetime.strftime(Valid1, "%Y-%m-%d %Hz")

#Find Forecast hour
Valid1 - Init1
data = pd.date_range(start=Init1, end=Valid1, freq='60min')
hours = len(data) -1 + 6

clevs_2 = [0,4,6,7,8,9,10,12,14,16,18,20,22,24,26,28,30,32,34,36,
           38,40,42,44,46,48,50,52,54,56,58,60,62,64,66,70,75,80,85,
           90,95,100]

wind_cmap= col.ListedColormap(["#ffffff","#D2D2D2","#BCBCBC","#969696","#646464","#1464D2","#1E6EEB","#2882F0","#3C96F5","#50A5F5","#78B9FA","#78B9FA",
                         "#96D2FA","#B4F0FA","#0FA00F","#1DB31D","#36D03B","#77F372","#96F58C","#B4FAAA","#C8FFBE","#FFE878","#FFC03C",
                         "#FFA000","#FF6000","#FF3200","#DF1300","#C00000","#A40000","#633B31","#774F45","#8C645A","#A0786E","#E1BEB4",
                         "#F0DCD2","#FFC8C8","#F5A1A1","#EE7F7F","#E45D5D","#DC3E3E","#D72F2F","#C92929","#B62727","#B13030","#AC4545",
                          "#A25A5A","#977372","#918080","#7D7D7D"])

norm = col.BoundaryNorm(clevs_2,wind_cmap.N)

wind = ax.contourf(lon,lat, Gust, clevs_2, transform=ccrs.PlateCarree(), cmap=wind_cmap, norm=norm)

cbar = plt.colorbar(wind, shrink=.74,pad=0.01, aspect=30, ticks=clevs_2)


#Add watermark
plt.text(0.99,0.02,'Graphics By: @CustomWX',
        ha='right',va='bottom',transform=ax.transAxes,fontsize=12,color='black',fontweight='bold'
            , bbox={'facecolor':'white', 'alpha':1, 'boxstyle':'square'}, zorder=15)

#Plot Title
fig.suptitle(r"0.25$^o$ GFS | 10m Wind Gusts [mph] ", transform=ax.transAxes, fontweight="bold", fontsize=15, y=1.084, x=0, ha="left", va="top")
plt.title(f"Init: {Init} | Valid: {Valid} | Hour: [{hours}]",x=0.0, y=1.017, fontsize=15, loc="left", transform=ax.transAxes)
