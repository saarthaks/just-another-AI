WORDS = ["calendar", "event", "events"]

def isValid(text):
    if [word for word in WORDS if word in text]:
        return True

    return False

def handle(text, speaker, profile):
    resp = "You have 2 events. AP at 4 and Prob/Stats at 7."
    return resp.split()

