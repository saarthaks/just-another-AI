import yaml
import profile_builder as builder
from conversation import Conversation
from speaker import Speaker


class Alfred_Core(object):
    def __init__(self):
        self.speaker = Speaker()
        self.person = {}
        try:
            infile = open("/Users/user/Projects/alfred/tester/personality.yml", "r")
            print "Reading personality file ... "
            self.person = yaml.load(infile)
        except IOError:
            outfile = open("/Users/user/Projects/alfred/tester/personality.yml", "w")
            builder.add_personality_tree(self.person)
            builder.add_gmail_login(self.person)
            builder.add_spotify_login(self.person)
            builder.stt_setup(self.person)
            builder.tts_setup(self.person)
            yaml.dump(self.person, outfile, default_flow_style=False)
            outfile.close()


    def run(self):
        conversation = Conversation("alfred", self.speaker, self.person)
        conversation.handleForever()

if __name__ == "__main__":

    print("*******************************************************")
    print("*             ALFRED - THE TALKING COMPUTER           *")
    print("*              (c) 2016 Saarthak Sarup                *")
    print("*******************************************************")

    app = Alfred_Core()

    app.run()