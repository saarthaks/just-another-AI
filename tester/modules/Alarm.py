WORDS = ["alarm"]

def isValid(text):
    if [word for word in WORDS if word in text]:
        return True

    return False

def handle(text, speaker, profile):
    resp = "Setting alarm for 8 pm."
    return resp.split()

