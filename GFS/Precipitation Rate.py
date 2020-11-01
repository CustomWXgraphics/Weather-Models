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

lat_north = 55
lat_south = -10
lon_west = 360
lon_east = 250
data = xr.open_dataset(dataset)
data = data.sel(lat=slice(lat_north,lat_south), lon=slice(lon_east,lon_west))

#Select hour
hour = 40

lon = data["lon"]
lat = data["lat"]
rate = data["Precipitation_rate_surface_Mixed_intervals_Average"][hour] * 900
msl_hp = data["Pressure_reduced_to_MSL_msl"][hour] / 100

#Plot time
time1 = datetime.strptime(str(data.time.data[hour].astype('datetime64[ms]')),
                          '%Y-%m-%dT%H:%M:%S.%f')
time2 = datetime.strftime(time1, "%Y-%m-%d %H00 UCT")

#Create figure
fig = plt.figure(figsize=(14,9))
ax = fig.add_axes([1,1,1,1],projection=ccrs.Miller())

#List Coordinates
Lat_west = -105
Lat_east =-55
Lon_south = 15
Lon_north = 38

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
data = pd.date_range(start=Init1, end=Valid1, freq='60min')
hours = len(data) -1 + 6

    
clevs = [0.01,0.03,0.05,0.07,0.1,0.15,0.2,0.25,0.3,0.4,0.5,0.6,0.7,0.8,0.9,1.0,
         1.2,1.4,1.6,1.8,2,2.5,3,3.5,4, 5,6,7,8,9,10,11,12,13,14,15,16,17,18,19]

#Create Colormap
cmap= col.ListedColormap(["#BEBEBE","#AAA5A5","#828282","#6E6E6E","#B4FAAA","#96F58C",
                          "#78F573","#50F050","#1EB41E","#0FA00F","#1464D2","#2882F0",
                         "#50A5F5","#96D2FA","#B4F0FA","#FFFAAA","#FFE878","#FFC03C",
                          "#FFA000","#FE5F00","#FE3100","#E11400","#BF0000","#A40000",
                         "#870000","#643C32","#8C645A","#B48C82","#C8A096","#F0DCD2",
                          "#CFC8DF","#ADA0C9","#9988BB","#735CA3","#685393","#770077",
                          "#8B008B","#B100B1","#C400C4","#DB00DB"])

norm = col.BoundaryNorm(clevs,cmap.N)

rate = ax.contourf(lon,lat,rate, clevs, transform=ccrs.PlateCarree(), norm=norm, cmap=cmap)

ax.contour(lon,lat, msl_hp, 20, transform=ccrs.PlateCarree(), colors="black")

cbar = plt.colorbar(rate, shrink=.74,pad=0.01, aspect=30, ticks=clevs)

#Add watermark
plt.text(0.99,0.02,'Graphics By: @CustomWX',
        ha='right',va='bottom',transform=ax.transAxes,fontsize=12,color='black',fontweight='bold'
            , bbox={'facecolor':'white', 'alpha':1, 'boxstyle':'square'}, zorder=15)

#Plot Title
fig.suptitle(r"0.25$^o$ GFS | Precipitation rate [in] | MSLP [hPa] ", transform=ax.transAxes, fontweight="bold", fontsize=15, y=1.084, x=0, ha="left", va="top")
plt.title(f"Init: {Init} | Valid: {Valid} | Hour: [{hours}]",x=0.0, y=1.017, fontsize=15, loc="left", transform=ax.transAxes)