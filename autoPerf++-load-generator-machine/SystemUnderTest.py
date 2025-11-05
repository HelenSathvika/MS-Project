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

    def setServerDetails(self):
        server_configurations="input-configurations/system-under-test-conf.json"
        with open(server_configurations,'rb') as file:
           server_conf_content=file.read()
        server_conf_json_content=server_conf_content.decode('utf-8')
        self.server_conf=json.loads(server_conf_json_content)

        server_details=self.server_conf['serverDetails']

        self.ip_adress=server_details['IPAdress']
        self.port=server_details['port']
        self.username=server_details['username']
        self.password=server_details['password']

    def startServer(self):
        ssh=paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(self.ip_adress,username=self.username,password=self.password)
        stdin,stdout,stderr=ssh.exec_command("python3 /home/perf/autoperfsbserver/run.py &")
        channel=stdout.channel
        while not channel.exit_status_ready():
            pass

    def connectToServer(self):
        self.socket_connect_info=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        self.socket_connect_info.connect((self.ip_adress,self.port))
        self.socket_connect_info.recv(1024).decode('utf-8')

    def closeServerConnection(self):
        self.socket_connect_info.send((json.dumps(["Close Connection"])+'\n').encode('utf-8'))
        data=self.socket_connect_info.recv(1024).decode('utf-8')
        print(data)
        self.socket_connect_info.close()

    