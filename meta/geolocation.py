import numpy as np
from geopy.geocoders import Nominatim
geolocator = Nominatim(user_agent="MyApp")


def input_geolocation(list_of_cities, df, var):
    df[var + ' latitude'] = np.nan
    df[var + ' longitude'] = np.nan
    for item in list_of_cities:
        latitude = geolocator.geocode(item).latitude
        longitude = geolocator.geocode(item).longitude
        df[var + ' latitude'] = np.where(df[var] == item, latitude, df[var + ' latitude'])
        df[var + ' longitude'] = np.where(df[var] == item, longitude, df[var + ' longitude'])
    return df