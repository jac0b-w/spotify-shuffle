import spotipy
import spotipy.util as util

from itertools import count
import random

##########################################################

user_id = "your user id"
client_id = "your client id"
client_secret = "your client secret"

##########################################################

scope = 'streaming playlist-read-private playlist-modify-private user-modify-playback-state user-read-currently-playing user-read-playback-state playlist-read-collaborative'

redirect_uri = "http://localhost:8888/callback"

def shuffle(lst):
    temp = lst
    random.shuffle(temp)
    return temp

def collect_playlists(user):
    playlists = []
    for request in count(0):
        items = sp.user_playlists(user, offset = request*50)["items"]
        playlists += items
        if len(items) < 50:
            break
    return playlists

def collect_tracks(id):
    tracks = []
    for request in count(0):
        items = sp.playlist_tracks(playlist_id=id, offset=100*request)["items"]
        tracks += items
        if len(items) < 100:
            break
    return tracks

def current_playlist():
    context = sp.current_playback()["context"]
    if context != None and context["type"] == "playlist":
        return(context["uri"][-22:])

def playlist_selector(lst):
    print(0,"Currently playing playlist")
    for i,playlist in enumerate(lst):
        print(f"{i+1} {playlist['name']}")
    option = input(">>")
    if option == "0" or option == "0 ":
        return current_playlist()
    try:
        return lst[int(option)-1]["id"]
    except:
        print('Try again\n')
        playlist_selector(lst)

token = util.prompt_for_user_token(username=user_id,scope=scope,client_id=client_id,client_secret=client_secret,redirect_uri=redirect_uri)

if token:
    sp = spotipy.Spotify(auth=token)
    while True:
        playlist_id = playlist_selector(collect_playlists(user_id))
        tracks = collect_tracks(playlist_id)
        shuffled_ids = shuffle([track["track"]["id"] for track in tracks if track["track"]["id"] != None])

        sp.user_playlist_create(user=user_id,name="Your Shuffled Playlist",public=False,description="This playlist is only supposed to be created temporarily feel free to delete this playlist")

        temp_playlist_id = sp.user_playlists(user_id, limit = 1)["items"][0]["id"]

        for request in range((len(shuffled_ids)//100) + 1):
           sp.user_playlist_add_tracks(user=user_id,playlist_id=temp_playlist_id,tracks=shuffled_ids[request*100:(request+1)*100],position=0)

        context_uri = "spotify:playlist:" + temp_playlist_id
        sp.start_playback(context_uri=context_uri)
        sp.user_playlist_unfollow(user = user_id, playlist_id = temp_playlist_id)

else:
    print("Can't get token for", user_id)