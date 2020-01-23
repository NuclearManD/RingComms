import socket, _thread, json

DEFAULT_PORT = 325

class ProtocolException(Exception):
    pass

class Communicator:
    def __init__(self, socket, on_recv_callback, on_close_callback):
        self.socket = socket
        self.socket.sendall(b'ring')
        if not socket.recv(4)==b'ring':
            raise ProtocolException()
        self.recv_callback = on_recv_callback
        self.close_callback = on_close_callback
        _thread.start_new_thread(self.__receiver__, ())
    def send_raw(self, jsonobj):
        text = json.dumps(jsonobj).encode()
        self.socket.sendall(len(text).to_bytes(3, 'big'))
        self.socket.sendall(text)
    def __receiver__(self):
        self.close_callback(self)
class Client:
    def __init__(self, address, port = DEFAULT_PORT):
        self.socket = socket.socket()
        self.socket.connect((address, port))
        
