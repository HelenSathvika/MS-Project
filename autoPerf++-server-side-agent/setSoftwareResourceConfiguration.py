import subprocess
import re
import time
import os

class setSoftwareResourceConfiguration:
    data=["path","regExp","value","command","sleep_time"]
    getData=[]

    def setValue(self):
        command=['sudo', '-S', 'cat', self.data[0]]
        result = subprocess.run(command, input="adi1506", stdout=subprocess.PIPE, text=True)
        file_content=result.stdout
        modified_content=re.sub(rf'{self.data[1]}', rf'\g<1>{self.data[2]}', file_content)
        command = ['sudo', '-S', 'tee', self.data[0]]
        process = subprocess.Popen(command, stdin=subprocess.PIPE, stdout=subprocess.PIPE, text=True)
        process.communicate(input=modified_content)
        process.wait()
        os.system(self.data[3])
        time.sleep(self.data[4])
