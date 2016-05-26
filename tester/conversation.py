from brain import Brain

class Conversation(object):

    def __init__(self, persona, speaker, profile):
        self.persona = persona
        self.speaker = speaker
        self.profile = profile
        self.brain = Brain(speaker, profile)

    def handleForever(self):

        while True:
            text = raw_input("").split()
            input = False
            for word in text:
                if self.persona == word:
                    input = True
                else:
                    continue

            if input:
                self.brain.query(self.profile, text)