from datetime import datetime, timedelta
from retry_requests import retry
import requests
import openmeteo_requests
import requests
import requests_cache
import pandas as pd
import streamlit as st
from geopy.geocoders import Nominatim
import plotly.express as px

cache_session = requests_cache.CachedSession('.cache', expire_after=3600)
retry_session = retry(cache_session, retries=5, backoff_factor=0.2)
openmeteo = openmeteo_requests.Client(session=retry_session)

st.title("Weather Forecast Dashboard")

st.sidebar.header("Query For Location")
city = st.sidebar.text_input("Enter City Name (Leave blank to use Latitude/Longitude)")
st.sidebar.divider()
latitude = st.sidebar.number_input("Enter Latitude")
longitude = st.sidebar.number_input("Enter Longitude")

location = None
def get_coordinates(city):
    url = f"https://nominatim.openstreetmap.org/search?q={city}&format=json"
    response = requests.get(url, headers={"User-Agent": "your-app-name"})
    data = response.json()
    if data:
        latitude = float(data[0]['lat'])
        longitude = float(data[0]['lon'])
        return latitude, longitude
    return None



if city:
    try:
        coordinates = get_coordinates(city)
        if coordinates:
            latitude, longitude = coordinates
            st.write(f"City '{city}' found: {latitude}°N, {longitude}°E")
        else:
                st.write(f"City '{city}' not found. Using latitude and longitude inputs.")
    except Exception:
        st.write("Geocoding timed out. Using latitude and longitude inputs.")
else:
    st.write("No city provided. Using latitude and longitude inputs.")



st.sidebar.divider()
st.sidebar.header("Query For Weather")
past_days = st.sidebar.number_input("Number of past days",value=1)
past_days = past_days if past_days < 90 else 90
forcast_days = st.sidebar.number_input("Number of forcast days",value=16)
forcast_days = forcast_days if forcast_days < 17 else 16

params = {
    "latitude": latitude,
    "longitude": longitude,
    "daily": ["weather_code", "precipitation_sum", "rain_sum", "snowfall_sum", "wind_speed_10m_max"],
    "past_days": past_days,
    "forecast_days": forcast_days
}

responses = openmeteo.weather_api("https://api.open-meteo.com/v1/forecast", params=params)

response = responses[0]
st.write(f"Coordinates: {response.Latitude()}°N, {response.Longitude()}°E")


daily = response.Daily()
daily_weather_code = daily.Variables(0).ValuesAsNumpy()
daily_precipitation_sum = daily.Variables(1).ValuesAsNumpy()
daily_rain_sum = daily.Variables(2).ValuesAsNumpy()
daily_snowfall_sum = daily.Variables(3).ValuesAsNumpy()
daily_wind_speed_10m_max = daily.Variables(4).ValuesAsNumpy()

daily_data = {
    "date": pd.date_range(
        start=pd.to_datetime(daily.Time(), unit="s", utc=True),
        end=pd.to_datetime(daily.TimeEnd(), unit="s", utc=True),
        freq=pd.Timedelta(seconds=daily.Interval()),
        inclusive="left"
    ),
    "precipitation_sum": daily_precipitation_sum,
    "rain_sum": daily_rain_sum,
    "snowfall_sum": daily_snowfall_sum,
    "wind_speed_10m_max": daily_wind_speed_10m_max,
    "daily_weather_code":daily_weather_code
}

daily_dataframe = pd.DataFrame(data=daily_data)

st.write("### Daily Weather Data")
st.dataframe(daily_dataframe)

st.write("### Weather Variables Over Time")
st.line_chart(daily_dataframe.set_index("date"))






st.sidebar.divider()
st.title('Earthquake Data')

st.sidebar.header("Query For Earthquakes")
start_time = st.sidebar.date_input('Start Date', datetime(2024, 10, 1))
end_time = st.sidebar.date_input('End Date', datetime(2024, 10, 20))
min_magnitude = st.sidebar.slider('Minimum Magnitude', 1.0, 10.0, 3.0)
max_radius = st.sidebar.number_input('Max Radius (km)', value=200)

url = f"https://earthquake.usgs.gov/fdsnws/event/1/query?format=geojson&starttime={start_time}&endtime={end_time}&minmagnitude={min_magnitude}&latitude={latitude}&longitude={longitude}&maxradiuskm={max_radius}"


def fetch_earthquake_data(url):
    try:
        response = requests.get(url)
        data = response.json()
        return data
    except Exception as e:
        st.error(f"Error fetching data: {e}")
        return None


data = fetch_earthquake_data(url)
print(data)

if data is not None and data['metadata']['count']>0 :
    earthquakes = data['features']

    df = pd.DataFrame([{
        'Place': quake['properties']['place'],
        'Magnitude': quake['properties']['mag'],
        'Time': pd.to_datetime(quake['properties']['time'], unit='ms'),
        'Longitude': quake['geometry']['coordinates'][0],
        'Latitude': quake['geometry']['coordinates'][1],
        'Depth': quake['geometry']['coordinates'][2]
    } for quake in earthquakes])

    st.write(f"Total Earthquakes: {len(df)}")

    st.dataframe(df)

    st.subheader('Map of Earthquakes')
    fig = px.scatter_mapbox(df, lat='Latitude', lon='Longitude', color='Magnitude',
                            hover_name='Place', size='Magnitude',
                            size_max=15, zoom=5, mapbox_style="carto-positron")
    st.plotly_chart(fig)

else:
    st.info("No data found for the selected parameters.")

st.sidebar.divider()
st.title('ACLED Conflict Data')

st.sidebar.header("Query For Conflicts")


event_date = st.sidebar.date_input('Event Date', datetime(2024, 10, 10))

days_before = st.sidebar.number_input('Number of past days', 2)

days = [event_date - timedelta(days=i) for i in range(0, days_before)]


api_key = "KfSN1O6bRG9u9tFd*PFW"
email = "sami.jaadar@etu.uae.ac.ma"
base_url = "https://api.acleddata.com/acled/read"


def get_country(latitude, longitude):
    url = f"https://nominatim.openstreetmap.org/reverse?lat={latitude}&lon={longitude}&format=jsonv2&accept-language=en"
    response = requests.get(url, headers={"User-Agent": "your-app-name"})
    data = response.json()
    if 'address' in data and 'country' in data['address']:
        return data['address']['country']
    return None

country = get_country(latitude,longitude)

if country:

    def fetch_acled_data_for_date(date, country):
        url = f"{base_url}?key={api_key}&email={email}&event_date={date}&country={country}"
        try:
            response = requests.get(url)
            data = response.json()
            if data and 'data' in data:
                return data['data']
            return []
        except Exception as e:
            st.error(f"Error fetching data for {date}: {e}")
            return []


    all_data = []
    for day in days:
        day_data = fetch_acled_data_for_date(day.strftime('%Y-%m-%d'), country)
        all_data.extend(day_data)

    if len(all_data) > 0:
        df = pd.DataFrame(all_data)
        df = df[['event_date', 'event_type', 'sub_event_type', 'location', 'latitude', 'longitude', 'fatalities']]

        df['event_date'] = pd.to_datetime(df['event_date'])

        st.subheader(f'Conflict Data for {country} for Last {days_before} Days Before {event_date})')
        st.write(f"Total Events: {len(df)}")

        st.dataframe(df)

    else:
        st.info(f"No conflict data found for {country} .")
