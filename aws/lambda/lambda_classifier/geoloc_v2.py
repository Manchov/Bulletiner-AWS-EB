#geoloc_v2.py
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
        return geojson.load(file)

def normalize_text(text):
    if not text:
        return ''
    text = text.lower().strip()
    # Expand abbreviations
    abbreviation_mapping = {
        r'\bул\b\.?': 'улица ',
        r'\bбул\b\.?': 'булевар ',
        r'\bс\b\.?': 'село ',
        r'\bгр\b\.?': 'град ',
        r'\bмн\b\.?': 'маало ',
        r'\bпл\b\.?': 'плоштад '
    }
    for pattern, repl in abbreviation_mapping.items():
        text = re.sub(pattern, repl, text)

    # Remove punctuation except commas
    punctuation_except_commas = string.punctuation.replace(',', '')
    text = text.translate(str.maketrans('', '', punctuation_except_commas))
    text = re.sub(r'\s+', ' ', text).strip()
    return text

class TwoFileGeoCoder:
    """
    Loads 2 separate geojson files:
      - places.geojson -> dictionary of cities/towns/villages
      - amenities.geojson -> dictionary of schools/hospitals/police, etc.
    Each dictionary can store (normalized_name -> (lat, lon, city)).
    Then we do city-based matching, or fallback to fuzzy matching, etc.
    """
    def __init__(self, places_path="location.geojson", amenities_path="location_2.geojson"):
        self.places_data = load_geojson(places_path)
        self.amenities_data = load_geojson(amenities_path)

        # Build dictionaries
        self.places_dict = self._build_places_dict()
        self.amenities_dict = self._build_amenities_dict()

        self.geolocator = Nominatim(user_agent="twofile_geocoder")
        self.cache = {}

    def _build_places_dict(self):
        """
        Return dict: normalized_place_name -> { 'lat': float, 'lon': float }
        Or we can store geometry coords as well.
        """
        d = {}
        for feature in self.places_data.get("features", []):
            props = feature.get("properties", {})
            geom = feature.get("geometry", {})
            coords = geom.get("coordinates")
            if not coords or len(coords) < 2:
                continue

            # Typically coords = [lon, lat]
            name = normalize_text(props.get("name", ""))
            if not name:
                continue

            lat = coords[1]
            lon = coords[0]
            d[name] = { "lat": lat, "lon": lon }
        return d

    def _build_amenities_dict(self):
        """
        Return dict: normalized_amenity_name -> list of { 'lat': float, 'lon': float, 'city': ???, 'raw_name': ???}
        Because multiple amenities can share the same name in different cities.
        """
        d = {}
        for feature in self.amenities_data.get("features", []):
            props = feature.get("properties", {})
            geom = feature.get("geometry", {})
            coords = geom.get("coordinates")
            if not coords or len(coords) < 2:
                continue

            lat = coords[1]
            lon = coords[0]
            raw_name = props.get("name", "")
            name_norm = normalize_text(raw_name)

            # If your amenities have a property like "addr:city" or "city" you can store it.
            city_prop = props.get("addr:city", "") or props.get("city", "")
            city_norm = normalize_text(city_prop)

            # Collect in a list, because multiple items can share the same normalized name
            if name_norm not in d:
                d[name_norm] = []
            d[name_norm].append({
                "lat": lat,
                "lon": lon,
                "city": city_norm,
                "raw_name": raw_name
            })
        return d

    def geocode_location(self, location_str, retries=3):
        """
        We parse the location_str to see if there's a city mention,
        match that city from places_dict, then try to match the rest in amenities_dict.
        If all fails, fallback to Nominatim.
        """
        if not location_str:
            return None, None

        # Cache check
        if location_str in self.cache:
            return self.cache[location_str]

        # Try local approach
        lat, lon = self._lookup_local(location_str)
        if lat is not None and lon is not None:
            self.cache[location_str] = (lat, lon)
            return (lat, lon)

        # Fallback to Nominatim
        for attempt in range(retries):
            try:
                query = f"{location_str}, Северна Македонија"
                location = self.geolocator.geocode(query)
                if location:
                    lat, lon = location.latitude, location.longitude
                    self.cache[location_str] = (lat, lon)
                    return (lat, lon)
            except GeocoderTimedOut:
                logger.warning(f"Nominatim timed out, attempt {attempt+1} for '{location_str}'")
                time.sleep(2 ** attempt)
            except GeocoderServiceError as e:
                logger.error(f"Nominatim service error: {e}")
                self.cache[location_str] = (None, None)
                return (None, None)
            except Exception as e:
                logger.error(f"Unexpected error with Nominatim: {e}")
                self.cache[location_str] = (None, None)
                return (None, None)

        # If still not found
        self.cache[location_str] = (None, None)
        return (None, None)

    def _lookup_local(self, location_str):
        """
        Attempt city-based approach:
          1) parse out city from location_str if there's a comma
          2) match city in places_dict
          3) if found, try to match the rest in amenities_dict but only items that have that city
             or if city not found, we do a fallback approach
        """
        normalized = normalize_text(location_str)
        parts = [p.strip() for p in normalized.split(',')]

        # If multiple parts, the last part might be city
        city_candidate = None
        if len(parts) > 1:
            city_candidate = parts[-1]  # e.g. "скопје" or "прилеп"
            # Attempt city fuzzy match
            city_latlon = self._fuzzy_match_city(city_candidate, threshold=75)
            if city_latlon:
                # We have a recognized city. Now let's match the rest (everything except last part) as an amenity
                rest = ', '.join(parts[:-1]).strip()
                if rest:
                    lat, lon = self._match_amenity_in_city(rest, city_candidate)
                    if lat is not None and lon is not None:
                        return lat, lon
                # If we found city but can't match amenity, fallback to city coords
                return city_latlon["lat"], city_latlon["lon"]

        # else or fallback: single-part or city not found. Attempt direct city match or direct amenity match
        # 1) direct city match
        city_latlon = self._fuzzy_match_city(normalized)
        if city_latlon:
            return city_latlon["lat"], city_latlon["lon"]

        # 2) direct amenity match
        lat, lon = self._fuzzy_match_amenity_any_city(normalized)
        if lat is not None and lon is not None:
            return lat, lon

        return (None, None)

    def _fuzzy_match_city(self, city_name, threshold=70):
        """
        Attempt fuzzy match city_name in self.places_dict. Return { lat, lon } if found.
        """
        if not city_name:
            return None
        best = process.extractOne(city_name, list(self.places_dict.keys()), scorer=fuzz.token_set_ratio)
        if best:
            match_key, score, _ = best
            if score >= threshold:
                return self.places_dict[match_key]
        return None

    def _match_amenity_in_city(self, amenity_str, city_str, threshold=70):
        """
        Fuzzy match amenity_str among those that have city=city_str in self.amenities_dict entries.
        We'll do:
          1) fuzzy match city_str to known city keys
          2) filter the amenities that have city=that city (norm)
          3) do fuzzy match on amenity_str in that subset
        """
        city_normalized = normalize_text(city_str)
        # We fuzzy matched city earlier, but let's see if we do direct exact match or partial match
        # for the amenity's 'city' field.

        # We'll try the amenity dictionary. The dictionary keys are normalized names of the amenity.
        # but each amenity has a city field we can filter on.

        # step 1) collect all items that have city=city_normalized (or close enough)
        # a robust approach might do a fuzzy match on city in each amenity's city field,
        # but let's keep it simpler: direct or partial
        # We'll do direct check if amenity_item["city"] == city_normalized
        # or if there's a mismatch in spacing, you can do fuzzy match city separately.
        matched_candidates = []
        for amen_key, amen_list in self.amenities_dict.items():
            # amen_key is normalized amenity name, amen_list is a list of dict
            for item in amen_list:
                if item["city"] == city_normalized:
                    matched_candidates.append((amen_key, item))

        # now do fuzzy match amenity_str with matched_candidates' keys
        if not matched_candidates:
            return (None, None)

        # We can build a unique set of amen_keys
        unique_keys = list({x[0] for x in matched_candidates})

        best = process.extractOne(amenity_str, unique_keys, scorer=fuzz.token_set_ratio)
        if best:
            match_key, score, _ = best
            if score >= threshold:
                # We have an amen_key that matched
                # but there might be multiple items with that key
                # pick the first or the best? We'll pick the first for simplicity
                for candidate_key, item in matched_candidates:
                    if candidate_key == match_key:
                        return item["lat"], item["lon"]
        return (None, None)

    def _fuzzy_match_amenity_any_city(self, amenity_str, threshold=70):
        """
        Fuzzy match amenity_str among all amenities in self.amenities_dict, ignoring city.
        """
        if not amenity_str:
            return (None, None)

        # gather all unique amen_keys
        all_amen_keys = list(self.amenities_dict.keys())

        best = process.extractOne(amenity_str, all_amen_keys, scorer=fuzz.token_set_ratio)
        if best:
            match_key, score, _ = best
            if score >= threshold:
                # pick the first item in the amen_list (or refine further)
                item = self.amenities_dict[match_key][0]
                return item["lat"], item["lon"]
        return (None, None)

if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    geocoder = TwoFileGeoCoder("location.geojson", "location_2.geojson")

    test_strings = [
        "ООУ Гоце Делчев, Скопје",
        "ООУ Гоце Делчев, Прилеп",
        "Полициска станица Бит Пазар, Скопје",
        "Село Грчец, Скопје",
        "Полициска станица Охрид",
        "Непостоечко Место",
        "ул. „Довлеџик”, Битола"
    ]

    for txt in test_strings:
        lat, lon = geocoder.geocode_location(txt)
        print(f"'{txt}' => lat={lat}, lon={lon}")
