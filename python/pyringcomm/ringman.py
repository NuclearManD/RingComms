import re, json
from cityhash import CityHash128
from threading import Lock

TOPIC_KEY = '%topic'
DATA_KEY = '%data'

class Subscriber:
    def __init__(self, manager, callback, topic_pattern):
        'Create a subscriber object manually'
        self.topic = re.compile(topic_pattern)
        self.callback = callback
        self.manager = manager
    def recv(self, jsonobj):
        'Internal use; processes incoming messages and calls the callback'
        if self.topic.fullmatch(jsonobj[TOPIC_KEY]) !=None:
            self.callback(self, jsonobj[DATA_KEY])
class Publisher:
    def __init__(self, manager, topic):
        'Create a publisher object manually'
        self.topic = topic
        self.man = manager
    def publish(self, payload):
        'Publish a message'
        self.man.publish(self.topic, payload)
        
class Manager:
    def __init__(self):
        'Class to manage connections, publishers, and subscribers'
        self.coms = []
        self.subscribers = []
        self.hashes = []
        self.hash_times = []
        self.hash_lock = Lock()
    def add_com(self, com):
        'Add a Communicator object'
        self.coms.append(com)
    def subscribe(self, callback, topic_pattern):
        'Get a subscriber to a topic or a pattern of topics'
        sub = Subscriber(self, callback, topic_pattern)
        self.subscribers.append(sub)
        return sub
    def advertise(self, topic):
        'Get a publisher for a topic'
        return Publisher(self, topic)
    def publish(self, topic, payload):
        'single-time publish of a topic'
        jsonobj = {
            TOPIC_KEY: topic,
            DATA_KEY : payload
            }
        json_txt = json.dumps(jsonobj)
        if self.hash_handle(json_txt):
            for i in self.subscribers:
                i.recv(jsonobj)
            for i in self.coms:
                i.send_raw(json_txt)
    def on_recv(self, src, json_txt):
        'Internal use; processes incoming JSON text and routes messages'
        if self.hash_handle(json_txt):
            jsonobj = json.loads(json_txt)
            for i in self.subscribers:
                i.recv(jsonobj)
            for i in self.coms:
                if i != src:
                    i.send_raw(json_txt)
    def hash_handle(self, json_txt):
        'Returns False if the message has already been processed.  Otherwise it stores the hash and returns True'
        hash = CityHash128(json_txt)
        if hash in self.hashes:
            return False
        time_limit = time.time() - 60
        with self.hash_lock:
            for i in range(len(self.hash_times)):
                if self.hash_times[i] > time_limit:
                    self.hash_times = self.hash_times[i:]
                    self.hashes = self.hashes[i:]
                    break
            self.hashes.append(hash)
            self.hash_times.append(time.time())
        return True
    def on_close(self, com):
        'Internal use; handler for a closed Communicator object'
        self.coms.remove(com)
