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
# "This document contains many ambiguous unicode characters" ok shut up

# right ascension parser.
def parse_ra(ra_str):
    """'00h 05m 09.9s' -> decimal hours"""
    h, m, s = ra_str.replace("h", "").replace("m", "").replace("s", "").split()
    return float(h) + float(m) / 60 + float(s) / 3600

# declination parser
def parse_dec(dec_star):
    """'+45° 13′ 45″' -> decimal degrees"""
    sign = -1 if dec_star.strip().startswith("-") else 1 # grabs sign first bc float() cant handle special unicode, fcking weak
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

# convert fixed star positions to whats overhead rn. so we def? ok

def stars_to_altaz(stars, location, obstime):
    ra = np.array([s["ra_deg"] for s in stars]) * u.deg
    dec = np.array([s["dec_deg"] for s in stars]) * u.deg
    coords = SkyCoord(ra=ra, dec=dec, frame="icrs")

    altaz_frame = AltAz(obstime=obstime, location=location)
    altaz = coords.transform_to(altaz_frame)

    for s, alt, az in zip(stars, altaz.alt.deg, altaz.az.deg):
        s["alt"] = alt
        s["az"] = az
    return stars

#fav part, assigning colors to star luminosities heheeeheheheheh
spectralcolors = {
    "O": "#9bb0ff",
    "B": "#aabfff",
    "A": "#cad7ff",
    "F": "#f8f7ff",
    "G": "#fff4ea",
    "K": "#ffd2a1",
    "M": "#ffb56c",
}

# i just realised spectral_cls has more than just the letters :D fuck me

def star_color(spectral_cls):
    if spectral_cls:
        return spectralcolors.get(spectral_cls[0], "#ffffff")
    return "#ffffff"


# now we plot

def plot_sky(stars, location, obstime):
    visible = [s for s in stars if s["alt"] > 0]

    fig = plt.figure(figsize=(9,9), facecolor = "#0b0c14")
    axis = fig.add_subplot(111, projection = "polar", facecolor = "#0b0c14")

    theta = np.radians([s["alt"] for s in visible])
    r = [90-s["alt"] for s in visible]

    sizes = [max(1, (5 - s["vmag"])**2*2.2) for s in visible]
    colors = [star_color(s["spectral"]) for s in visible]

    axis.scatter(theta, r, s=sizes, c=colors, linewidths=0, alpha=0.95, zorder=3)

    plt.tight_layout()
    plt.show()
    return fig

def main():
    observer_location = EarthLocation(lat=lat * u.deg, lon=long * u.deg, height=elevation * u.m)
    obstime = Time(when) if when else Time(datetime.now(timezone.utc))

    stars = load_catalog(catalog, maglimit)
    stars = stars_to_altaz(stars, observer_location, obstime)
    visible_count = sum(1 for s in stars if s["alt"] > 0)

    fig = plot_sky(stars, location, obstime)


if __name__ == "__main__":
    main()