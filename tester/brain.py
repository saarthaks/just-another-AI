import yaml


class Brain(object):

    def __init__(self, speaker, profile):

        self.speaker = speaker
        self.profile = profile

    def ask(self, state, response, flag):
        threshold = 0.75

        if flag:
            flag = False
            return (True, self.speaker.ask("What can I do for you?"))

        count = state.counts
        if count > 10:
            max = state.max_child()
            if max is not None and max.get_probability > threshold:
                return (False, response)

        return (True, self.speaker.ask("What can I do for you?"))

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
        while current_state.mod != "goal":
            while current_state.mod != "goal":

                if len(current_state.children) == 0:        #new leaf on tree
                    print "Adding states..."
                    current_state.load_allStates()

                ask, response = self.ask(current_state, response, flag)
                if ask:
                    for child in current_state.children:
                        for text in response:
                            if text == child.mod:
                                response = child.handle(child.mod, response, self.profile)
                                self.speaker.say(response)
                                child.update_occurrences()
                                current_state = child
                else:
                    child = self.max_mod(current_state)
                    response = child.handle(child.mod, response, self.profile)
                    self.speaker.say(response)
                    child.update_occurrences()
                    current_state = child

            ask, response = self.ask(current_state, response, flag)
            if ask:               #do you want to quit?
                if "end" in response:
                    self.update_personality_tree(root, profile)
                    return
                else:
                    current_state.update_occurrences(True)
                    current_state = current_state.backpointer
                    flag = True
            else:
                self.update_personality_tree(root, profile)
                return

