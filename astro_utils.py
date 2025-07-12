import swisseph as swe
import datetime

# Set Swiss Ephemeris path (leave blank if using pip-installed version)
swe.set_ephe_path("")

# Get Julian Day
def get_julian_day(date):
    return swe.julday(date.year, date.month, date.day)

# Check Moon Phase: New Moon or Full Moon
def is_new_moon_or_full_moon(date=None):
    if date is None:
        date = datetime.datetime.now().date()
    jd = get_julian_day(date)
    moon_phase = swe.pheno(jd, swe.MOON)[1]  # Angle between Sun and Moon
    if moon_phase < 10:
        return "NEW_MOON"
    elif abs(moon_phase - 180) < 10:
        return "FULL_MOON"
    else:
        return None

# Check if Planet is Retrograde
def is_planet_retrograde(planet_name="Mercury", date=None):
    if date is None:
        date = datetime.datetime.now().date()
    jd = get_julian_day(date)
    planet_id = getattr(swe, planet_name.upper())
    position, _ = swe.calc_ut(jd, planet_id)
    speed = position[3]  # 4th value = speed (deg/day)
    return speed < 0

# Get Astro Flags for Today
def get_astro_flags(date=None):
    if date is None:
        date = datetime.datetime.now().date()
    flags = {}

    moon_phase = is_new_moon_or_full_moon(date)
    if moon_phase:
        flags[moon_phase] = 1

    for planet in ["Mercury", "Venus", "Mars", "Jupiter", "Saturn"]:
        if is_planet_retrograde(planet, date):
            flags[f"{planet.upper()}_RETRO"] = 1

    return flags
