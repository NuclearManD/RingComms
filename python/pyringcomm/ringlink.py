import socket, _thread, json, time

DEFAULT_PORT = 325

class ProtocolException(Exception):
    pass

class Communicator:
    def __init__(self, socket, on_recv_callback, on_close_callback):
        'Create a Communicator to talk over TCP'
        self.socket = socket
        self.socket.sendall(b'ring')
        if not socket.recv(4)==b'ring':
            raise ProtocolException()
        self.recv_callback = on_recv_callback
        self.close_callback = on_close_callback
        _thread.start_new_thread(self.__receiver__, ())
    def send_raw(self, json_txt):
        'Internal use; send raw JSON text over the network'
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
        finally:
            self.close_callback(self)
        

class Client:
    def __init__(self, man, address, port = DEFAULT_PORT):
        'Connect to a server'
        self.socket = socket.socket()
        self.socket.connect((address, port))
        self.com = Communicator(sok, man.on_recv, man.on_close)
        self.manager = man
        man.add_com(self.com)
    def disconnect(self):
        'Close the connection to the server'
        self.manager.rm_com(self.com)
        self.socket.close()
class Server:
    def __init__(self, man, port = DEFAULT_PORT, adr='0.0.0.0'):
        'Create a server object'
        self.socket = socket.socket()
        self.socket.bind((adr, port))
        self.communicators = []
        self.running = False
        self.manager = man
    def start(self):
        'start the server. Will fail if already running'
        assert not self.running
        self.running = True
        self.socket.listen(1)
        _thread.start_new_thread(self.__server_thread__, ())
    def stop(self):
        'stop the server (can be started again with start())'
        self.running = False
    def close(self):
        'closes the server so the socket is closed, cannot start server again'
        self.stop()
        self.socket.close()
    def __server_thread__(self):
        while self.running:
            connection, client_address = sock.accept()
            try:
                com = Communicator(connection, self.man.on_recv, self.on_close)
            except ProtocolException:
                print("Failed to connect to " + str(client_address) + " because they are using the wrong protocol")
                connection.close()
                continue
            print("Connected to " + str(client_address))
            self.communicators.append(com)
            self.man.add_com(com)
