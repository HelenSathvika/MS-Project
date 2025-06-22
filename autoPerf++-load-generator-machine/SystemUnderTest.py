#!/usr/bin/env python3
import socket
import paramiko
import json

class SystemUnderTest:
    ip_adress=""
    port=0
    username=""
    password=""
    socket_connect_info=None
    server_conf={}
    path={}

    def setServerDetails(self):
        server_configurations="input-configurations/system-under-test-conf.json" #Read the relative systemUnderTest Configuration File
        with open(server_configurations,'rb') as file:
           server_conf_content=file.read()
        server_conf_json_content=server_conf_content.decode('utf-8')
        self.server_conf=json.loads(server_conf_json_content)
        
        #Store the details in variables
        server_details=self.server_conf['serverDetails'] 

        self.ip_adress=server_details['IPAdress'] #IP address of the server machine
        self.port=server_details['port'] #Port on which Server Side Agent Listens
        self.username=server_details['username']  #Username of the server machine
        self.password=server_details['password']  #Password of the server 
        self.path=server_details['path']

    def startServer(self): #Start Server Side Agent using SSH Protocol
        ssh=paramiko.SSHClient() 
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(self.ip_adress,username=self.username,password=self.password) #Connect to the server machine using SSH protocol
        dict_arg = json.dumps(self.server_conf['serverDetails'])
        command = f"python3 {self.path}Run.py '{dict_arg}' &"
        stdin,stdout,stderr=ssh.exec_command(command) #Execute the command to start the Server Side Agent Script
        channel=stdout.channel
        while not channel.exit_status_ready(): #If not able to exceute the coomand return
            pass

    def connectToServer(self): #Connect to the Server Side Agent using Socket Protocol
        self.socket_connect_info=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        self.socket_connect_info.connect((self.ip_adress,self.port))
        self.socket_connect_info.recv(1024).decode('utf-8') #Recieve a msg "Connected to Server"

    def closeServerConnection(self): #Close Connection
        self.socket_connect_info.send((json.dumps(["Close Connection"])+'\n').encode('utf-8'))
        data=self.socket_connect_info.recv(1024).decode('utf-8') ##Recieve a msg "Connection Closed"
        print(data)
        self.socket_connect_info.close()
