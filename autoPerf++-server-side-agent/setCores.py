import os
import psutil

class setCores:
    data=["value"]
    total_cores = os.cpu_count()
    onlineCPUs=len(psutil.Process(os.getpid()).cpu_affinity())

    def setValue(self):
        for i in range(1,int(self.data[0])):
            path="/sys/devices/system/cpu/cpu"+str(i)+"/online"
            command = f'echo "adi1506" | sudo -S bash -c "echo 1 > {path}"'
            os.system(command)
        for i in range(int(self.data[0]),self.total_cores+1): 
            path="/sys/devices/system/cpu/cpu"+str(i)+"/online"
            command = f'echo "adi1506" | sudo -S bash -c "echo 0 > {path}"'
            os.system(command)
        self.onlineCPUs=len(psutil.Process(os.getpid()).cpu_affinity())

