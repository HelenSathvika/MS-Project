import os
import psutil

class setCores:
    data=["value"]
    total_cores = os.cpu_count()
    onlineCPUs=len(psutil.Process(os.getpid()).cpu_affinity())
    password=""

    def setValue(self):
        for i in range(0,int(self.data[0])):
            path="/sys/devices/system/cpu/cpu"+str(i)+"/online" #Read cores setting file enabling
            command = f'echo {self.password} | sudo -S bash -c "echo 1 > {path}"'
            os.system(command)
        for i in range(int(self.data[0]),self.total_cores+1): #Read cores settibg file disable
            path="/sys/devices/system/cpu/cpu"+str(i)+"/online"
            command = f'echo {self.password} | sudo -S bash -c "echo 0 > {path}"'
            os.system(command)
        self.onlineCPUs=len(psutil.Process(os.getpid()).cpu_affinity())
