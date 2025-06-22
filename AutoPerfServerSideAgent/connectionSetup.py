import socket
import json

class connectionSetup:

    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM) #Open Socket 
    IPAdress = ""
    port = 0
    s.bind((IPAdress, port)) #Bind to this IP Address and Port
    s.listen(1) #Start Listening
    c, addr = s.accept() #Accept Connection
    data=""
    condition=True
    c.send("Connected to server".encode('utf-8'))

    def receiveData(self):
        self.data=self.c.recv(1024).decode('utf-8')
        self.data=json.loads(self.data)
        self.c.send("Received Data".encode('utf-8'))
        return True
