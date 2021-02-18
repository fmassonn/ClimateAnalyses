#!/usr/bin/python3

from netCDF4 import Dataset
import numpy as np
import matplotlib.pyplot as plt
import datetime
from datetime import timedelta
import os

# yearb = 1979
# yeare = 2020
# # Sub-set dates to choose:

# import cdsapi

# offset = -273.15 # K to °C

# sYears  = [str(y)                  for y in range(yearb, yeare + 1)]
# years= np.array([int(y) for y in sYears])
# sMonths = [str(m)                  for m in range(1, 12 + 1)       ]
# months = [int(m) for m in sMonths]
# sHours  = [str(h).zfill(2) + ":00" for h in range(0, 23 + 1)       ]   

# lonmin, lonmax = 2, 6
# latmin, latmax = 48, 53


def retrieveData():
    c = cdsapi.Client()
    data = c.retrieve(
                'reanalysis-era5-single-levels-monthly-means',
                {
                    'product_type': 'monthly_averaged_reanalysis_by_hour_of_day',
                    'format': 'netcdf',
                    'variable': ['2m_temperature'], 
                    'year': sYears,
                    'month': sMonths,
                    'time': sHours,
                    'area': [
                        latmax, lonmin, latmin,
                        lonmax,
                        ],
                    },
                "download.nc"
                )


def retrieveERA20C():
    yearb = 1900
    yeare = 2010
    # Sub-set dates to choose:
    dates = "/".join([str(year) + str(month).zfill(2) + "01" for \
             year in range(yearb, yeare + 1) for month in range(1, 13)])
    from ecmwfapi import ECMWFDataServer
    server = ECMWFDataServer()
    server.retrieve({
    "class": "e2",
    "dataset": "era20c",
    "date": dates,
    "expver": "1",
    "levtype": "sfc",
    "param": "167.128",
    "stream": "moda",
    "type": "an",
    'area': [
                        latmax, lonmin, latmin,
                        lonmax,
                        ],
    "grid":   "0.25/0.25",
    "target": "ERA20C",
                })
    
    os.system("/usr/local/bin/cdo -f nc copy -setgridtype,regular ERA20C ERA20C.nc")
    print("CONVERT TO NETCDF")
    print("cdo -f nc copy -setgridtype,regular ERAC out.nc")
    

#retrieveERA20C()


#retrieveData()


def getUccle():
    myList = list()
    import csv
    with open('./data_uccle.csv') as csv_file:
        csv_reader = csv.reader(csv_file, delimiter= '\t', )
        line_count = 0
        for row in csv_reader:
            if line_count > 0:
                year = int(row[0][:4])
                month = int(row[0][4:6])
                day = int(row[0][6:8])
                
                value1 = float(row[2])
                value2 = float(row[1])
                value = (value1 + value2) / 2
                # mean taken as mean between max and min
                myList.append([datetime.date(year, month, day) , value\
                               ])
            line_count += 1
    return myList

data = getUccle()


# # Get the downloaded data in arrays
# f = Dataset("./download.nc", mode = "r")
# lat = f.variables["latitude"][:]
# lon = f.variables["longitude"][:]
# var = f.variables["t2m"][:, 0, :, :] + offset
# time = f.variables["time"][:]

# dates = [datetime.datetime(1900,1, 1) + timedelta(hours = int(t)) \
#          for t in time]


# # Annual averages


# # Find indices of Brussels
# iX = np.where(lat == 50.75)[0][0]
# jX = np.where(lon == 4.25 )[0][0]

# if len(lon.shape) == 1:
#     lon, lat = np.meshgrid(lon, lat)
    
# f.close()

# mylist = list()

# # Brussels
# spaceIndices = (lat == 50.75) * (lon == 4.25)

years = np.arange(1901, 2018 + 1)
myList = list()
for y in years:
    tmp = np.mean([d[1] for d in data \
                   if d[0].year == int(y)])

    myList.append(tmp)
        

series = np.array(myList)


for y in np.arange(1931, 2019):
    print(y)
    # We browse through all years and compute anomalies relative 
    # to the three closest full decades
    
    ye = int(np.floor(y / 10) * 10)
    yb = ye - 30 + 1
    
    fig , ax = plt.subplots(2, 1, figsize = (5, 5), dpi = 300)

    # Plot raw data

    ax[0].set_ylim(5, 15)
    ax[0].grid()
    
    for j, year in enumerate(np.arange(1901, 2019)):
        # If before current year, in green
        if year <= y:
            ax[0].bar(year, series[j], color = "lightgreen", alpha = 0.8)
        else:
            ax[0].bar(year, series[j], edgecolor = "white", \
                      color = "black", lw = 0.2)
        
        
    ax[0].set_facecolor("black")
    ax[0].set_xlim(1900, 2021)

    
    avg = np.mean(series[(years >= yb) * (years <= ye)])
    ax[0].plot((yb, ye), (avg, avg), color = "white", lw = 2)


    ano = series - avg
    for j, year in enumerate(np.arange(1901, 2019)):
        if year <= y:
            color = plt.cm.RdBu_r(int((ano[j] + 3) * 255 / 6))
            ax[1].bar(year, ano[j], color = color, lw = 0)
        else:
            ax[1].bar(year, ano[j], edgecolor = "white", \
                      color = "black", lw = 0.2)
    ax[1].set_xlim(1900, 2021)
    ax[1].set_facecolor("black")
    ax[1].set_axisbelow(True)
    ax[1].grid()
    ax[1].set_ylim(-2.5, 2.5)
    ax[1].set_title("Anomalies par rapport à la moyenne " + \
                    str(yb) + "-" + str(ye))
    
    ax[0].text(yb, 11, "Période de référence", color = "white")
    ax[0].set_ylabel("°C")
    ax[0].set_title("Température annuelle moyenne à Uccle")
    ax[0].set_axisbelow(True)


    fig.tight_layout()
    fig.savefig("./figs/fig_" + str(y) + ".png")






