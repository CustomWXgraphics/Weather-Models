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
hour = 45

#Select variables from dataset
lon = data["lon"]
lat = data["lat"]
uwind = data["u-component_of_wind_isobaric"][hour].sel(isobaric5=20000)
vwind = data["v-component_of_wind_isobaric"][hour].sel(isobaric5=20000)
Geo_250 = data["Geopotential_height_isobaric"][hour].sel(isobaric3=25000) / 10

#assign time variables
time1 = datetime.strptime(str(data.time.data[hour].astype('datetime64[ms]')),
                          '%Y-%m-%dT%H:%M:%S.%f')
time2 = datetime.strftime(time1, "%Y-%m-%d %H00 UCT")

sped_250 = mpcalc.wind_speed(uwind, vwind).to('kt')

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
Valid1 = datetime.strptime(str(data.time1.data[hour].astype('datetime64[ms]')),
                          '%Y-%m-%dT%H:%M:%S.%f')
Valid = datetime.strftime(Valid1, "%Y-%m-%d %Hz")

Init1 = datetime.strptime(str(data.time.data[0].astype('datetime64[ms]')),
                          '%Y-%m-%dT%H:%M:%S.%f')  -timedelta(hours=3)
Init = datetime.strftime(Init1, "%Y-%m-%d %Hz")

#Find Forecast hour
Valid1 - Init1
data = pd.date_range(start=Init1, end=Valid1, freq='60min')
hours = len(data) -1 + 6

#create colormap with matplotlib.colors
cmap = col.ListedColormap(["#DDDDDD","#C3C3C3","#A9A9A9","#02A7F7","#0081D1","#005AA9","#00B51A","#44CF12","#89E708","#CDFF00",
                          "#EBFF00","#F1FF00","#F7FF00","#FDFF00","#FFB300","#FF7800","#FF5C00","#FF4000","#F93100","#FF0800",
                          "#B23116","#A36234","#C69066","#E9BD99","#FED2B6","#FCB89E","#F99C8A","#F97F72","#FE0783"])  

#Create intervals and normalize color pallet
clevs = np.arange(15,210,5)
norm = col.BoundaryNorm(clevs,cmap.N)

#Plot Colors
Vorticity = ax.contourf(lon, lat, sped_250, levels=clevs,  transform=ccrs.PlateCarree(), cmap=cmap , zorder=2, extend="max")
cbar = plt.colorbar(Vorticity, shrink=.74,pad=0.01, aspect=30, ticks=clevs)

skip=10
ax.barbs(lon[::skip], lat[::skip], u.m[::skip,::skip], v.m[::skip,::skip],  zorder=10)

#Plot contour lines
ax.contour(lon,lat,Geo_250, 30, colors="black")

#Add watermark
plt.text(0.99,0.02,'Graphics By: @CustomWX',
        ha='right',va='bottom',transform=ax.transAxes,fontsize=12,color='black',fontweight='bold'
            , bbox={'facecolor':'white', 'alpha':1, 'boxstyle':'square'}, zorder=15)

#Plot Title
fig.suptitle(r"0.25$^o$ GFS | 200mb Wind (KT) | 200mb Heights (dm) ", transform=ax.transAxes, fontweight="bold", fontsize=15, y=1.084, x=0, ha="left", va="top")
plt.title(f"Init: {Init} | Valid: {Valid} | Hour: [{hours}]",x=0.0, y=1.017, fontsize=15, loc="left", transform=ax.transAxes)


plt.show()
