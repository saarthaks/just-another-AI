class Speaker():

    def say(self, text):
        print text

    def ask(self, text):
        return raw_input(text).split()
