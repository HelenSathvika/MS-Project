#!/usr/bin/env python3
import json
import ast
import itertools
import time

class ServerConfigurationMaster:

    def setSoftwareResource(self,resource_details,socket_connect_info):
        software_resource_name=resource_details['name']
        software_resource_path=resource_details['filePath']
        software_resource_regexp=resource_details['reqExp']
        software_resource_value=resource_details['value']
        software_resource_commands=resource_details['commands']
        software_resource_timewait=resource_details['timeWait']
        socket_connect_info.send((json.dumps(["setsoftwareResoruceConfiguration",software_resource_path,software_resource_regexp,software_resource_value,software_resource_commands,software_resource_timewait])+'\n').encode('utf-8'))
        data=socket_connect_info.recv(1024).decode('utf-8')
        data=socket_connect_info.recv(1024).decode('utf-8')
        return

    def setCores(self,cores,socket_connect_info):
        socket_connect_info.send((json.dumps(["setCores",cores])+'\n').encode('utf-8'))
        data=socket_connect_info.recv(1024).decode('utf-8')
        data=socket_connect_info.recv(1024).decode('utf-8')
        data=socket_connect_info.recv(1024).decode('utf-8')
        no_of_server_cores=json.loads(data)
        return