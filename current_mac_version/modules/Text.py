import datetime


action = "send.message"

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
    resp = "Texting Mom on my way."
    speaker.say(resp)
    return build_JSON(resp, 200)

