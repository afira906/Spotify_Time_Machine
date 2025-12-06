from bs4 import BeautifulSoup
import requests
import spotipy
from spotipy.oauth2 import SpotifyOAuth
from dotenv import load_dotenv
import os

load_dotenv()  # Loads variables from .env

Client_ID = os.getenv("CLIENT_ID")
Client_secret = os.getenv("CLIENT_SECRET")
display_name = os.getenv("DISPLAY_NAME")


# Scraping Billboard 100
date = input("Which year do you want to travel to? Type the date in this format YYYY-MM-DD: ")
header = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:131.0) Gecko/20100101 Firefox/131.0"}
billboard_url = "https://www.billboard.com/charts/hot-100/" + date
response = requests.get(url=billboard_url, headers=header)

soup = BeautifulSoup(response.text, 'html.parser')
song_names_spans = soup.select("li ul li h3")
song_names = [song.getText().strip() for song in song_names_spans]

# Spotify Authentication
sp = spotipy.Spotify(
    auth_manager=SpotifyOAuth(
        scope="playlist-modify-private",
        redirect_uri="http://127.0.0.1:3000/callback",
        client_id=Client_ID,
        client_secret=Client_secret,
        show_dialog=True,
        cache_path="token.txt"
    )
)
user_id = sp.current_user()["id"]
print("Fetching user id from Spotify")
# print(user_id)

# Searching Spotify for songs by title
song_uris = []
year = date.split("-")[0]
for song in song_names:
    result = sp.search(q=f"track:{song} year:{year}", type="track")
    print(f"Searching for song: {song}")
    # print(result)
    try:
        uri = result["tracks"]["items"][0]["uri"]
        song_uris.append(uri)
    except IndexError:
        print(f"{song} doesn't exist in Spotify. Skipped.")

# Creating a new private playlist in Spotify
playlist = sp.user_playlist_create(user=user_id, name=f"{date} Billboard 100", public=False)
print("Playlist has been created")
# print(playlist)

# Adding songs found into the new playlist
sp.playlist_add_items(playlist_id=playlist["id"], items=song_uris)
