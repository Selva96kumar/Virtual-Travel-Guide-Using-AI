from flask import Flask, render_template, request
import requests

app = Flask(__name__)

OPENTRIPMAP_API_KEY = '5ae2e3f221c38a28845f05b601191ac37466b8b8dcdf793862d695d1'

def get_travel_info(destination, days):
    search_query = destination
    geo_response = requests.get(f"https://api.opentripmap.com/0.1/en/places/geoname?name={search_query}&apikey={OPENTRIPMAP_API_KEY}")
    geo_data = geo_response.json()

    lat = geo_data.get('lat')
    lon = geo_data.get('lon')

    places = []

    if lat and lon:
        places_response = requests.get(
            f"https://api.opentripmap.com/0.1/en/places/radius?radius=5000&lon={lon}&lat={lat}&limit=100&apikey={OPENTRIPMAP_API_KEY}"
        )
        places_data = places_response.json()
        places_raw = places_data.get('features', [])

        # Debug print statement
        print("Places Data:", places_raw)

        # Filter out places with missing 'properties' or 'name'
        places = [
            {
                'name': place.get('properties', {}).get('name', 'No Name Available'),
                'lat': place.get('geometry', {}).get('coordinates', [])[1],
                'lon': place.get('geometry', {}).get('coordinates', [])[0]
            }
            for place in places_raw
            if place.get('properties', {}).get('name')
        ]
    
    daily_itinerary = []
    places_per_day = len(places) // days if days else 0

    for i in range(days):
        day_plan = places[i*places_per_day:(i+1)*places_per_day]
        daily_itinerary.append(day_plan)

    return daily_itinerary

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        destination = request.form.get('destination')
        days = int(request.form.get('days'))
        style = request.form.get('style')
        daily_itinerary = get_travel_info(destination, days)
        return render_template('results.html', daily_itinerary=daily_itinerary, destination=destination, style=style, days=days)
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)
