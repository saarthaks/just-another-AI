import yaml
import profile_builder as builder
import alfredpath
from conversation import Conversation
from speaker import Speaker


class Alfred_Core(object):
    def __init__(self):
        self.person = {}
        try:
            infile = open(alfredpath.pi_builder('personality.yml'), "r")
            print "Reading personality file ... "
            self.person = yaml.load(infile)
        except IOError:
            outfile = open(alfredpath.pi_builder('personality.yml'), "w")
            builder.add_personality_tree(self.person)
            builder.add_gmail_login(self.person)
            builder.add_spotify_login(self.person)
            builder.stt_setup(self.person)
            builder.tts_setup(self.person)
            yaml.dump(self.person, outfile, default_flow_style=False)
            outfile.close()
        self.speaker = Speaker(self.person)


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