import spotipy

from itertools import count
import random

from tkinter import *
import json
from webbrowser import open as webbrowser_open
from os import getenv

##########################################################################################

def prompt_for_user_token(
    username,
    scope=None,
    client_id=None,
    client_secret=None,
    redirect_uri=None,
    cache_path=None,
    oauth_manager=None,
    show_dialog=False,
    create_token=False
):

    """ prompts the user to login if necessary and returns
        the user token suitable for use with the spotipy.Spotify
        constructor
        Parameters:
         - username - the Spotify username
         - scope - the desired scope of the request
         - client_id - the client id of your app
         - client_secret - the client secret of your app
         - redirect_uri - the redirect URI of your app
         - cache_path - path to location to save tokens
         - oauth_manager - Oauth manager object.
    """
    if not oauth_manager:
        if not client_id:
            client_id = getenv("SPOTIPY_CLIENT_ID")

        if not client_secret:
            client_secret = getenv("SPOTIPY_CLIENT_SECRET")

        if not redirect_uri:
            redirect_uri = getenv("SPOTIPY_REDIRECT_URI")

        if not client_id:
            print(
                """
                You need to set your Spotify API credentials.
                You can do this by setting environment variables like so:
                export SPOTIPY_CLIENT_ID='your-spotify-client-id'
                export SPOTIPY_CLIENT_SECRET='your-spotify-client-secret'
                export SPOTIPY_REDIRECT_URI='your-app-redirect-url'
                Get your credentials at
                    https://developer.spotify.com/my-applications
            """
            )
            raise spotipy.SpotifyException(550, -1, "no credentials set")

        cache_path = cache_path or ".cache-" + username

    sp_oauth = oauth_manager or spotipy.SpotifyOAuth(
        client_id,
        client_secret,
        redirect_uri,
        scope=scope,
        cache_path=cache_path,
        show_dialog=show_dialog
    )

    # try to get a valid token for this user, from the cache,
    # if not in the cache, the create a new (this will send
    # the user to a web page where they can authorize this app)

    cached_token = sp_oauth.get_cached_token()

    if not cached_token and create_token:
        url = redirect_link
        code = sp_oauth.parse_response_code(url)
        shuffle_page(sp_oauth.get_access_token(code, as_dict=False))
        
    elif not cached_token and not create_token:
        webbrowser_open(sp_oauth.get_authorize_url())
        show_redirect_entry()

    else:
        shuffle_page(cached_token["access_token"])

##########################################################################################
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
    file = open("client_ids.json","w")
    file.write(json.dumps({"client_id":client_id,"client_secret":client_secret}))
    file.close()

def read_json():
    try:
        file = open("client_ids.json","r")
        dic = json.loads(file.read())
        file.close()
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
        global redirect_link
        redirect_link = remove_spaces(redirect_link_entry.get())
        prompt_for_user_token(username="",scope=scope,client_id=client_id,client_secret=client_secret,redirect_uri=redirect_uri,create_token=True)

    Label(window,text="Redirect Link:",font=("Calibri", 18)).grid(row=4,column=0)
    redirect_link_entry = Entry(window,width=40)
    redirect_link_entry.grid(row=4,column=1)

    Button(window,command=auth_button_press,text="Authorise",height=2,width=50).grid(row=5,columnspan=2)

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

        prompt_for_user_token(username="",scope=scope,client_id=client_id,client_secret=client_secret,redirect_uri=redirect_uri,create_token=False)


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
        webbrowser_open_new(url)

    link = Label(window, text="Where do I find these?", fg="blue", cursor="hand2")
    link.grid(row = 2, columnspan =2)
    link.bind("<Button-1>", lambda e: callback("https://github.com/jac0b-w/spotify-shuffle/blob/master/README.md"))

    Button(window,command=sign_in_button_press,text="Sign In",height=2,width=50).grid(row=3,columnspan=2)


#  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  


def shuffle_page(my_token):
    def shuffle_button_press():
        shuffle_button.config(text = "loading...")
        construct_play_playlist(shuffle(collect_tracks(current_playlist())))
        shuffle_button.config(text = "Shuffle current playlist")

    global sp
    sp = spotipy.Spotify(auth=my_token)
    clear_window(window)

    global user_id
    user_id = sp.current_user()["id"]

    shuffle_button = Button(window,text="Shuffle current playlist",command=shuffle_button_press,height=7,width=50,font=("Calibri", 18))
    shuffle_button.pack()


window = Tk()

try:
   window.iconbitmap('icon.ico')
except TclError:
   pass

window.title("Spotify Shuffle")
window.geometry("395x225")
window.resizable(0, 0)
auth_page()
mainloop()