import imaplib
import email
import re
from dateutil import parser
import datetime


action = "read.email"

def getSender(email):
    sender = email['from']
    m = re.match(r'(.*)\s<.*>', sender)
    if m:
        return m.group(1)
    return sender

def getDate(email):
    return parser.parse(email.get('date'))

def getMostRecentDate(emails):
    dates = [getDate(e) for e in emails]
    dates.sort(reverse=True)
    if dates:
        return dates[0]
    return None

def fetchUnreadEmails(profile, since=None, markRead=False, limit=None):
    conn = imaplib.IMAP4_SSL('imap.gmail.com')
    conn.debug = 0
    conn.login(profile['gmail_address'], profile['gmail_password'])
    conn.select(readonly=(not markRead))

    msgs = []
    (retcode, messages) = conn.search(None, '(UNSEEN)')

    if retcode == 'OK' and messages != ['']:
        numUnread = len(messages[0].split(' '))
        if limit and numUnread > limit:
            return numUnread

        for num in messages[0].split(' '):
            ret, data = conn.fetch(num, '(RFC822)')
            msg = email.message_from_string(data[0][1])

            if not since or getDate(msg) > since:
                msgs.append(msg)

    conn.close()
    conn.logout()

    return msgs

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
    try:
        msgs = fetchUnreadEmails(profile, limit=5)

        if isinstance(msgs, int):
            resp = "You have %d unread emails." % msgs
            speaker.say(resp.split())
            return

        senders = [getSender(e) for e in msgs]
    except imaplib.IMAP4.error:
        resp = "I'm sorry. I'm not authenticated to work with your Gmail."
        speaker.say(resp)
        return build_JSON(resp, 404)

    if not senders:
        resp = "You have no unread emails."
    elif len(senders) == 1:
        resp = "You have one unread email from " + senders[0] + "."
    else:
        resp = "You have %d unread emails" % len(senders)
        unique_senders = list(set(senders))
        if len(unique_senders) > 1:
            unique_senders[-1] = 'and ' + unique_senders[-1]
            resp += ". Senders include: "
            resp += '...'.join(senders)
        else:
            resp += " from " + unique_senders[0]

    speaker.say(resp)
    return build_JSON(resp, 200)

