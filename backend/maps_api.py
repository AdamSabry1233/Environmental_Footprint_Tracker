import googlemaps
import datetime
import requests
from backend.dependencies import GOOGLE_MAPS_API_KEY

class MapsAPI:
    def __init__(self):
        """
        Initialize Google Maps API Client.
        """
        self.api_key = GOOGLE_MAPS_API_KEY
        self.geocode_url = "https://maps.googleapis.com/maps/api/geocode/json"
        self.routes_url = "https://routes.googleapis.com/directions/v2:computeRoutes"

    def get_coordinates_from_address(self, address: str):
        """
        Converts an address into latitude and longitude using the Geocoding API.
        
        :param address: The address to be geocoded
        :return: Dictionary with latitude and longitude
        """
        try:
            params = {
                "address": address,
                "key": self.api_key
            }

            response = requests.get(self.geocode_url, params=params)
            response_data = response.json()

            if response_data["status"] == "OK":
                location = response_data["results"][0]["geometry"]["location"]
                return {"lat": location["lat"], "lng": location["lng"]}
            else:
                return None  # No coordinates found

        except Exception as e:
            print(f"Error geocoding address: {e}")
            return None

    def get_route_details(self, origin: str, destination: str, mode="driving"):
        """
        Fetches route details (distance, duration) using Google Maps Routes API.
        """
        try:
            # Convert origin and destination to coordinates
            origin_coords = self.get_coordinates_from_address(origin)
            destination_coords = self.get_coordinates_from_address(destination)

            if not origin_coords or not destination_coords:
                print("[ERROR] Could not convert addresses to coordinates.")
                return None, None  

            # Fix: Convert FastAPI mode names to Google Maps API format
            mode_mapping = {
                "driving": "DRIVE",
                "bicycling": "BICYCLE",
                "walking": "WALK",
                "transit": "TRANSIT"
            }
            google_mode = mode_mapping.get(mode.lower(), "DRIVE")  # Default to DRIVE if invalid mode

            headers = {
                "Content-Type": "application/json",
                "X-Goog-Api-Key": self.api_key,
                "X-Goog-FieldMask": "routes.distanceMeters,routes.duration"
            }

            payload = {
                "origin": {"location": {"latLng": {"latitude": origin_coords["lat"], "longitude": origin_coords["lng"]}}},
                "destination": {"location": {"latLng": {"latitude": destination_coords["lat"], "longitude": destination_coords["lng"]}}},
                "travelMode": google_mode,  # ✅ FIX: Use mapped mode
                "routingPreference": "TRAFFIC_AWARE_OPTIMAL"
            }

            print("[INFO] Route Details Request Payload:", payload)

            response = requests.post(self.routes_url, json=payload, headers=headers)
            response_data = response.json()
            print("[INFO] Route Details API Response:", response_data)

            if "routes" not in response_data or not response_data["routes"]:
                print("[ERROR] No routes found in API response.")
                return None, None

            # Extract the first route
            route = response_data["routes"][0]
            distance_miles = route["distanceMeters"] / 1609.34  # Convert meters to miles
            duration_seconds = int(route["duration"].replace("s", "")) if "s" in route["duration"] else int(route["duration"])
            duration_minutes = duration_seconds / 60  # Convert seconds to minutes

            return distance_miles, duration_minutes

        except Exception as e:
            print(f"[ERROR] Exception in get_route_details: {e}")
            return None, None




    def get_eco_friendly_routes(self, origin: str, destination: str):
        try:
            # Convert origin and destination to coordinates
            origin_coords = self.get_coordinates_from_address(origin)
            destination_coords = self.get_coordinates_from_address(destination)

            if not origin_coords or not destination_coords:
                print("Error: Could not get coordinates for origin or destination.")
                return None  # Coordinates not found

            headers = {
                "Content-Type": "application/json",
                "X-Goog-Api-Key": self.api_key,
                "X-Goog-FieldMask": "routes.distanceMeters,routes.duration"  # Required FieldMask
            }

            payload = {
                "origin": {"location": {"latLng": {"latitude": origin_coords["lat"], "longitude": origin_coords["lng"]}}},
                "destination": {"location": {"latLng": {"latitude": destination_coords["lat"], "longitude": destination_coords["lng"]}}},
                "travelMode": "DRIVE",
                "routingPreference": "TRAFFIC_AWARE_OPTIMAL",
                "computeAlternativeRoutes": True  # Request alternative eco-friendly routes
}


            print("Eco Routes Request Payload (Fixed):", payload)

            response = requests.post(self.routes_url, json=payload, headers=headers)
            response_data = response.json()
            print("Eco Routes API Response:", response_data)  # Debugging line

            # Check if 'routes' exist and are non-empty
            if "routes" not in response_data or not response_data["routes"]:
                print("Error: No routes found in API response.")
                return None

            # Extract the first valid route
            route = response_data["routes"][0]

            # Ensure 'distanceMeters' and 'duration' exist
            if "distanceMeters" not in route or "duration" not in route:
                print("Error: Missing distance or duration in API response.")
                return None

            distance_miles = route["distanceMeters"] / 1609.34  # Convert meters to miles

            # Convert duration from string to integer (handle cases where 's' is missing)
            duration_str = route["duration"]
            duration_seconds = int(duration_str.replace("s", "")) if "s" in duration_str else int(duration_str)
            duration_minutes = duration_seconds / 60  # Convert seconds to minutes

            return [{
                "distance_miles": round(distance_miles, 2),
                "duration_minutes": round(duration_minutes, 2),
                "summary": "Optimal Route"
            }]

        except Exception as e:
            print(f"Error fetching eco-friendly routes: {e}")
            return None

