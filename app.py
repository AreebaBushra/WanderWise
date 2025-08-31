import os, json, requests, streamlit as st
from dotenv import load_dotenv
from openai import AzureOpenAI
import folium

# ---------- Load keys from environment ----------
load_dotenv()
MAPS_KEY = os.getenv("AZURE_MAPS_KEY")
AOAI_ENDPOINT = os.getenv("AZURE_OPENAI_ENDPOINT")
AOAI_KEY = os.getenv("AZURE_OPENAI_API_KEY")
AOAI_DEPLOYMENT = os.getenv("AZURE_OPENAI_DEPLOYMENT")
AOAI_API_VERSION = os.getenv("AZURE_OPENAI_API_VERSION", "2025-05-01-preview")

client = AzureOpenAI(
    api_key=AOAI_KEY,
    api_version=AOAI_API_VERSION,
    azure_endpoint=AOAI_ENDPOINT,
)

# ---------- Functions ----------
def geocode_city(city: str):
    url = "https://atlas.microsoft.com/search/fuzzy/json"
    params = {"api-version": "1.0", "query": city, "limit": 1, "subscription-key": MAPS_KEY}
    r = requests.get(url, params=params, timeout=20)
    r.raise_for_status()
    results = r.json().get("results", [])
    if not results: return None
    pos = results[0]["position"]
    return float(pos["lat"]), float(pos["lon"])

def get_pois(lat, lon, category="museum", radius=5000, limit=5):
    url = "https://atlas.microsoft.com/search/poi/category/json"
    params = {
        "api-version": "1.0",
        "query": category,
        "lat": lat, "lon": lon,
        "radius": radius, "limit": limit,
        "subscription-key": MAPS_KEY
    }
    r = requests.get(url, params=params, timeout=20)
    r.raise_for_status()
    return r.json().get("results", [])

def llm_plan(city, pois):
    names = [p.get("poi", {}).get("name", "Unknown") for p in pois]
    prompt = f"Create a 1-day itinerary in {city} visiting these places: {', '.join(names)}."
    resp = client.chat.completions.create(
        model=AOAI_DEPLOYMENT,
        messages=[{"role": "user", "content": prompt}],
        temperature=0.5,
    )
    return resp.choices[0].message.content

def render_map(lat, lon, pois):
    m = folium.Map(location=[lat, lon], zoom_start=13)
    for p in pois:
        folium.Marker(
            [p["position"]["lat"], p["position"]["lon"]],
            popup=p.get("poi", {}).get("name", "POI"),
        ).add_to(m)
    return m._repr_html_()

# ---------- Streamlit UI ----------
st.set_page_config(page_title="WanderWise", page_icon="🌍", layout="wide")
st.title("🌍 WanderWise – Smart Travel Itinerary")

city = st.text_input("Enter a city:", value="Paris")

if st.button("Plan my trip"):
    with st.spinner("Fetching itinerary..."):
        coords = geocode_city(city)
        if not coords:
            st.error("City not found.")
            st.stop()

        lat, lon = coords
        pois = get_pois(lat, lon, "landmark", radius=5000, limit=5)
        plan = llm_plan(city, pois)

        st.subheader("Your Itinerary")
        st.write(plan)

        st.subheader("Map")
        st.components.v1.html(render_map(lat, lon, pois), height=500)
