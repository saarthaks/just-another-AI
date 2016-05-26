import yaml


class Brain(object):

    def __init__(self, speaker, profile):
        self.speaker = speaker
        self.profile = profile

    def ask(self, state, response, flag):
        threshold = 0.75

        if flag:
            flag = False
            return (True, self.speaker.ask("Anything else?"))

        if state.mod == "start":
            return (True, self.speaker.ask("What can I do for you?"))

        if state.mod == "nope":
            return ((True if self.speaker.ask("Will that be all?") == "yes" else False), None)

        count = state.counts
        if count > 10:
            max = state.max_child()
            if max is not None and max.get_probability > threshold:
                return (False, response)

        return (True, self.speaker.ask("Anything else?"))

    def max_mod(self, state):
        return state.max_child()

    def update_personality_tree(self, root, profile):
        profile["personality"] = root
        outputFile = open("/Users/user/Projects/alfred/tester/personality.yml", "w")
        yaml.dump(profile, outputFile, default_flow_style=False)
        outputFile.close()

    def query(self, profile, texts):
        root = profile["personality"]
        current_state = root
        current_state.update_occurrences()
        response = texts
        flag = False
        while current_state.mod != "nope":

            if len(current_state.children) == 0:
                print "Adding new states... "
                current_state.load_allStates()

            ask, response = self.ask(current_state, response, flag)
            if ask:
                children = [child for child in current_state.children if child.mod in response]
                if children:
                    child = children[0]
                    response = child.handle(child.mod, response, self.profile)
                    self.speaker.say(response)
                    child.update_occurrences()
                    current_state = child
                else:
                    self.speaker.say("Sorry, I can't do that")
                    continue
            else:
                child = self.max_mod(current_state)
                if child.mod != "nope":
                    response = child.handle(child.mod, response, self.profile)
                    self.speaker.say(response)
                    child.update_occurrences()
                    current_state = child
                else:
                    if self.ask(child, response, flag):
                        response = child.handle(child.mod, response, self.profile)
                        self.speaker.say(response)
                        child.update_occurrences()
                        current_state = child
                    else:
                        flag = True
                        continue
        self.update_personality_tree(root, profile)
        return

