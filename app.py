import streamlit as st
import base64
import os
import pandas as pd
from datetime import datetime
from textblob import TextBlob
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import random

# ---------------- PAGE CONFIG ----------------
st.set_page_config(page_title="AI Diary - Mood Analyzer", page_icon="📝", layout="wide")

# ---------------- LOAD LOCAL BACKGROUND IMAGE ----------------
def get_base64_of_file(file_path):
    if not os.path.exists(file_path):
        st.error(f"Background image '{file_path}' not found! Place it in the same folder as this script.")
        return ""
    with open(file_path, "rb") as f:
        return base64.b64encode(f.read()).decode()

bg_path = "diary_bg.jpg"  # your local background image
bg_image = get_base64_of_file(bg_path)

# ---------------- CUSTOM CSS ----------------
st.markdown(f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Dancing+Script&display=swap');

    [data-testid="stAppViewContainer"] {{
        background-image: url("data:image/png;base64,{bg_image}");
        background-size: cover;
        background-attachment: fixed;
        background-repeat: no-repeat;
        background-position: center;
    }}

    [data-testid="stSidebar"] {{
        background-color: rgba(255, 248, 230, 0.95);
        color: #4e342e !important;
        font-family: 'Comic Sans MS', cursive;
    }}

    * {{
        font-family: "Comic Sans MS", "Segoe Print", cursive !important;
        color: #3e2723 !important;
    }}

    .main-title {{
        font-family: 'Dancing Script', cursive !important;
        text-align: center;
        color: #4e342e !important;
        font-size: 3rem;
        font-weight: bold;
        text-shadow: 1px 1px 3px #f5f5dc;
    }}

    div.stButton > button:first-child {{
        width: 200px;
        height: 50px;
        font-size: 18px;
        border-radius: 12px;
        background-color: #d7a86e; 
        color: white;
        font-weight: bold;
        box-shadow: 2px 2px 6px #b58b00;
        display: block;
        margin: 15px auto;
    }}
    div.stButton > button:first-child:hover {{
        background-color: #c48a3a;
        transform: scale(1.05);
    }}

    .quote {{
        font-style: italic;
        color: #6d4c41;
        margin-bottom: 15px;
        font-size: 0.95rem;
    }}

    /* Handwritten style for text area */
    div[data-baseweb="textarea"] textarea {{
        font-family: 'Dancing Script', cursive !important;
        font-size: 1.3rem !important;
        color: #3e2723 !important;
        border-radius: 15px !important;
        border: 2px solid #d7ccc8 !important;
        padding: 15px !important;
    }}
    </style>
""", unsafe_allow_html=True)

# Optional subtle floating paper effect
st.markdown("""
<style>
[data-testid="stAppViewContainer"]::after {
    content: "";
    position: fixed;
    top: 0; left: 0;
    width: 100%; height: 100%;
    background: url('"C:/Users/ASUS/OneDrive/Documents/AI_journal/diary_bg.jpg"');
    opacity: 0.05;
    pointer-events: none;
    z-index: 0;
}
</style>
""", unsafe_allow_html=True)

# ---------------- HEADER ----------------
st.markdown("<h1 class='main-title'>📝 AI Diary</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align:center;'>Reflect on your day and enjoy Spotify vibes 🎶</p>", unsafe_allow_html=True)

# ---------------- SIDEBAR ----------------
st.sidebar.header("Daily Journal Quotes")
quotes = [
    "“The best way to capture moments is to write them down.”",
    "“Journaling is like whispering to oneself and listening at the same time.”",
    "“Your mood is your message; reflect and grow.”",
    "“Write what should not be forgotten.”",
    "“Every day is a blank page in the diary of your life.”"
]
for q in quotes:
    st.sidebar.markdown(f"<p class='quote'>💭 {q}</p>", unsafe_allow_html=True)

# ---------------- SPOTIFY SETUP ----------------
CLIENT_ID = "a6e8eb6110e64e3187e8e43b667f386f"        # Put your Client ID here
CLIENT_SECRET = "6ae20d21a0f244b7933b0b40222c172f"  # Put your Client Secret here

sp = spotipy.Spotify(auth_manager=SpotifyClientCredentials(
    client_id=CLIENT_ID,
    client_secret=CLIENT_SECRET
))

# ---------------- MOOD ANALYZER ----------------
def analyze_mood(entry):
    blob = TextBlob(entry)
    polarity = blob.sentiment.polarity

    text = entry.lower()
    positive_words = ["yay","happy","awesome","great","amazing","good","love","super","excited","won","marks","passed","success","awe","awwe","wow"]
    negative_words = ["sad","angry","bad","hate","upset","fail","failed","tired","bored","disappointed","worst","cry","crying"]

    for word in positive_words:
        if word in text:
            polarity += 0.3
    for word in negative_words:
        if word in text:
            polarity -= 0.3

    polarity = max(-1, min(1, polarity))

    if polarity > 0.2:
        return "😊 Positive"
    elif polarity < -0.2:
        return "😞 Negative"
    else:
        return "😐 Neutral"

# ---------------- MOOD COLOR ----------------
def get_mood_color(mood):
    if mood == "😊 Positive":
        return "rgba(198, 239, 206, 0.8)"  # light green
    elif mood == "😞 Negative":
        return "rgba(255, 199, 206, 0.8)"  # light red
    else:
        return "rgba(255, 235, 156, 0.8)"  # light yellow

# ---------------- SAVE ENTRY ----------------
def save_entry(entry, mood, filename="journal.csv"):
    date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    new_entry = pd.DataFrame([[date, entry, mood]], columns=["Date","Entry","Mood"])
    if os.path.exists(filename):
        new_entry.to_csv(filename, mode="a", header=False, index=False)
    else:
        new_entry.to_csv(filename, index=False)

# ---------------- KEYWORD → PLAYLIST MAP ----------------
keyword_map = {
    "happy": "happy upbeat",
    "excited": "happy upbeat",
    "amazing": "happy upbeat",
    "sad": "calm relaxing",
    "tired": "chill relaxing",
    "focus": "lofi instrumental",
    "project": "motivational upbeat",
    "work": "focus lo-fi",
}

def get_spotify_playlist_by_keyword(entry):
    entry_lower = entry.lower()
    for key, query in keyword_map.items():
        if key in entry_lower:
            results = sp.search(q=query, type="playlist", limit=1)
            items = results.get('playlists', {}).get('items', [])
            if items:
                playlist = items[0]
                name = playlist['name']
                url = playlist['external_urls']['spotify']
                image_url = playlist['images'][0]['url'] if playlist['images'] else None
                return name, url, image_url
    results = sp.search(q="chill", type="playlist", limit=1)
    items = results.get('playlists', {}).get('items', [])
    if items:
        playlist = items[0]
        name = playlist['name']
        url = playlist['external_urls']['spotify']
        image_url = playlist['images'][0]['url'] if playlist['images'] else None
        return name, url, image_url
    return "No playlist found", "#", None

# ---------------- CENTER THOUGHT BOX ----------------
thought_input = st.text_area(
    "Write your thoughts here...",
    height=250
)

# Apply mood color dynamically
if 'thought_input' in locals():
    st.markdown(f"""
    <style>
    div[data-baseweb="textarea"] textarea {{
        background-color: {get_mood_color("😐 Neutral")} !important;
    }}
    </style>
    """, unsafe_allow_html=True)

if st.button("🔍 Analyze & Save"):
    if thought_input.strip() == "":
        st.warning("Please write something before analyzing!")
    else:
        mood = analyze_mood(thought_input)
        save_entry(thought_input, mood)

        # Update text area color based on mood
        st.markdown(f"""
        <style>
        div[data-baseweb="textarea"] textarea {{
            background-color: {get_mood_color(mood)} !important;
        }}
        </style>
        """, unsafe_allow_html=True)

        # Mood + Playlist banner
        name, url, image_url = get_spotify_playlist_by_keyword(thought_input)
        st.markdown(f"<h3 style='text-align:center;'>{mood} 🎶 {name}</h3>", unsafe_allow_html=True)
        if image_url:
            st.markdown(f"<div style='text-align:center;'>[![{name}]({image_url})]({url})</div>", unsafe_allow_html=True)
        st.success(f"Your mood today: {mood}")
