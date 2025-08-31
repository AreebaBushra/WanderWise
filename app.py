import streamlit as st
import requests
import os

# Set page config
st.set_page_config(page_title="WanderWise", page_icon="🌍", layout="wide")

st.title("🌍 WanderWise – AI Travel Assistant")

# Ask user for destination
destination = st.text_input("Enter a city or country you want to explore:")

if st.button("Plan My Trip") and destination:
    st.write(f"✨ Generating travel plan for **{destination}**...")

    # --- Call Azure OpenAI (dummy example for now) ---
    travel_plan = f"""
    🏙️ Destination: {destination}
    ✈️ Best time to visit: Spring & Autumn
    🍲 Famous food: Local specialties
    📍 Top attractions: Example Park, Example Museum, Example Street
    """

    st.success(travel_plan)

    # --- Show map (using Streamlit’s map feature) ---
    st.subheader("🗺️ Map Location")
    try:
        url = f"https://nominatim.openstreetmap.org/search?city={destination}&format=json"
        response = requests.get(url).json()
        if response:
            lat, lon = float(response[0]["lat"]), float(response[0]["lon"])
            st.map({"lat": [lat], "lon": [lon]})
        else:
            st.warning("Could not fetch map for this location.")
    except:
        st.warning("Error loading map.")
