import re, json, time, random
from cityhash import CityHash128
from threading import Lock

TOPIC_KEY = '%topic'
DATA_KEY = '%data'

class Subscriber:
    def __init__(self, manager, callback, topic_pattern):
        self.topic = re.compile(topic_pattern)
        self.callback = callback
        self.manager = manager
    def recv(self, jsonobj):
        if self.topic.fullmatch(jsonobj[TOPIC_KEY]) !=None:
            self.callback(self, jsonobj[DATA_KEY])
class Publisher:
    def __init__(self, manager, topic):
        self.topic = topic
        self.man = manager
    def publish(self, payload):
        self.man.publish(self.topic, payload)
        
class Manager:
    def __init__(self):
        self.coms = []
        self.subscribers = []
        self.hashes = []
        self.hash_times = []
        self.hash_lock = Lock()
    def add_com(self, com):
        self.coms.append(com)
    def subscribe(self, callback, topic_pattern):
        sub = Subscriber(self, callback, topic_pattern)
        self.subscribers.append(sub)
        return sub
    def advertise(self, topic):
        return Publisher(self, topic)
    def publish(self, topic, payload):
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
def test_hash_speed():
    def timehash(indata):
        t = time.time()
        res = CityHash128(indata)
        return time.time() - t
    def time_len(l):
        'returns hashes/second for random bytes of length l'
        t = time.time() + 10
        n = 0
        timer = 0
        while t > time.time():
            n += 1
            data = ''
            for i in range(l):
                data += chr(random.randint(0,255))
            timer += timehash(data)
        return n / timer
    print("Testing for short messages (128 bytes)")
    short_speed = round(time_len(128)/1000000, 3)
    print(str(short_speed) + " Mhashes/sec")
    print("Testing for long messages (8192 bytes)")
    long_speed = round(time_len(8192)/1000000, 3)
    print(str(long_speed) + " Mhashes/sec")
