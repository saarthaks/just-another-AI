import spotify
import threading


action = "play.music"

def make_thread():
    logged_in_event = threading.Event()
    return logged_in_event

def connection_state_listener(session, logged_in_event):
    if session.connection.state is spotify.ConnectionState.LOGGED_IN:
        logged_in_event.set()

def loginSpotify(profile):
    session = spotify.Session()
    logged_in_event = make_thread()
    session.on(spotify.SessionEvent.CONNECTION_STATE_UPDATED, connection_state_listener)

    usr = profile['spotify_username']
    pswd = profile['spotify_password']
    session.login(usr, pswd)
    while not logged_in_event.wait(0.1):
        session.process_events()

    return session

def playSong(artist=None, playlist=None):
    return None, None


def isValid(text):
    if text['result']['action'] == action:
        return True

    return False

def handle(text, speaker, profile):

    session = loginSpotify(profile)

    artist = text['parameters']['music-artist']
    genre = text['parameters']['music-genre']

    if artist != "":
        search = session.search(artist, search_type=spotify.SearchType.SUGGEST).load()
        artist = search.artists[0].load().name if len(search.artists) > 0 else artist = None
    if genre != "":
        search = session.search(genre, search_type=spotify.SearchType.SUGGEST).load()
        genre = search.playlists[0].load().name if len(search.playlists) > 0 else genre = None

    song, artist = playSong(artist, genre)

    resp = "Playing "
    resp += song
    resp += " by "
    resp += artist
    resp += "."
    return resp.split()

