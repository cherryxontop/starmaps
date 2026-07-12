import json
from datetime import datetime, timezone
import matplotlib as plt
import numpy as np
from astropy.coordinates import EarthLocation, AltAz, SkyCoord
from astropy.time import Time
import astropy.units as u

# edit here

LOCATION_NAME = "canberra"
LATITIDE = "-35.2809"
LONGTIDUE = 149.1300
ELEVATION_M = 577
WHEN = None # setting datetime. none = right now; datetime(2026, 7, 12, 0, 0)
MAG_LIMIT = 5.0
CATALOG_PATH = "bsc5.json"


# catalog

# right ascension parser. data has h, m, s so we gotta remove that ugh
def parse_ra(ra_str):
    """'00h 05m 09.9s' -> decimal hours"""
    h, m, s = ra_str.replace("h", "").replace("m", "").replace("s", "").split()
    return float(h) + float(m) / 60 + float(s) / 3600

# declination parser. dec is like latitude but in degrees/arcminutes/arcseconds and it can be -ve = southern sky
def parse_dec(dec_star):
    """'+45° 13′ 45″' -> decimal degrees"""
    sign = -1 if dec_star.strip().startswith("-") else 1 # grabs sign first bc float() cant handle special unicode. weak.
    dec_star = dec_star.replace("+", "").replace("-", "")
    d, m, s = dec_star.replace("°", " ").replace("′", " ").replace("″", "").split()
    return sign * (float(d) + float(m) / 60 + float(s) / 3600) # sign reapplied :3

