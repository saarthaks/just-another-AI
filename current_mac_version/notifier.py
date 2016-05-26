import Queue
import Gmail
from datetime import datetime as dt
from apscheduler.schedulers.background import BackgroundScheduler
import atexit


class Notifier(object):

    class NotificationClient(object):

        def __init__(self, gather, timestamp):
            self.gather = gather
            self.timestamp = timestamp

        def run(self):
            self.timestamp = self.gather(self.timestamp)

    def __init__(self, profile):
        self.q = Queue.Queue()
        self.profile = profile
        self.notifiers = []

        if 'gmail_address' in profile and 'gmail_password' in profile:
            self.notifiers.append(self.NotificationClient(self.handleGmailNotifcations, None))

        sched = BackgroundScheduler(timezone="EST", daemon=True)
        sched.start()
        sched.add_job(self.gather, 'interval', seconds=30)
        atexit.register(lambda: sched.shutdown(wait=False))

    def gather(self):
        [client.run() for client in self.notifiers]


    def handleGmailNotifications(self, lastDate):
        emails = Gmail.fetchUnreadEmails(self.profile, since=lastDate)
        if emails:
            lastDate = Gmail.getMostRecentDate(emails)

        def styleEmail(e):
            resp = "New email from %s" % Gmail.getSender(e)
            return resp.split()

        for e in emails:
            self.q.put(styleEmail(e))

        return lastDate

    def getNotifications(self):
        try:
            notif = self.q.get(block=False)
            return notif
        except Queue.Empty:
            return None

    def getAllNotifications(self):
        notifs = []

        notif = self.getNotifications()
        while notif:
            notifs.append(notif)
            notif = self.getNotifications()

        return notifs
