import subprocess
import re
import time
import os

class SetSoftResourceConfiguration:
    data=["path","regExp","value","command","sleep_time"]
    getData=[]
    password=""

    def setValue(self): #Set Value
        command=['sudo', '-S', 'cat', self.data[0]]
        result = subprocess.run(command, input=self.password, stdout=subprocess.PIPE, text=True) #Read the file content
        file_content=result.stdout
        modified_content=re.sub(rf'{self.data[1]}', rf'\g<1>{self.data[2]}', file_content) #Modify the Value
        command = ['sudo', '-S', 'tee', self.data[0]]
        process = subprocess.Popen(command, stdin=subprocess.PIPE, stdout=subprocess.PIPE, text=True) #Rewrite the file content with the modified value
        process.communicate(input=modified_content)
        process.wait()
        os.system(self.data[3]) #Execute the command
        time.sleep(self.data[4]) #Wait for the changes 
