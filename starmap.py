import json
from datetime import datetime, timezone
import matplotlib.pyplot as plt
import numpy as np
from astropy.coordinates import EarthLocation, AltAz, SkyCoord
from astropy.time import Time
import astropy.units as u

# edit here

location = "cotonou"
lat = 6.379448
long = 2.451324
elevation = 7
when = datetime(2008, 3, 15, 0, 0) # setting datetime. none = right now; datetime(2026, 7, 12, 0, 0)
maglimit = 5.0
catalog = "resources/bsc5.json"


# catalog

# right ascension parser.
def parse_ra(ra_str):
    """'00h 05m 09.9s' -> decimal hours"""
    h, m, s = ra_str.replace("h", "").replace("m", "").replace("s", "").split()
    return float(h) + float(m) / 60 + float(s) / 3600

# declination parser
def parse_dec(dec_star):
    """'+45° 13′ 45″' -> decimal degrees"""
    sign = -1 if dec_star.strip().startswith("-") else 1 # grabs sign first bc float() cant handle special unicode; weak.
    dec_star = dec_star.replace("+", "").replace("-", "")
    d, m, s = dec_star.replace("°", " ").replace("′", " ").replace("″", "").split()
    return sign * (float(d) + float(m) / 60 + float(s) / 3600) # sign reapplied :3

def load_catalog(path, maglimit):
    with open(path) as f:
        raw = json.load(f)

    stars = []
    for entry in raw:
        try:
            vmag = float(entry["Vmag"])
            if vmag > maglimit:
                continue
            ra_hours = parse_ra(entry["RA"])
            dec_deg = parse_dec(entry["Dec"])
            stars.append(
                {
                    "ra_deg": ra_hours * 15.0,
                    "dec_deg": dec_deg,
                    "vmag": vmag,
                    "spectral": entry.get("SpectralCls", ""),
                }
            )
        except (KeyError, ValueError):
            continue
    return stars