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

hour = 25

lat = data.lat.values
lon = data.lon.values
mslp = data["Pressure_reduced_to_MSL_msl"][hour] / 100
zr = data["Categorical_Freezing_Rain_surface"][hour]
ip = data["Categorical_Ice_Pellets_surface"][hour]
sn = data["Categorical_Snow_surface"][hour]
rate = data["Precipitation_rate_surface"][hour] * 1500

#Heights
Geo_500 = data["Geopotential_height_isobaric"][hour].sel(isobaric3=50000.0) / 10
Geo_1000 = data["Geopotential_height_isobaric"][hour].sel(isobaric3=100000.0) / 10
remain = Geo_500 - Geo_1000

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

def smooth(prod,sig):
    
    #Check if variable is an xarray dataarray
    try:
        lats = prod.lat.values
        lons = prod.lon.values
        prod = ndimage.gaussian_filter(prod,sigma=sig,order=0)
        prod = xr.DataArray(prod, coords=[lats, lons], dims=['lat', 'lon'])
    except:
        prod = ndimage.gaussian_filter(prod,sigma=sig,order=0)
    
    return prod

#Label MSLP extrema
def extrema(mat,mode='wrap',window=75):
        mn = minimum_filter(mat, size=window, mode=mode)
        mx = maximum_filter(mat, size=window, mode=mode)
        return np.nonzero(mat == mn), np.nonzero(mat == mx)

def mslp_label(mslp,lat,lon):
    
    #Determine an appropriate window given the lat/lon grid resolution
    mslp = np.ma.masked_invalid(mslp)
    local_min, local_max = extrema(mslp, mode='wrap', window=50)
    
    #Determine axis boundaries
    xmin, xmax, ymin, ymax = ax.get_extent()
    lons2d, lats2d = np.meshgrid(lon, lat)
    transformed = proj_ccrs.transform_points(ccrs.PlateCarree(), lons2d, lats2d)
    x = transformed[..., 0]
    y = transformed[..., 1]
    
    #Get location of extrema on grid
    xlows = x[local_min]; xhighs = x[local_max]
    ylows = y[local_min]; yhighs = y[local_max]
    lowvals = mslp[local_min]; highvals = mslp[local_max]
    yoffset = 0.022*(ymax-ymin)
    dmin = yoffset
    
    #Plot low pressures
    xyplotted = []
    for x,y,p in zip(xlows, ylows, lowvals):
        if x < xmax-yoffset and x > xmin+yoffset and y < ymax-yoffset and y > ymin+yoffset:
            dist = [np.sqrt((x-x0)**2+(y-y0)**2) for x0,y0 in xyplotted]
            if not dist or min(dist) > dmin: #,fontweight='bold'
                a = ax.text(x,y,'L',fontsize=20, 
                        ha='center',va='center',color='r',fontweight='normal')
                b = ax.text(x,y-yoffset,repr(int(p)),fontsize=12, 
                        ha='center',va='top',color='r',fontweight='normal')
                a.set_path_effects([path_effects.Stroke(linewidth=1.5, foreground='black'),
                       path_effects.SimpleLineShadow(),path_effects.Normal()])
                b.set_path_effects([path_effects.Stroke(linewidth=1.5, foreground='black'),
                       path_effects.SimpleLineShadow(),path_effects.Normal()])
                xyplotted.append((x,y))
                
    #Plot high pressures
    xyplotted = []
    for x,y,p in zip(xhighs, yhighs, highvals):
        if x < xmax-yoffset and x > xmin+yoffset and y < ymax-yoffset and y > ymin+yoffset:
            dist = [np.sqrt((x-x0)**2+(y-y0)**2) for x0,y0 in xyplotted]
            if not dist or min(dist) > dmin:
                a = ax.text(x,y,'H',fontsize=20, 
                        ha='center',va='center',color='b',fontweight='normal')
                b = ax.text(x,y-yoffset,repr(int(p)),fontsize=12,  
                        ha='center',va='top',color='b',fontweight='normal')
                a.set_path_effects([path_effects.Stroke(linewidth=1.5, foreground='black'),
                       path_effects.SimpleLineShadow(),path_effects.Normal()])
                b.set_path_effects([path_effects.Stroke(linewidth=1.5, foreground='black'),
                       path_effects.SimpleLineShadow(),path_effects.Normal()])
                xyplotted.append((x,y))

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

