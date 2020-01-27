from cryptography.fernet import Fernet
from ringman import TOPIC_KEY, DATA_KEY, CRYPT_KEY
import json, re

class FernetSubscriber:
    def __init__(self, manager, callback, topic_pattern, key):
        'Create a subscriber object using Cryptography\'s Fernet'
        self.topic = re.compile(topic_pattern)
        self.callback = callback
        self.manager = manager
        manager.subscribers.append(self)
        self.fernet = Fernet(key)
    def recv(self, jsonobj):
        'Internal use; processes incoming messages and calls the callback'
        if self.topic.fullmatch(jsonobj[TOPIC_KEY]) !=None:
            try:
                data = json.loads(self.fernet.decrypt(jsonobj[CRYPT_KEY].encode()).decode())
            except:
                return
            self.callback(self, jsonobj[TOPIC_KEY], data)

class FernetPublisher:
    def __init__(self, manager, topic, key):
        'Create a publisher object using Cryptography\'s Fernet'
        self.topic = topic
        self.man = manager
        self.fernet = Fernet(key)
    def publish(self, payload):
        'Publish a message'
        data = json.dumps(payload).encode()
        cyphertext = self.fernet.encrypt(data).decode()
        self.man.publish_crypt(self.topic, cyphertext)
