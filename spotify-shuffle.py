import spotipy
import spotipy.util as util

from itertools import count
import random

from tkinter import *
import json


def shuffle(lst):
    temp = lst
    random.shuffle(temp)
    return temp

# def collect_playlists(user):
#     playlists = []
#     for request in count(0):
#         items = sp.user_playlists(user, offset = request*50)["items"]
#         playlists += items
#         if len(items) < 50:
#             break
#     return playlists

def collect_tracks(id):
    tracks = []
    for request in count(0):
        items = sp.playlist_tracks(playlist_id=id, offset=100*request)["items"]
        tracks += items
        if len(items) < 100:
            break
    tracks = [track["track"]["id"] for track in tracks if track["track"]["id"] != None]
    return tracks

def current_playlist():
    context = sp.current_playback()["context"]
    if context != None and context["type"] == "playlist":
        return(context["uri"][-22:])

# def playlist_selector(lst):
#     print(0,"Currently playing playlist")
#     for i,playlist in enumerate(lst):
#         print(f"{i+1} {playlist['name']}")
#     option = input(">>")
#     if option == "0" or option == "0 ":
#         return current_playlist()
#     try:
#         return lst[int(option)-1]["id"]
#     except:
#         print('Try again\n')
#         playlist_selector(lst)

def construct_play_playlist(ids):
    sp.user_playlist_create(user=user_id,name="Your Shuffled Playlist",public=False,description="This playlist is only supposed to be created temporarily feel free to delete this playlist")

    temp_playlist_id = sp.user_playlists(user_id, limit = 1)["items"][0]["id"]

    for request in range((len(ids)//100) + 1):
       sp.user_playlist_add_tracks(user=user_id,playlist_id=temp_playlist_id,tracks=ids[request*100:(request+1)*100],position=0)

    context_uri = "spotify:playlist:" + temp_playlist_id
    sp.start_playback(context_uri=context_uri)
    sp.user_playlist_unfollow(user = user_id, playlist_id = temp_playlist_id)

def write_json(client_id, client_secret):
    file = open("client_ids.json","w")
    file.write(json.dumps({"client_id":client_id,"client_secret":client_secret}))

def read_json():
    try:
        file = open("client_ids.json","r")
        dic = json.loads(file.read())
        file.close()
        return (dic["client_id"], dic["client_secret"])
    except FileNotFoundError:
        write_json("","")
        read_json()

#######################################################################################################################

def clear_window(window):
    for widget in window.winfo_children():
        widget.destroy()

def auth_window():
    def button_press():

        scope = 'streaming playlist-read-private playlist-modify-private user-modify-playback-state user-read-currently-playing user-read-playback-state playlist-read-collaborative'
        redirect_uri = "http://localhost/"
        client_id = client_id_entry.get()
        client_secret = client_secret_entry.get()

        token = util.prompt_for_user_token(username="",scope=scope,client_id=client_id,client_secret=client_secret,redirect_uri=redirect_uri)
        global sp
        sp = spotipy.Spotify(auth=token)

        write_json(client_id,client_secret)

        shuffle_page()


    client_id_saved, client_secret_saved = read_json()

    client_id_label = Label(window,text="Client ID:",font=("Calibri", 18)).grid(row=0,column=0)

    client_id_entry = Entry(window,width=40)
    client_id_entry.insert(0,client_id_saved)
    client_id_entry.grid(row=0,column=1)

    client_secret_label = Label(window,text="Client Secret:",font=("Calibri", 18)).grid(row=1,column=0)
    client_secret_entry = Entry(window,width=40)
    client_secret_entry.insert(0,client_secret_saved)
    client_secret_entry.grid(row=1,column=1)

    Label(window,text="Follow instructions in the terminal/console",font=("Calibri", 13)).grid(row=2,columnspan=2)
    button = Button(window,command=button_press,text="Authorise",height=2,width=50).grid(row=3,columnspan=2)

def shuffle_page():
    def shuffle_button_press():
        construct_play_playlist(shuffle(collect_tracks(current_playlist())))

    clear_window(window)

    global user_id
    user_id = sp.current_user()["id"]

    shuffle_button = Button(window,text="Shuffle current playlist",command=shuffle_button_press,height=7,width=50,font=("Calibri", 18))
    shuffle_button.pack()

window = Tk()
window.title("Spotify Shuffle")
window.geometry("395x150")
window.resizable(0, 0)
auth_window()
mainloop()