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
import scipy.ndimage as ndimage
from scipy.ndimage.filters import minimum_filter, maximum_filter
import matplotlib.patheffects as path_effects
import matplotlib as mpl


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
lon_east = 220
data = xr.open_dataset(dataset)
data = data.sel(lat=slice(lat_north,lat_south), lon=slice(lon_east,lon_west))

hour = 20

lat = data.lat.values
lon = data.lon.values

snow_equiv = data["Water_equivalent_of_accumulated_snow_depth_surface"][hour] * 0.04 *10


print("----> Read and defined data")

#plot figure
proj_ccrs = ccrs.LambertConformal()

#plot figure
fig = plt.figure(figsize=(18,12))
ax = plt.subplot(1,1,1, projection=ccrs.LambertConformal()) #main plot

transform = ccrs.PlateCarree()._as_mpl_transform(ax)

#add landforms
ax.add_feature(cfeat.LAKES.with_scale('50m'), facecolor='#ABD9ED', zorder=0)
ax.add_feature(cfeat.STATES.with_scale('50m'), linewidth=0.6, edgecolor='#404040', zorder=2)
ax.add_feature(cfeat.COASTLINE.with_scale('50m'), edgecolor='#172520', linewidth=1.2)
Lat_west = -123
Lat_east = -67
Lon_south = 21
Lon_north = 50
ax.set_extent([Lat_east, Lat_west, Lon_north, Lon_south])

print("----> Set up cartopy projection & geography")


#define times
if run_hour == "0600" or "1800":
    Init1 = datetime.strptime(str(data.time.data[0].astype('datetime64[ms]')),
                            '%Y-%m-%dT%H:%M:%S.%f')-timedelta(hours=3)
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
hours = len(data) - 1

clevs = [0.1,0.5,1,1.5,2,2.5,3,3.5,4,4.5,5,5.5,6,6.5,7,7.5,8,8.5,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27,28,29,30,31,32,33,34,35,36,37,38,39,40,41,42,43,44,45,46,47,48,49]

cmap = col.ListedColormap(['#bebebe','#969696', '#6E6E6E', '#505050', '#96D2FA', '#78B9FA', '#50A5F5', '#3C96F5', 
                               '#2882F0', '#1E6EEB', '#1464D2', '#0A5AC3', '#0A5AC3', '#4D038E', '#5B038D', '#69038B', 
                               '#840388', '#A00485', '#C90481', '#F3047C', '#F83C9B', '#FC5EAE', '#FE6FB7', '#FB84C2',
                               '#F48CC6', '#F48CC6', '#E69DCD', '#D8ADD5', '#D1B6DB', '#C3C6E0', '#B6D5F0', '#ABE2F0',
                               '#A0EFF3', '#93F6F4', '#93F6F4', '#84DDDB', '#74C0C6', '#80B5CD', '#80B5CD', '#80B5CD',
                               '#8BB0D3', '#8BB0D3', '#8BB0D3', '#95A9D8', '#95A9D8', '#9D9FDA', '#A4A1E0', '#A4A1E0',
                               '#A4A1E0', '#AF9AE6', '#AF9AE6', '#BB90EC', '#BB90EC', '#BB90EC', '#C98AF5', '#C98AF5',
                               '#C98AF5', '#C98AF5', '#C98AF5'])

norm = col.BoundaryNorm(clevs,cmap.N)

rate = ax.contourf(lon,lat,snow_equiv, clevs, transform=ccrs.PlateCarree(), cmap=cmap, norm=norm)

cbar = plt.colorbar(rate, shrink=.70,pad=0.01, aspect=35, ticks=clevs[::2])

#Add watermark
plt.text(0.99,0.02,'Graphics By: @CustomWX',
        ha='right',va='bottom',transform=ax.transAxes,fontsize=12,color='black',fontweight='bold'
            , bbox={'facecolor':'white', 'alpha':1, 'boxstyle':'square'}, zorder=15)

#Plot Title
fig.suptitle(r"0.25$^o$ GFS | Snow Depth [10:1] [in]", transform=ax.transAxes, fontweight="bold", fontsize=15, y=1.084, x=0, ha="left", va="top")
plt.title(f"Init: {Init} | Valid: {Valid} | Hour: [{hours}]",x=0.0, y=1.017, fontsize=15, loc="left", transform=ax.transAxes)

print("----> Plotted Map")

plt.show()
