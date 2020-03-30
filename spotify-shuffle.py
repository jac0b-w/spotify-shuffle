import spotipy

from itertools import count
from random import shuffle as rand_shuffle

from tkinter import *
from json import loads, dumps
from webbrowser import open as webbrowser_open

class ContextError(Exception):
    pass

def prompt_for_user_token(
    username,
    scope,
    client_id,
    client_secret,
    redirect_uri,
    redirect_link=None
):

    sp_oauth = spotipy.SpotifyOAuth(
        client_id=client_id,
        client_secret=client_secret,
        redirect_uri=redirect_uri,
        scope=scope,
        cache_path=".cache",
    )

    cached_token = sp_oauth.get_cached_token()

    if not cached_token and redirect_link:
        code = sp_oauth.parse_response_code(redirect_link)
        shuffle_page(sp_oauth.get_access_token(code, as_dict=False))
        
    elif not cached_token and not redirect_link:
        webbrowser_open(sp_oauth.get_authorize_url())
        show_redirect_entry()

    else:
        shuffle_page(cached_token["access_token"])

##########################################################################################
def shuffle(lst):
    temp = lst
    rand_shuffle(temp)
    return temp

def collect_tracks(context_uri):
    context = {"type":context_uri.split(":")[-2],"id":context_uri.split(":")[-1]}
    track_ids = []
    if context["type"] == "playlist":
        for request in count(0):
            items = sp.playlist_tracks(playlist_id=context["id"], offset=100*request)["items"]
            track_ids += [track["track"]["id"] for track in items]
            if len(items) < 100:
                break
    elif context["type"] == "album":
        for request in count(0):
            items = sp.album_tracks(album_id=context["id"], offset=50*request)["items"]
            track_ids += [track["id"] for track in items]
            if len(items) < 50:
                break
    return track_ids


def current_context_uri():
    context = sp.current_playback()["context"]
    if context == None:
        raise ContextError("Shuffling Liked Songs and Local Files \nis not supported\nTry Again")
    elif context["type"] == "artist":
        raise ContextError("Shuffling from the artist page \nis not supported\nTry Again")
    return(context["uri"])


def construct_play_playlist(ids):
    sp.user_playlist_create(user=user_id,name="Your Shuffled Playlist",public=False,description="This playlist is only supposed to be created temporarily feel free to delete this playlist")

    temp_playlist_id = sp.user_playlists(user_id, limit = 1)["items"][0]["id"]
    sp.user_playlist_unfollow(user = user_id, playlist_id = temp_playlist_id)
    context_uri = "spotify:playlist:" + temp_playlist_id

    #improves responsiveness for large playlists
    sp.user_playlist_add_tracks(user=user_id,playlist_id=temp_playlist_id,tracks=[ids[0]])
    sp.start_playback(context_uri=context_uri)
    ids = ids[1:]

    for request in range((len(ids)//100) + 1):
       sp.user_playlist_add_tracks(user=user_id,playlist_id=temp_playlist_id,tracks=ids[request*100:(request+1)*100])
    sp.user_playlist_unfollow(user = user_id, playlist_id = temp_playlist_id)
    

def write_json(client_id, client_secret):
    with open("client_ids.json","w") as f:
        f.write(dumps({"client_id":client_id,"client_secret":client_secret}))

def read_json():
    try:
        with open("client_ids.json","r") as f:
            dic = loads(f.read())
        return (dic["client_id"], dic["client_secret"])
    except FileNotFoundError:
        return ("","")

def remove_spaces(string):
    while string[-1] == " ":
        string = string[:-1]
    return string

#######################################################################################################################

def clear_window(window):
    for widget in window.winfo_children():
        widget.destroy()

#  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  
def show_redirect_entry():
    def auth_button_press():
        write_json(client_id,client_secret)
        #global redirect_link
        redirect_link = remove_spaces(redirect_link_entry.get())
        prompt_for_user_token(username="",scope=scope,client_id=client_id,client_secret=client_secret,redirect_uri=redirect_uri,redirect_link=redirect_link)

    Label(window,text="""
        Sign into your spotify account and once you reach the 
        'This site can’t be reached' page copy the url and paste it here.
        (starts with: 'localhost/?code=')
        """).grid(row=4,columnspan=2)
    Label(window,text="Redirect URL:",font=("Calibri", 18)).grid(row=6,column=0)
    redirect_link_entry = Entry(window,width=40)
    redirect_link_entry.grid(row=6,column=1)

    Button(window,command=auth_button_press,text="Authorise",height=2,width=50).grid(row=7,columnspan=2)

def auth_page():
    def sign_in_button_press():
        global scope
        global redirect_uri

        scope = 'streaming playlist-read-private playlist-modify-private user-modify-playback-state user-read-currently-playing user-read-playback-state playlist-read-collaborative'
        redirect_uri = "http://localhost/"

        global client_id
        global client_secret
        client_id = remove_spaces(client_id_entry.get())
        client_secret = remove_spaces(client_secret_entry.get())

        prompt_for_user_token(username="",scope=scope,client_id=client_id,client_secret=client_secret,redirect_uri=redirect_uri)


    client_id_saved, client_secret_saved = read_json()

    Label(window,text="Client ID:",font=("Calibri", 18)).grid(row=0,column=0)
    client_id_entry = Entry(window,width=40)
    client_id_entry.insert(0,client_id_saved)
    client_id_entry.grid(row=0,column=1)

    Label(window,text="Client Secret:",font=("Calibri", 18)).grid(row=1,column=0)
    client_secret_entry = Entry(window,width=40)
    client_secret_entry.insert(0,client_secret_saved)
    client_secret_entry.grid(row=1,column=1)

    def callback(url):
        webbrowser_open(url)

    link = Label(window, text="Where do I find these?", fg="blue", cursor="hand2")
    link.grid(row = 2, columnspan =2)
    link.bind("<Button-1>", lambda e: callback("https://github.com/jac0b-w/spotify-shuffle/blob/master/README.md"))

    Button(window,command=sign_in_button_press,text="Sign In",height=2,width=50).grid(row=3,columnspan=2)


#  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  


def shuffle_page(my_token):
    def shuffle_button_press():
        try:
            construct_play_playlist(shuffle(collect_tracks(current_context_uri())))
        except ContextError as e:
            shuffle_button.config(text = e)

    global sp
    sp = spotipy.Spotify(auth=my_token)
    clear_window(window)

    global user_id
    user_id = sp.current_user()["id"]

    Label(window,text="""
        You cannot shuffle with a free account
        Shuffling your liked songs is not currently supported
        """).grid(row=0)
    shuffle_button = Button(window,text="Shuffle current playlist",command=shuffle_button_press,height=7,width=30,font=("Calibri", 18))
    shuffle_button.grid(row=1)


window = Tk()
    
try:
    window.iconbitmap('spotify-shuffle.exe')
except TclError:
    try:
        window.iconbitmap('icon.ico')
    except TclError:
        pass

window.title("Spotify Shuffle")
window.geometry("395x300")
window.resizable(0, 0)
auth_page()
mainloop()