import socket
import json

class ConnectionSetup:

    IPAdress = ""
    port = 0
    s=""
    c=""
    data=""
    condition=False
    def initialize(self):
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM) #Open Socket 
        self.s.bind((self.IPAdress, self.port)) #Bind to this IP Address and Port
        self.s.listen(1) #Start Listening
        self.c, addr = self.s.accept() #Accept Connection
        self.condition=True
        self.c.send("Connected to server".encode('utf-8'))

    def receiveData(self):
        self.data=self.c.recv(1024).decode('utf-8')
        self.data=json.loads(self.data)
        self.c.send("Received Data".encode('utf-8'))
        return True


