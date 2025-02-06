#geoloc.py

import json
import geojson
import re
import string
import time
import logging
from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut, GeocoderServiceError
from rapidfuzz import process, fuzz

logger = logging.getLogger(__name__)

def load_geojson(filepath):
    with open(filepath, 'r', encoding='utf-8') as file:
        data = geojson.load(file)
    return data

# If you want to set a default filepath, do so here.
DEFAULT_FILEPATH = "location.geojson"

def normalize_text(text):
    if not text:
        return ''
    # Lowercase
    text = text.lower().strip()

    # Expand common abbreviations before removing punctuation
    abbreviation_mapping = {
        r'\bул\b\.?': 'улица ',
        r'\bбул\b\.?': 'булевар ',
        r'\bс\b\.?': 'село ',
        r'\bгр\b\.?': 'град ',
        r'\bмн\b\.?': 'маало ',
        r'\bпл\b\.?': 'плоштад ',
    }
    for abbr_pattern, full_form in abbreviation_mapping.items():
        text = re.sub(abbr_pattern, full_form, text)

    # Remove punctuation except commas
    punctuation_except_commas = string.punctuation.replace(',', '')
    text = text.translate(str.maketrans('', '', punctuation_except_commas))

    # Replace multiple spaces with a single space
    text = re.sub(r'\s+', ' ', text).strip()
    return text

class GeoCoder:
    def __init__(self, filepath=DEFAULT_FILEPATH):
        """
        :param filepath: path to your GeoJSON file that includes known places
        """
        self.filepath = filepath
        self.geojson_data = load_geojson(filepath)
        self.locations = self._build_locations()
        self.geolocator = Nominatim(user_agent="police_bulletin_geocoder")
        self.cache = {}

    def _build_locations(self):
        """
        Build a dict mapping normalized location names/alt_names -> [lon, lat].
        We flip to [lat, lon] only when returning from 'lookup_coordinates'.
        """
        locations = {}
        features = self.geojson_data.get('features', [])
        for feature in features:
            props = feature.get('properties', {})
            geom = feature.get('geometry', {})
            coords = geom.get('coordinates', None)

            if not coords or len(coords) < 2:
                continue  # skip if invalid geometry

            # Typically, a point geometry is [lon, lat].
            # We'll store as is, and flip in lookup_coordinates.

            name = normalize_text(props.get('name', ''))
            if name:
                locations[name] = coords

            # alt_name1, alt_name2, etc.
            for key, val in props.items():
                if key.startswith('alt_name') and val:
                    alt = normalize_text(val)
                    locations[alt] = coords
        return locations

    def geocode_location(self, location_name, retries=3):
        """
        Attempt to geocode location_name:
        1. Use a local fuzzy match from self.locations
        2. If not found, fallback to Nominatim
        3. Cache results to avoid repeated calls
        """
        if not location_name:
            return None, None

        # Check cache
        if location_name in self.cache:
            logger.debug(f"[GeoCoder] Cache hit for '{location_name}'")
            return self.cache[location_name]

        # 1) Local fuzzy match
        lat, lon = self.lookup_coordinates(location_name)
        if lat is not None and lon is not None:
            logger.info(f"[GeoCoder] Found coords in local data for '{location_name}'")
            self.cache[location_name] = (lat, lon)
            return lat, lon

        # 2) Nominatim fallback
        for attempt in range(retries):
            try:
                query = f"{location_name}, Северна Македонија"
                location = self.geolocator.geocode(query)
                if location:
                    lat, lon = location.latitude, location.longitude
                    logger.info(f"[GeoCoder] Nominatim found '{location_name}' -> ({lat}, {lon})")
                    self.cache[location_name] = (lat, lon)
                    return lat, lon
                else:
                    logger.warning(f"[GeoCoder] Nominatim could not find '{location_name}'")
                    self.cache[location_name] = (None, None)
                    return None, None
            except GeocoderTimedOut:
                logger.warning(f"[GeoCoder] Timed out on attempt {attempt+1} for '{location_name}', retrying...")
                time.sleep(2 ** attempt)
            except GeocoderServiceError as e:
                logger.error(f"[GeoCoder] Nominatim service error for '{location_name}': {e}")
                self.cache[location_name] = (None, None)
                return None, None
            except Exception as e:
                logger.error(f"[GeoCoder] Unexpected error geocoding '{location_name}': {e}")
                self.cache[location_name] = (None, None)
                return None, None

        logger.error(f"[GeoCoder] Max retries exceeded for '{location_name}'")
        self.cache[location_name] = (None, None)
        return None, None

    def lookup_coordinates(self, location_name, threshold=70):
        """
        Local fuzzy match using 'rapidfuzz' to find the best match in self.locations.
        Return (lat, lon) if found, or (None, None) if no match.
        """
        normalized_input = normalize_text(location_name)
        if not normalized_input:
            return None, None

        # 1) Single best fuzzy match on entire string
        match = process.extractOne(
            normalized_input,
            list(self.locations.keys()),
            scorer=fuzz.token_set_ratio
        )
        if match:
            best_match, score, _ = match
            if score >= threshold:
                # note: self.locations[best_match] is [lon, lat], so flip to lat, lon
                lon, lat = self.locations[best_match]
                logger.debug(f"[GeoCoder] Fuzzy matched '{normalized_input}' -> '{best_match}' (score={score})")
                return (lat, lon)

        # 2) Split input by commas and attempt partial matches
        parts = [p.strip() for p in normalized_input.split(',')]
        for part in parts:
            if not part:
                continue
            match = process.extractOne(part, list(self.locations.keys()), scorer=fuzz.token_set_ratio)
            if match:
                best_match, score, _ = match
                if score >= threshold:
                    lon, lat = self.locations[best_match]
                    logger.debug(f"[GeoCoder] Partial match '{part}' -> '{best_match}' (score={score})")
                    return (lat, lon)

        # 3) Attempt substring-based matching within each part
        for part in parts:
            tokens = part.split()
            # from largest substring to smaller
            for length in range(len(tokens), 0, -1):
                for start_idx in range(len(tokens) - length + 1):
                    substring = ' '.join(tokens[start_idx:start_idx + length])
                    match = process.extractOne(substring, list(self.locations.keys()), scorer=fuzz.token_set_ratio)
                    if match:
                        best_match, score, _ = match
                        if score >= threshold:
                            lon, lat = self.locations[best_match]
                            logger.debug(f"[GeoCoder] Substring '{substring}' -> '{best_match}' (score={score})")
                            return (lat, lon)

        logger.debug(f"[GeoCoder] No local match for '{location_name}'")
        return None, None

if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)

    geocoder = GeoCoder(filepath=DEFAULT_FILEPATH)

    test_locations = [
        "бул. Трета македонска бригада, Скопје",
        "село Баница",
        "с.Врапчиште",
        "бул. Илинден, Битола",
        "Непостоечко Место",
        "ул.„Македонска косовска бригада“, Скопје",
        "Комплексот клиники „Мајка Тереза“, Скопје",
        "СВР Скопје"
    ]

    for loc in test_locations:
        lat, lon = geocoder.geocode_location(loc)
        print(f"'{loc}' -> lat={lat}, lon={lon}")
