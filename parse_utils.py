import re
from dateutil import parser as dtp

_PRICE_RE = re.compile(r"\$[\s]*([0-9][0-9,\.]*)")
_BED_RE = re.compile(r"(\d+(\.\d+)?)\s*(bed|bd|br|brm|bedroom)s?", re.I)
_BATH_RE = re.compile(r"(\d+(\.\d+)?)\s*(bath|ba|bathroom)s?", re.I)
_SQFT_RE = re.compile(r"(\d{3,5})\s*(sq\s?ft|ft²|sqft)", re.I)

def _to_int(val):
    try:
        return int(str(val).replace(",", "").replace("$",""))
    except Exception:
        return None

def _to_float(val):
    try:
        return float(val)
    except Exception:
        return None

def parse_price(text: str):
    m = _PRICE_RE.search(text or "")
    return _to_int(m.group(1)) if m else None

def parse_bedrooms(text: str):
    m = _BED_RE.search(text or "")
    return _to_float(m.group(1)) if m else None

def parse_bathrooms(text: str):
    m = _BATH_RE.search(text or "")
    return _to_float(m.group(1)) if m else None

def parse_sqft(text: str):
    m = _SQFT_RE.search(text or "")
    return _to_int(m.group(1)) if m else None

def parse_flags(text: str):
    t = (text or "").lower()
    flags = {}
    flags["has_central_air"] = int(any(x in t for x in [
        "central air", "central a/c", "central ac", "air conditioning", "a/c", "ac included"
    ]))
    flags["has_offstreet_prk"] = int(any(x in t for x in [
        "off-street parking", "off street parking", "driveway", "assigned parking", "lot parking"
    ]))
    flags["has_garage"] = int(any(x in t for x in ["garage", "detached garage", "attached garage"]))
    flags["has_dishwasher"] = int(any(x in t for x in ["dishwasher", "d/w"]))
    flags["pets_allowed"] = int(any(x in t for x in ["pets ok", "cats ok", "dogs ok", "pet friendly"]))
    return flags

def parse_when(text: str):
    try:
        dt = dtp.parse(text)
        return dt
    except Exception:
        return None

def NEIGHBORHOOD_TODO(title: str, desc: str):
    return None
