WORDS = ["text", "message"]

def isValid(text):
    if [word for word in WORDS if word in text]:
        return True

    return False

def handle(text, speaker, profile):
    resp = "Texting Mom on my way."
    return resp.split()

