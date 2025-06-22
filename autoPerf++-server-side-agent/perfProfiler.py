import psutil
import time
import threading
import subprocess
import re
import concurrent.futures
import os
import json

class perfProfiler:

    process_names=[]
    process_perf_resource_usage={}
    application_perf_resource_usage={}
    perf_monitoring_flag=""
    input_conf={}
    password=""

    def start(self,process_names):
        self.process_names=process_names
        self.perf_monitoring_flag=True
        for process_name in process_names:
            self.process_perf_resource_usage[process_name]={"LLC-loads":0,"LLC-load-misses":0,"LLC-stores":0,"LLC-store-misses":0}
        self.application_perf_resource_usage={"LLC-loads":0,"LLC-load-misses":0,"LLC-stores":0,"LLC-store-misses":0}

        threading.Thread(target=self.perfMetrics, daemon=True).start() #Start sepearte thread to capture cache resource usage

    def getApplicationResourceUsage(self):
        return self.application_perf_resource_usage

    def getprocessResourceUsage(self):
        return self.process_perf_resource_usage

    def stop(self):
        self.perf_monitoring_flag=False
        time.sleep(60)

    def run_perf_command_for_pid(self, pid_name):

        pid=0
        for proc in psutil.process_iter(attrs=['pid', 'name']):
            if proc.info['name'] == pid_name:
                pid=proc.info['pid']
                break

        #Capture cache misses for its sub process and process
        command = (
            f'echo "{self.password}" | sudo -S perf stat '
            f'-p $(pgrep -d, -P {pid}),{pid} '
            f'-e LLC-loads,LLC-load-misses,LLC-stores,LLC-store-misses '
            f'sleep 10'
        )

        output_file = f'output_{pid}.txt'
        with open(output_file, 'w') as f:
            subprocess.run(command, shell=True, stdout=f, stderr=subprocess.STDOUT)

        return output_file

    def run_perf_command_for_system(self):

        #Capture cache misses for entire system
        command = (
            f'echo "{self.password}" | sudo -S perf stat '
            f'-e cpu_core/LLC-loads/,cpu_core/LLC-load-misses/,cpu_core/LLC-stores/,cpu_core/LLC-store-misses/ '
            f'-a sleep 10'
        )

        output_file = 'system_output.txt'
        with open(output_file, 'w') as f:
            subprocess.run(command, shell=True, stdout=f, stderr=subprocess.STDOUT)
        return output_file

    def process_output(self, file_path): #Parse the output file to extract the metrics

        results = {"LLC-loads": 0,"LLC-load-misses": 0,"LLC-stores": 0,"LLC-store-misses": 0,"time_elapsed": 0}
        with open(file_path, 'r') as f:
            output = f.read()
            for line in output.splitlines():
                for event in results.keys():
                    if event != "time_elapsed" and event in line:
                        try:
                            value = int(line.split()[0].replace(',', ''))
                            results[event] += value
                        except ValueError:
                            pass
                time_pattern = r'(\d*\.?\d+)\s+seconds\s+time\s+elapsed'
                time_match = re.search(time_pattern, output)
                if time_match:
                    results['time_elapsed'] = float(time_match.group(1))
        return results

    def run_parallel_perf_commands(self): 
        with concurrent.futures.ThreadPoolExecutor() as executor: # Use a thread pool to concurrently run perf commands for each process and for the system
            future_to_pid = {executor.submit(self.run_perf_command_for_pid, pid): pid for pid in self.process_names}  # Submit a perf task for each process ID in self.process_names and Store the Future object mapped to its corresponding PID
            future_system = executor.submit(self.run_perf_command_for_system) # Submit a separate perf task for capturing system-wide performance metrics

            # Process results as soon as any of the futures (PID-based or system-wide) completes
            for future in concurrent.futures.as_completed(list(future_to_pid.keys()) + [future_system]):
                if future in future_to_pid: # If the completed future is one of the per-process perf tasks
                    pid = future_to_pid[future] # Get the associated PID
                    try:
                        output_file = future.result() # Get the output file produced by the perf command
                        metrics = self.process_output(output_file) # Parse the metrics from the output
                        for key, value in metrics.items(): # Accumulate all metrics (except 'time_elapsed') for this PID
                            if key != 'time_elapsed':
                                self.process_perf_resource_usage[pid][key] += value
                        os.remove(output_file) # Clean up the output file
                    except Exception as e:
                        print(f"Error processing PID {pid}: {e}")
                elif future == future_system: # If the completed future is the system-wide perf task
                    try:
                        system_output_file = future_system.result() # Get the system-wide output file
                        system_metrics = self.process_output(system_output_file) # Parse the system-wide metrics
                        for key, value in system_metrics.items(): # Accumulate system-wide metrics (except 'time_elapsed')
                            if key != 'time_elapsed':
                                self.application_perf_resource_usage[key] += value
                        os.remove(system_output_file)
                    except Exception as e:
                        print(f"Error processing system-wide metrics: {e}")

    def perfMetrics(self): #Start capturing
        while self.perf_monitoring_flag:
            self.run_parallel_perf_commands()

    
