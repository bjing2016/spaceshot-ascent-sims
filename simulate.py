import h5py
import numpy as np 
import math
import io
import sys

EARTH_RADIUS = 6.371e6

levels = [1, 2, 3, 5, 7, 10, 20, 30, 50, 70,\
          100, 150, 200, 250, 300, 350, 400, 450,\
          500, 550, 600, 650, 700, 750, 800, 850,\
          900, 925, 950, 975, 1000]

def open_h5(filename):
    hf = h5py.File(filename, 'r')
    return hf['test']


def get_wind(data, lat_res, lon_res, level_res):
    lat_i, lat_f = lat_res
    lon_i, lon_f = lon_res
    level_i, level_f = level_res

    u = data[0][level_i][lat_i][lon_i] * lat_f * lon_f * level_f + \
        data[0][level_i][lat_i + 1][lon_i] * (1-lat_f) * lon_f * level_f + \
        data[0][level_i][lat_i][lon_i + 1] * lat_f * (1-lon_f) * level_f + \
        data[0][level_i][lat_i + 1][lon_i + 1] * (1-lat_f) * (1-lon_f) * level_f + \
        data[0][level_i + 1][lat_i][lon_i]* lat_f * lon_f * (1-level_f) + \
        data[0][level_i + 1][lat_i + 1][lon_i] * (1-lat_f) * lon_f * (1-level_f) + \
        data[0][level_i + 1][lat_i][lon_i + 1]* lat_f * (1-lon_f) * (1-level_f) + \
        data[0][level_i + 1][lat_i + 1][lon_i + 1] * (1-lat_f) * (1-lon_f) * (1-level_f)
        
    v = data[1][level_i][lat_i][lon_i] * lat_f * lon_f * level_f + \
        data[1][level_i][lat_i + 1][lon_i] * (1-lat_f) * lon_f * level_f + \
        data[1][level_i][lat_i][lon_i + 1] * lat_f * (1-lon_f) * level_f + \
        data[1][level_i][lat_i + 1][lon_i + 1] * (1-lat_f) * (1-lon_f) * level_f + \
        data[1][level_i + 1][lat_i][lon_i]* lat_f * lon_f * (1-level_f) + \
        data[1][level_i + 1][lat_i + 1][lon_i] * (1-lat_f) * lon_f * (1-level_f) + \
        data[1][level_i + 1][lat_i][lon_i + 1]* lat_f * (1-lon_f) * (1-level_f) + \
        data[1][level_i + 1][lat_i + 1][lon_i + 1] * (1-lat_f) * (1-lon_f) * (1-level_f)

    return u, v

## Array format: array[u,v][Pressure][Lat][Lon] ##
## Currently [lat 90 to -90][lon 0 to 395.5]

## Note: this returns bounds as array indices ##
def get_bounds_and_fractions (lat, lon, alt):
    
    lat_res, lon_res, pressure_res = None, None, None
    
    pressure = alt_to_hpa(alt)

    for i in range(len(levels)):
        if pressure<=levels[i]:
            fraction = (levels[i]-pressure)/(levels[i]-levels[i-1])
            pressure_res = (i - 1, fraction)
            break;
        pressure_res = i-1, 0
    
    lat = lat * 2;
    lat = 90 - lat;
    lat_res = (math.floor(lat) , 1 - lat % 1)

    
    lat = (lon % 360) * 2;
    lon_res = (math.floor(lat), 1 - lon % 1)

    return lat_res, lon_res, pressure_res


## Credits to KMarshland ##
def alt_to_hpa(altitude):
    pa_to_hpa = 1.0/100.0
    if altitude < 11000:
        return pa_to_hpa * math.exp(math.log(1.0 - (altitude/44330.7)) / 0.190266) * 101325.0
    else:
        return pa_to_hpa * math.exp(altitude / -6341.73) * 22632.1 / 0.176481


def lin_to_angular_velocities(lat, lon, u, v): 
    dlat = math.degrees(u / EARTH_RADIUS)
    dlon = math.degrees(v / EARTH_RADIUS * math.cos(math.radians(90-lat)))
    return dlat, dlon

def simulate(outstream, data, slat, slon, salt, ascent_rate, timestep_s, stop_alt):
    
    lat, lon, alt = slat, slon, salt
    time = 0

    while alt < stop_alt:
        u, v = get_wind(data, *get_bounds_and_fractions(lat, lon, alt))

        dlat, dlon = lin_to_angular_velocities(lat, lon, u, v)
            

        alt = alt + timestep_s * ascent_rate
        lat = lat + dlat * timestep_s
        lon = lon + dlon * timestep_s
        time = time + timestep_s
        print("Time="+ str(time) + "," + str(lat) + "," + str(lon) + ",alt=" + str(alt))


simulate(sys.stdout, open_h5("../../gfsanl/2018020300.h5"), 37, -122, 0, 5, 300, 15000)

