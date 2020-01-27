import time, random
from cityhash import CityHash128

class test_socket:
    def __init__(self):
        self.buffer = b'ring'
    def recv(self,n):
        while self.buffer == b'':
            time.sleep(.01)
        dt = self.buffer[:n]
        self.buffer = self.buffer[n:]
        return dt
    def wr(self, jsonobj):
        go = json.dumps(jsonobj).encode()
        self.buffer += len(go).to_bytes(3, 'big')
        self.buffer += go
    def sendall(self, d):
        print("sendall(" + repr(d) + ')')

def onrec(d, m):
    print("Com "+repr(d)+" revc'd " + repr(m))

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
