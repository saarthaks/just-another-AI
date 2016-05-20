action = "send.message"

def isValid(text):
    if text['result']['action'] == action:
        return True

    return False

def handle(text, speaker, profile):
    resp = "Texting Mom on my way."
    return resp.split()

