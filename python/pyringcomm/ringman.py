import re

class Subscriber:
    def __init__(self, manager, callback, topic_pattern):
        self.topic = re.compile(topic_pattern)
        self.callback = callback
        self.manager = manager
    def recv(self, json):
        if self.topic.fullmatch(json['topic']) !=None:
            self.callback(self, json)

class Manager:
    def __init__(self):
        self.coms = []
        self.subscribers = []
    def add_com(self, com):
        self.coms.append(com)
    def subscribe(self, callback, topic_pattern):
        sub = Subscriber(self, callback, topic_pattern)
        self.subscribers.append(sub)
        return sub
    def on_recv(self, json):
        for i in self.subscribers:
            i.recv(json)
