import socket, _thread, json, time

DEFAULT_PORT = 325

class ProtocolException(Exception):
    pass

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

class Communicator:
    def __init__(self, socket, on_recv_callback, on_close_callback):
        self.socket = socket
        self.socket.sendall(b'ring')
        if not socket.recv(4)==b'ring':
            raise ProtocolException()
        self.recv_callback = on_recv_callback
        self.close_callback = on_close_callback
        _thread.start_new_thread(self.__receiver__, ())
    def send_raw(self, json_txt):
        text = json_txt.encode()
        self.socket.sendall(len(text).to_bytes(3, 'big'))
        self.socket.sendall(text)
    def __receiver__(self):
        try:
            while True:
                lenbytes = self.socket.recv(3)
                if len(lenbytes) != 3:
                    break
                length = int.from_bytes(lenbytes, 'big')
                data = self.socket.recv(length).decode()
                self.recv_callback(self, data)
        except:
            pass
        self.close_callback(self)
        

class Client:
    def __init__(self, address, port = DEFAULT_PORT):
        self.socket = socket.socket()
        self.socket.connect((address, port))
        self.com = Communicator(sok, self.on_recv, self.on_close)


