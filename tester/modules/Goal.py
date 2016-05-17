WORDS = ["nope", "no"]

def isValid(text):
    if [word for word in WORDS if word in text]:
        return True

    return False

def handle(text, speaker, profile):
    resp = "Have a nice day sir."
    return resp.split()
