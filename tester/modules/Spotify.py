import spotify
import threading
import datetime


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

def build_JSON(resp, code):
    mes = {}
    mes['id'] = "self-made"
    mes['timestamp'] = str(datetime.datetime.utcnow().isoformat('T')) + 'Z'
    mes['result'] = {}
    mes['result']['source'] = "self"
    mes['result']['resolvedQuery'] = resp
    mes['status'] = {}
    mes['status']['code'] = code
    mes['status']['errorType'] = "success" if code==200 else "failure"

    return mes

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
    speaker.say(resp)
    return build_JSON(resp, 200)