snow = np.where(sn >= 1, rate, sn)
zr = np.where(zr >= 1, rate, zr)
ip = np.where(ip >= 1, rate, ip)

clevs = [0.1,0.3,0.5,0.7,1,1.5,2,2.5,3,5,7,10,15,20,25]

cmap= col.ListedColormap(["#00FF01","#00E600","#00CC01","#00AB01","#018100","#006300", "#FFFF00","#FED500","#FF8E00","#FF0100",
                         "#C60001","#970001","#FF00FF","#AB00FF"])
norm = col.BoundaryNorm(clevs,cmap.N)


snow_cmap = col.ListedColormap(["#00E7FF","#00CEFD","#00BCFF","#009CFF","#007DFF","#005FFF","#0024FF","#000EFF"
                                ,"#6519FF","#B25DD8","#EC76E2","#E362D5","#DA4EC8","#D03BBC",])

mix_cmap = col.ListedColormap(["#DA4EC8","#D03BBC","#C727AF","#BD14A2","#AA0088","#B40B7C","#BD126F"
                                ,"#C71A63","#D02357","#DA2C49","#E4333E","#EC3D32","#F84528",])

ice_cmap = col.ListedColormap(["#FDC18A","#FDB678","#FDA966","#FD9D53","#FA9144","#EE6B1A","#E45709"
                                ,"#D04A05","#BB3D02","#A23403","#8E2D04"])


rate = ax.contourf(lon, lat, rate, clevs, transform=ccrs.PlateCarree(),cmap=cmap, norm=norm)

try:
    snow = ax.contourf(lon, lat, snow, clevs, transform=ccrs.PlateCarree(),cmap=snow_cmap, norm=norm)
except:
    pass
try:
    zr = ax.contourf(lon, lat, zr, clevs, transform=ccrs.PlateCarree(),cmap=ice_cmap, norm=norm)
except:
    pass
try:
    ip = ax.contourf(lon, lat, ip, clevs, transform=ccrs.PlateCarree(),cmap=mix_cmap, norm=norm)
except:
    pass


cbar = plt.colorbar(rate, shrink=.70,pad=0.01, aspect=35, ticks=clevs)

print("----> Plotted Preciptation Type")


remain = ndimage.gaussian_filter(remain,sigma=5,order=0)

below = np.arange(474,541,6)
above = np.arange(543,598,6)

#Plot data
A = ax.contour(lon, lat, remain, above, transform=ccrs.PlateCarree(), linestyles="dashed", colors="red", linewidths=1, alpha=0.7)
B = ax.contour(lon, lat, remain, below, transform=ccrs.PlateCarree(), linestyles="dashed", colors="blue", linewidths=1, alpha=0.7)

ax.clabel(A, fmt="%0.0f")
ax.clabel(B, fmt="%0.0f")

B.collections[11].set_color("blue")
B.collections[11].set_linewidth(2)
B.collections[11].set_linestyle("-")

print("----> Plotted Heights")

mslp = ndimage.gaussian_filter(mslp,sigma=5,order=0)

contour = ax.contour(lon,lat, mslp, 15, transform=ccrs.PlateCarree(), colors="#666666", linewidths=1, zorder=5)
ax.clabel(contour, fmt="%0.0f")

mslp_label(mslp,lat,lon)

print("----> Plotted MSLP")

#Add watermark
plt.text(0.99,0.02,'Graphics By: @CustomWX',
        ha='right',va='bottom',transform=ax.transAxes,fontsize=12,color='black',fontweight='bold'
            , bbox={'facecolor':'white', 'alpha':1, 'boxstyle':'square'}, zorder=15)

#Plot Title
fig.suptitle(r"0.25$^o$ GFS | Precipitation Rate & Type [in] | MSLP [hPa] | 500-1000mb Thickness", transform=ax.transAxes, fontweight="bold", fontsize=15, y=1.084, x=0, ha="left", va="top")
plt.title(f"Init: {Init} | Valid: {Valid} | Hour: [{hours}]",x=0.0, y=1.017, fontsize=15, loc="left", transform=ax.transAxes)

print("----> Plotted Map")

plt.show()