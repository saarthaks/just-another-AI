from __future__ import division
import os
import sys

rootDir = "/Users/user/Projects/alfred/tester/modules/"

class State(object):

    def __init__(self, backpointer, module):
        self.counts = 0
        self.backpointer = backpointer
        self.mod = module
        self.children = []

    def load_allStates(self):
        mods = []
        for dirName, subdirList, fileList in os.walk("./modules"):
            for file in fileList:
                file = file.split(".")
                mods.append(file[0])

        sys.path.append(rootDir)
        mods = map(__import__, mods)
        for mod in mods:
            self.children.append(State(self, mod))
        return

    def update_occurrences(self):
        self.counts += 1
        return

    def get_probability(self):
        ans = self.counts / self.backpointer.counts
        return ans

    def max_child(self):
        maxState = None
        maxProb = 0
        for child in self.children:
            if child.get_probability() > maxProb:
                maxProb = child.get_probability()
                maxState = child

        return maxState

    def handle(self, name, response, profile):
        if name == "email":
            resp = "You have no new mail."
        elif name == "calendar":
            resp = "You have 2 events. AP at 4 and Prob/Stats at 7."
        elif name == "music":
            resp = "Playing Panda by Desiigner."
        elif name == "text":
            resp = "Texting Mom on my way."
        elif name == "alarm":
            resp = "Setting alarm for 8 pm."
        else:
            resp = "Have a nice day sir."


        return resp
