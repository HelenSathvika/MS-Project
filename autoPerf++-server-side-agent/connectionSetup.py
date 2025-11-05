import socket
import json
import time

class connectionSetup:
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    port = 8986
    s.bind(('10.129.131.148', port))
    s.listen(1)
    c, addr = s.accept()
    data=""
    condition=True
    c.send("Connected to server".encode('utf-8'))


    def receiveData(self):
        self.data=self.c.recv(1024).decode('utf-8')
        self.data=json.loads(self.data)
        self.c.send("Received Data".encode('utf-8'))
        return True


