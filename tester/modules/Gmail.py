WORDS = ["email", "mail", "inbox"]

def isValid(text):
    if [word for word in WORDS if word in text]:
        return True

    return False

def handle(text, speaker, profile):
    resp = "You have no new mail"
    return resp.split()
