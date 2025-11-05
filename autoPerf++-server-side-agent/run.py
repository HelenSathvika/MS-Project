import json
import time
import connectionSetup
import setSoftwareResourceConfiguration
import setCores
import profiling
#import identifyPotentialProcessBottlenecks
import perfProfiling
class main:                                                                  
    connection_setup=connectionSetup.connectionSetup()
    print(1)
    sc=setCores.setCores()
    srco=setSoftwareResourceConfiguration.setSoftwareResourceConfiguration()
    profiling_obj=profiling.profiling()
    #ipbo=identifyPotentialProcessBottlenecks.identifyPotentialProcessBottlenecks()
    perf_profiling_obj=perfProfiling.perfProfiling()
    while connection_setup.condition:
        signalSet=connection_setup.receiveData()
        if signalSet:
            # if connection_setup.data[0]=="identifyPotentialProcessBottlenecks":
            #     ipbo.start(connection_setup.data[1],connection_setup.data[2],connection_setup.data[3])
            #     connection_setup.c.send("Completed".encode('utf-8'))
            #     connection_setup.c.recv(1024).decode('utf-8')
            # if connection_setup.data[0]=="similarityCheck":
            #     data=ipbo.calculateProcessSimilarity()
            #     connection_setup.c.send((json.dumps(data)+'\n').encode('utf-8'))
            #     connection_setup.c.recv(1024).decode('utf-8')
            if connection_setup.data[0]=="getApplicationResourceUsage":
                data=profiling_obj.getApplicationResourceUsage()
                connection_setup.c.send((json.dumps(data)+'\n').encode('utf-8'))
                connection_setup.c.recv(1024).decode('utf-8')
            if connection_setup.data[0]=="getprocessResourceUsage":
                data=profiling_obj.getprocessResourceUsage()
                connection_setup.c.send((json.dumps(data)+'\n').encode('utf-8'))
                connection_setup.c.recv(1024).decode('utf-8')
            if connection_setup.data[0]=="getPerfApplicationResourceUsage":
                data=perf_profiling_obj.getApplicationResourceUsage()
                connection_setup.c.send((json.dumps(data)+'\n').encode('utf-8'))
                connection_setup.c.recv(1024).decode('utf-8')
            if connection_setup.data[0]=="getPerfProcessResourceUsage":
                data=perf_profiling_obj.getprocessResourceUsage()
                connection_setup.c.send((json.dumps(data)+'\n').encode('utf-8'))
                connection_setup.c.recv(1024).decode('utf-8')
            if connection_setup.data[0]=="getCPUTime":
                data=profiling_obj.getCPUTime()
                connection_setup.c.send((json.dumps(data)+'\n').encode('utf-8'))
                connection_setup.c.recv(1024).decode('utf-8')
            if connection_setup.data[0]=="startGettingCPUTime":
                profiling_obj.startGettingCPUTime()
            if connection_setup.data[0]=="profiling":
                if connection_setup.data[1]=="start":
                    profiling_obj.start(connection_setup.data[2])
                elif connection_setup.data[1]=="stop":
                    profiling_obj.stop()
            if connection_setup.data[0]=="perfProfiling":
                if connection_setup.data[1]=="start":
                    perf_profiling_obj.start(connection_setup.data[2])
                elif connection_setup.data[1]=="stop":
                    perf_profiling_obj.stop()
            if connection_setup.data[0]=="setCores":
                #connection_setup.c.send("Rescource value set".encode('utf-8'))
                sc.data[0]=connection_setup.data[1]
                print(json.dumps([sc.data[0]]))
                #connection_setup.c.send((json.dumps([sc.data[0]])+'\n').encode('utf-8'))
                
                sc.setValue()
                #connection_setup.c.send("Rescource value set".encode('utf-8'))
                connection_setup.c.send((json.dumps([sc.onlineCPUs])+'\n').encode('utf-8'))
            if connection_setup.data[0]=="setsoftwareResoruceConfiguration":
                srco.data[0]=connection_setup.data[1]
                srco.data[1]=connection_setup.data[2]
                srco.data[2]=connection_setup.data[3]
                srco.data[3]=connection_setup.data[4]
                srco.data[4]=connection_setup.data[5]
                srco.setValue()
                connection_setup.c.send("Soft rescource value set".encode('utf-8'))
            if connection_setup.data[0]=="Close Connection":
                connection_setup.c.send("Connection Closed".encode('utf-8'))
                time.sleep(2)
                connection_setup.c.close()
                connection_setup.s.close()
                connection_setup.condition=False

