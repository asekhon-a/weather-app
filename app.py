from flask import Flask, render_template, request
import requests
import os
from dotenv import load_dotenv # New Import

# Load environment variables from .env file
load_dotenv() 

# Configuration
app = Flask(__name__)
# 🔑 Get API Key securely from environment variables
API_KEY = os.environ.get("OPENWEATHER_API_KEY") 
BASE_URL = "http://api.openweathermap.org/data/2.5/weather"

# Function to fetch weather data
def get_weather_data(city):
    if not API_KEY:
        print("Error: OPENWEATHER_API_KEY not found in .env file.")
        return None

    params = {
        'q': city,
        'appid': API_KEY,
        'units': 'metric' # Displays temperature in Celsius
    }
    
    try:
        response = requests.get(BASE_URL, params=params)
        response.raise_for_status() # Raises an HTTPError for bad responses (4xx or 5xx)
        return response.json()
    except requests.exceptions.HTTPError as e:
        print(f"HTTP Error for city {city}: {e}")
        return None
    except requests.exceptions.RequestException as e:
        print(f"Error fetching weather data: {e}")
        return None

# Main route for the application
@app.route('/', methods=['GET', 'POST'])
def index():
    weather_data = None
    error_message = None

    if request.method == 'POST':
        city = request.form.get('city')
        
        if city:
            data = get_weather_data(city)
            
            if data:
                # Process and structure the data for the template (with new fields)
                weather_data = {
                    'city': data.get('name'),
                    'country': data['sys']['country'],
                    'temperature': int(data['main']['temp']),
                    'description': data['weather'][0]['description'].title(),
                    'icon': data['weather'][0]['icon'],
                    # New Data Fields
                    'temp_min': int(data['main']['temp_min']),
                    'temp_max': int(data['main']['temp_max']),
                    'humidity': data['main']['humidity'],
                    # Convert wind speed from m/s to km/h (multiply by 3.6) and round to 1 decimal
                    'wind_speed': round(data['wind']['speed'] * 3.6, 1) 
                }
            else:
                error_message = f"Weather for '{city}' not found or API error. Please check the spelling."

    # Render the HTML template, passing the data to the frontend
    return render_template('index.html', weather=weather_data, error=error_message)

if __name__ == '__main__':
    # Add an error check for the API key at startup
    if not os.environ.get("OPENWEATHER_API_KEY"):
         print("FATAL ERROR: Please create a .env file and set OPENWEATHER_API_KEY.")
    else:
        app.run(debug=True)