from datetime import datetime as dt


action = "set.alarm"

def isValid(text):
    if text['result']['action'] == action:
        return True

    return False

def extractAlarmTime(text, speaker):
    date_time = text["parameters"]["date-time"]
    try:
        date_time = dt.strptime(date_time, "%Y-%m-%dT%H:%M:%SZ")
    except ValueError:
        resp = speaker.ask("When should I set your alarm?")
        resp = resp["parameters"]["date-time"]
        date_time = dt.strptime(resp, "%Y-%m-%dT%H:%M:%SZ")

    return date_time

def build_JSON(resp, code):
    mes = {}
    mes['id'] = "self-made"
    mes['timestamp'] = str(dt.utcnow().isoformat('T')) + 'Z'
    mes['result'] = {}
    mes['result']['source'] = "self"
    mes['result']['resolvedQuery'] = resp
    mes['status'] = {}
    mes['status']['code'] = code
    mes['status']['errorType'] = "success" if code==200 else "failure"

    return mes

def handle(text, speaker, profile):
    date_time = extractAlarmTime(text, speaker)

    hr = str(date_time.hour % 12)
    m = "a m" if date_time.hour < 12 else "p m"
    min = str(date_time.minute)
    resp = "Setting alarm for "
    resp += hr
    resp += " "
    resp += min
    resp += " "
    resp += m
    resp += "."
    speaker.say(resp)
    return build_JSON(resp, 200)

