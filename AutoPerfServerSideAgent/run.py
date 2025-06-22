import json
import time
import connectionSetup
import SetSoftResourceConfiguration
import SetCores
import profiler
import ThreadPoolClassification
import perfProfiler
class main:
    server_conf_json = sys.argv[1] 
    server_conf = json.loads(server_conf_json)
    connection_setup=connectionSetup.connectionSetup() #Create an instance of connectionSetUp
    connection_setup.IPAdress=server_conf['IPAdress']
    connection_setup.port=server_conf['port']
    sc=SetCores.SetCores()  #Create an instance of SetCores
    sc.password=server_conf['password']
    srco=SetSoftResourceConfiguration.SetSoftResourceConfiguration()  #Create an instance of SetSoftResourceConfiguration
    srco.password=server_conf['password']
    profiler_obj=profiler.profiler()  #Create an instance of Profiler
    ipbo=ThreadPoolClassification.ThreadPoolClassification()
    perf_profiler_obj=perfprofiler.perfprofiler() #Create an instance of Perf Profiler
    perf_profiler_obj.password=server_conf['password']
    while connection_setup.condition:
        signalSet=connection_setup.receiveData()
        if signalSet:
            if connection_setup.data[0]=="threadPoolClassification": #Start thread pool classification
                ipbo.start(connection_setup.data[1],connection_setup.data[2],connection_setup.data[3])
                connection_setup.c.send("Completed".encode('utf-8'))
                connection_setup.c.recv(1024).decode('utf-8')
            if connection_setup.data[0]=="similarityScore": #Get similarity score
                data=ipbo.calculateProcessSimilarity()
                connection_setup.c.send((json.dumps(data)+'\n').encode('utf-8'))
                connection_setup.c.recv(1024).decode('utf-8')
            if connection_setup.data[0]=="getApplicationResourceUsage": #Get application resource uasge
                data=profiler_obj.getApplicationResourceUsage()
                connection_setup.c.send((json.dumps(data)+'\n').encode('utf-8'))
                connection_setup.c.recv(1024).decode('utf-8')
            if connection_setup.data[0]=="getprocessResourceUsage": #Get process resource usage
                data=profiler_obj.getprocessResourceUsage()
                connection_setup.c.send((json.dumps(data)+'\n').encode('utf-8'))
                connection_setup.c.recv(1024).decode('utf-8')
            if connection_setup.data[0]=="getPerfApplicationResourceUsage": #Get cache misses data of entire application
                data=perf_profiler_obj.getApplicationResourceUsage()
                connection_setup.c.send((json.dumps(data)+'\n').encode('utf-8'))
                connection_setup.c.recv(1024).decode('utf-8')
            if connection_setup.data[0]=="getPerfProcessResourceUsage": #Get cache misses data of each process
                data=perf_profiler_obj.getprocessResourceUsage()
                connection_setup.c.send((json.dumps(data)+'\n').encode('utf-8'))
                connection_setup.c.recv(1024).decode('utf-8')
            if connection_setup.data[0]=="getCPUTime": #Get CPU Time
                data=profiler_obj.getCPUTime()
                connection_setup.c.send((json.dumps(data)+'\n').encode('utf-8'))
                connection_setup.c.recv(1024).decode('utf-8')
            if connection_setup.data[0]=="startGettingCPUTime": #Start getting CPU time
                profiler_obj.startGettingCPUTime()
            if connection_setup.data[0]=="profiling":
                if connection_setup.data[1]=="start": #Start Profiler
                    profiler_obj.start(connection_setup.data[2])
                elif connection_setup.data[1]=="stop": #Stop Profiling
                    profiler_obj.stop()
            if connection_setup.data[0]=="perfProfiling": 
                if connection_setup.data[1]=="start": #Start Perf profiling
                    perf_profiler_obj.start(connection_setup.data[2])
                elif connection_setup.data[1]=="stop": #Stop Perf profiling
                    perf_profiler_obj.stop()
            if connection_setup.data[0]=="SetCores": #Set Cores
                sc.data[0]=connection_setup.data[1]
                sc.setValue()
                connection_setup.c.send("Rescource value set".encode('utf-8'))
                connection_setup.c.send((json.dumps([sc.onlineCPUs])+'\n').encode('utf-8'))
            if connection_setup.data[0]=="setsoftwareResoruceConfiguration": #Set Soft Resource Configuration 
                srco.data[0]=connection_setup.data[1]
                srco.data[1]=connection_setup.data[2]
                srco.data[2]=connection_setup.data[3]
                srco.data[3]=connection_setup.data[4]
                srco.data[4]=connection_setup.data[5]
                srco.setValue()
                connection_setup.c.send("Soft rescource value set".encode('utf-8'))
            if connection_setup.data[0]=="Close Connection": #Close connection
                connection_setup.c.send("Connection Closed".encode('utf-8'))
                time.sleep(2)
                connection_setup.c.close()
                connection_setup.s.close()
                connection_setup.condition=False
