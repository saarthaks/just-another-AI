import yaml
import alfredpath
from scipy.stats import chisquare
import random as r


class Brain(object):

    def __init__(self, speaker, profile):
        self.speaker = speaker
        self.profile = profile

    def ask(self, state, response, flag):
        threshold = 0.75

        if flag:
            flag = False
            return (True, self.speaker.ask("Continuing Ask"))

        if state.mod == "start":
            return (True, self.speaker.ask("Initial Ask"))

        if state.mod.__name__ == "Goal":
            resp = self.speaker.ask("Ending Ask")
            if resp['result']['resolvedQuery'] == "yes":
                return (True, None)

        count = state.counts
        if count > 10:
            max = state.max_child()
            child_counts = [c.count for c in state.children]

            if max is not None and (self.random_ask(child_counts) or max.get_probability() > threshold):
                return (False, response)

        return (True, self.speaker.ask("Continuing Ask"))

    def random_ask(self, counts):
        chi_val, p = chisquare(counts)
        x = r.random()
        if x > p:
            return True
        return False

    def update_personality_tree(self, root, profile):
        profile["personality"] = root
        outputFile = open(alfredpath.pi_builder('personality.yml'), "w")
        yaml.dump(profile, outputFile, default_flow_style=False)
        outputFile.close()

    def query(self, profile, texts):
        root = profile["personality"]
        current_state = root
        current_state.update_occurrences()
        response = texts
        flag = False
        while current_state.mod == "start" or current_state.mod.__name__ != "Goal":

            if len(current_state.children) == 0:
                print "Adding new states... "
                current_state.load_allStates()

            ask, response = self.ask(current_state, response, flag)
            if ask:
                children = [child for child in current_state.children if child.mod.isValid(response)]
                if children:
                    child = children[0]
                    print child.mod.__name__
                    response = child.mod.handle(response, self.speaker, self.profile)
                    child.update_occurrences()
                    current_state = child
                else:
                    self.speaker.say("Sorry")
                    continue
            else:
                child = current_state.max_child()
                if child.mod.__name__ != "Goal":
                    response = child.mod.handle(response, self.speaker, self.profile)
                    child.update_occurrences()
                    current_state = child
                else:
                    if self.ask(child, response, flag):
                        response = child.mod.handle(response, self.speaker, self.profile)
                        child.update_occurrences()
                        current_state = child
                    else:
                        flag = True
                        continue
        self.update_personality_tree(root, profile)
        return

