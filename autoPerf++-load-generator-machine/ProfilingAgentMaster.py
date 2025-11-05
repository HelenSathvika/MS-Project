#!/usr/bin/env python3
import json
import time

class ProfilingAgentMaster:

    process_names=[]
    socket_connect_info=None

    def initialize(self,process_names,socket_connect_info):
        self.process_names=process_names
        self.socket_connect_info=socket_connect_info

    def startProfilingAgentAtServer(self):
        self.socket_connect_info.send((json.dumps(["profiling","start",self.process_names])+'\n').encode('utf-8'))
        self.socket_connect_info.recv(1024).decode('utf-8')

    def startPerfProfilingAtServer(self):
        self.socket_connect_info.send((json.dumps(["perfProfiling","start",self.process_names])+'\n').encode('utf-8'))
        self.socket_connect_info.recv(1024).decode('utf-8')

    def startGettingCPUTime(self):
        self.socket_connect_info.send((json.dumps(["startGettingCPUTime"])+'\n').encode('utf-8'))
        data=self.socket_connect_info.recv(1024).decode('utf-8')

    def getCPUTime(self):
        self.socket_connect_info.send((json.dumps(["getCPUTime"])+'\n').encode('utf-8'))
        self.socket_connect_info.recv(1024).decode('utf-8')
        self.socket_connect_info.setblocking(True)
        data=self.socket_connect_info.recv(1024).decode('utf-8')
        data=json.loads(data)
        self.socket_connect_info.send("Recieved data".encode('utf-8'))
        return data

    def getApplicationResourceUsage(self):
        self.socket_connect_info.send((json.dumps(["getApplicationResourceUsage"])+'\n').encode('utf-8'))
        self.socket_connect_info.recv(1024).decode('utf-8')
        self.socket_connect_info.setblocking(True)
        data=self.socket_connect_info.recv(1024).decode('utf-8')
        data=json.loads(data)
        self.socket_connect_info.send("Recieved data".encode('utf-8'))
        return data

    def getprocessResourceUsage(self):
        self.socket_connect_info.send((json.dumps(["getprocessResourceUsage"])+'\n').encode('utf-8'))
        self.socket_connect_info.recv(1024).decode('utf-8')
        self.socket_connect_info.setblocking(True)
        data=''
        while True:
            chunk=self.socket_connect_info.recv(1024).decode('utf-8')
            data=data+chunk
            if '\n' in chunk:
                break
        data=data.strip()
        data=json.loads(data)
        self.socket_connect_info.send("Recieved data".encode('utf-8'))
        return data

    def getPerfApplicationResourceUsage(self):
        self.socket_connect_info.send((json.dumps(["getPerfApplicationResourceUsage"])+'\n').encode('utf-8'))
        self.socket_connect_info.recv(1024).decode('utf-8')
        self.socket_connect_info.setblocking(True)
        data=self.socket_connect_info.recv(1024).decode('utf-8')
        data=json.loads(data)
        self.socket_connect_info.send("Recieved data".encode('utf-8'))
        return data

    def getPerfProcessResourceUsage(self):
        self.socket_connect_info.send((json.dumps(["getPerfProcessResourceUsage"])+'\n').encode('utf-8'))
        self.socket_connect_info.recv(1024).decode('utf-8')
        self.socket_connect_info.setblocking(True)
        data=''
        while True:
            chunk=self.socket_connect_info.recv(1024).decode('utf-8')
            data=data+chunk
            if '\n' in chunk:
                break
        data=data.strip()
        data=json.loads(data)
        self.socket_connect_info.send("Recieved data".encode('utf-8'))
        return data

    def stopProfilingAgentAtServer(self):
        self.socket_connect_info.send((json.dumps(["profiling","stop"])+'\n').encode('utf-8'))
        self.socket_connect_info.recv(1024).decode('utf-8')

    def stopPerfProfilingAgentAtServer(self):
        self.socket_connect_info.send((json.dumps(["perfProfiling","stop"])+'\n').encode('utf-8'))
        self.socket_connect_info.recv(1024).decode('utf-8')

    def identifyPotentialProcessBottlenecks(self,test_duration,event):
        self.socket_connect_info.send((json.dumps(["identifyPotentialProcessBottlenecks",event,self.process_names,test_duration])+'\n').encode('utf-8'))
        data=self.socket_connect_info.recv(1024).decode('utf-8')
        #self.socket_connect_info.setblocking(True)
        data=self.socket_connect_info.recv(1024).decode('utf-8')
        self.socket_connect_info.send("Recieved data".encode('utf-8'))

    def similarityCheck(self):
        self.socket_connect_info.send((json.dumps(["similarityCheck"])+'\n').encode('utf-8'))
        self.socket_connect_info.recv(1024).decode('utf-8')
        self.socket_connect_info.setblocking(True)
        data=''
        while True:
            chunk=self.socket_connect_info.recv(1024).decode('utf-8')
            if not chunk:
                break
            data=data+chunk
            if '\n' in chunk:
                break
        data=data.strip()
        data=json.loads(data)
        self.socket_connect_info.send("Recieved data".encode('utf-8'))
        return data

    