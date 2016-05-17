WORDS = ["music", "spotify", "song"]

def isValid(text):
    if [word for word in WORDS if word in text]:
        return True

    return False

def handle(text, speaker, profile):
    resp = "Playing Panda by Desiigner."
    return resp.split()

