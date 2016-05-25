from brain import Brain
from notifier import Notifier

class Conversation(object):

    def __init__(self, persona, speaker, profile):
        self.persona = persona
        self.speaker = speaker
        self.profile = profile
        self.notifier = Notifier(profile)
        self.brain = Brain(speaker, profile)

    def handleForever(self):

        while True:

            notifications = self.notifier.getAllNotifications()
            for notif in notifications:
                self.speaker.say(notif)

            threshold, transcribed = self.speaker.passiveListen(self.persona)
            if not threshold or not transcribed:
                continue

            input = self.speaker.activeListenToAllOptions(threshold)

            if input:
                self.brain.query(self.profile, transcribed)