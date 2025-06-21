#!/usr/bin/env python3
import json
import ast
import itertools
import time

class ServerConfigurationMaster:

    def setSoftwareResource(self,resource_details,socket_connect_info): #Set the baseline soft resource configurations
        software_resource_name=resource_details['name'] #Name of the resource paramter
        software_resource_path=resource_details['filePath'] #File path 
        software_resource_regexp=resource_details['reqExp'] #Regular expression
        software_resource_value=resource_details['value'] #Value
        software_resource_commands=resource_details['commands'] #Command
        software_resource_timewait=resource_details['timeWait'] #Time to wait
        socket_connect_info.send((json.dumps(["setsoftwareResoruceConfiguration",software_resource_path,software_resource_regexp,software_resource_value,software_resource_commands,software_resource_timewait])+'\n').encode('utf-8')) #Send instruction to set the resource configuration
        data=socket_connect_info.recv(1024).decode('utf-8')
        data=socket_connect_info.recv(1024).decode('utf-8') #Recieve the msg "Value set"
        return

    def setCores(self,cores,socket_connect_info): #Set core value
        socket_connect_info.send((json.dumps(["setCores",cores])+'\n').encode('utf-8')) #Send instruction to server side agent to set the core level
        data=socket_connect_info.recv(1024).decode('utf-8')
        data=socket_connect_info.recv(1024).decode('utf-8')
        data=socket_connect_info.recv(1024).decode('utf-8')
        no_of_server_cores=json.loads(data)
        return
