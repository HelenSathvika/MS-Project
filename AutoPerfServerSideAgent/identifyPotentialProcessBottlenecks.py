import time
import datetime
from datetime import datetime
import os
import subprocess
import time
from multiprocessing import Pool
import json
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import functools
import threading
import psutil

class identifyPotentialProcessBottlenecks:

    process_names=[]
    load_test_folder=""
    input_conf={}
    test_duration=0
    pids_workers={} #Store child worker PIDs of each process
    pids_threads={} #Store thread TDs of each process

    def start(self,event,process_names,test_duration):
        self.process_names=process_names
        self.test_duration=test_duration
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        if self.load_test_folder=="":
            self.load_test_folder = "/home/perf/autoperfsbserver/potential_bottlenecks_outputs"+"/"+"loadTesting_"+timestamp
            os.makedirs(self.load_test_folder)

        with open("/home/perf/autoperfsbserver/input_conf.json",'rb') as file:
            input_conf_content=file.read()
        input_conf_json_content=input_conf_content.decode('utf-8')
        self.input_conf=json.loads(input_conf_json_content)

        self.captureData(event)

    def getthreads(self,pid): #Get thread id's of parent process id

        if pid in self.pids_threads:
            return self.pids_threads[pid]

        try:
            process = psutil.Process(pid) #Using psutil library capture thread id's
            threads = process.threads()
            thread_ids = [thread.id for thread in threads]
            self.pids_threads[pid]=thread_ids
            return thread_ids
        except psutil.NoSuchProcess:
            print(f"No process found with PID {pid}.")
            self.pids_threads[pid]=[]
            return []
        except Exception as e:
            print(f"Error fetching thread IDs for PID {pid}: {e}")
            self.pids_threads[pid]=[]
            return []

    def getWorkerProcesses(self, pid): #Get worker process id's of parent process id

        if pid in self.pids_workers:
            return self.pids_workers[pid]
        try:
            command = f"ps --ppid {pid} -o pid --no-headers" #
            worker_pids = subprocess.check_output(command, shell=True).decode().split()
            worker_pids = [int(pid.strip()) for pid in worker_pids if pid.strip().isdigit()]
            self.pids_workers[pid]=worker_pids
            return worker_pids
        except Exception as e:
            print(f"Error while fetching worker processes for PID {pid}: {e}")
            worker_pids = []
            self.pids_workers[pid]=worker_pids
            return worker_pids
    
    #Capture strace output for a single process/thread
    def captureStrace(self,pid,temp_load_test_folder):

        if not os.path.exists(f"/proc/{pid}"):
            print(f"Process with PID {pid} does not exist.")
            return

        #Store Strace output for each pid in different file
        output_file = os.path.join(temp_load_test_folder, f"{pid}.strace")
        print(f"Capturing strace for PID {pid} for {self.test_duration} seconds...")

        #Run strace with sudo and a timeout(test duration)
        command = f"echo {self.input_conf["system_password"]} | sudo -S timeout {self.test_duration} strace -p {pid} -o {output_file}"
    
        try:
            result = subprocess.run(command, shell=True, check=True, timeout=self.test_duration + 5)
            print(f"Finished capturing strace for PID {pid}. Exit code: {result.returncode}")
        except subprocess.TimeoutExpired:
            print(f"Timeout expired for PID {pid}.")
        except subprocess.CalledProcessError as e:
            print(f"Failed to capture strace for PID {pid}: {e}")
        except Exception as e:
            print(f"Unexpected error for PID {pid}: {e}")

    # Captures straces for all processes (threads+worker processes)
    def captureData(self,event): #Capture data
        temp_load_test_folder=self.load_test_folder
        temp_load_test_folder=temp_load_test_folder+"/"+event
        os.makedirs(temp_load_test_folder, exist_ok=True)

        all_pids = set()
        for pid in self.process_names: #Collect worker process ids and thread ids of the parent id
            all_pids.add(pid)
            all_pids.update(self.getWorkerProcesses(pid))
            all_pids.update(self.getthreads(pid))

        #Prepare arguments to capture straces for all pids in parallel
        args=[(pid,temp_load_test_folder) for pid in all_pids]

        #Multiprocessing to capture strace in parallel
        capture_strace_func = functools.partial(self.captureStrace) #Start capturing strace for each thread

        with Pool(len(args)) as pool: 
            pool.starmap(capture_strace_func, args)
    
    #Chunk text into overlapping segments
    def chunk_text(self, text, chunk_size=500, overlap=100):
        words = text.split()
        chunks = []
        i = 0
        while i < len(words):
            chunks.append(' '.join(words[i:i + chunk_size]))
            i += chunk_size - overlap  
        return chunks

    # Sfely read a log file
    def read_log_file(self, filename):
        try:
            with open(filename, 'r', encoding='utf-8') as file:
                return file.read()
        except Exception as e:
            print(f"Error reading file {filename}: {e}")
            return ""

    #Compare two strace logs of process (load vs. no-load)
    def similarityCheck(self, process_id):
        load_folder = os.path.join(self.load_test_folder, "Load")
        noload_folder = os.path.join(self.load_test_folder, "noLoad")
        load_file_path = os.path.join(load_folder, f"{process_id}.strace")
        noload_file_path = os.path.join(noload_folder, f"{process_id}.strace")

        if not (os.path.exists(load_file_path) and os.path.exists(noload_file_path)):
            print(f"Missing strace file for process {process_id}")
            return 0.0 

        A = self.read_log_file(load_file_path)
        B = self.read_log_file(noload_file_path)

        if not A.strip() or not B.strip():
            print(f"Empty log file detected for process {process_id}")
            return 0.0  

        chunks_A = self.chunk_text(A)
        chunks_B = self.chunk_text(B)
        
        if not chunks_A or not chunks_B:
            print(f"Insufficient data for TF-IDF for process {process_id}")
            return 0.0

        all_chunks = chunks_A + chunks_B
        vectorizer = TfidfVectorizer()
        vectors = vectorizer.fit_transform(all_chunks)
 
        #Compare chunks using cosine similarity 
        num_chunks = min(len(chunks_A), len(chunks_B))
        similarities = []

        for i in range(num_chunks):
            sim = cosine_similarity(
                vectors[i], vectors[len(chunks_A) + i]
            )[0][0]
            similarities.append(sim)

        return sum(similarities) / len(similarities) if similarities else 0.0

    #Run similarity analysis for all parent ids
    def calculateProcessSimilarity(self):
        process_similarities = {}
        load_folder = os.path.join(self.load_test_folder, "Load")
        noload_folder = os.path.join(self.load_test_folder, "noLoad")

        for pid in self.process_names:
            all_pids = [pid] + self.pids_workers[pid] + self.pids_threads[pid]
            similarities = []

            for process_id in all_pids:
                load_log_file = os.path.join(load_folder, f"{process_id}.strace")
                noload_log_file = os.path.join(noload_folder, f"{process_id}.strace")

                if os.path.exists(load_log_file) and os.path.exists(noload_log_file):
                    similarity = self.similarityCheck(process_id) #Capture similatiry score for each thread id or worker process id
                    similarities.append(similarity)

            if similarities: #Average the similairity as one process thread pool
                process_similarities[pid] = sum(similarities) / len(similarities)
            else:
                print(f"No similarity data available for process {pid} and its workers.")

        return process_similarities #Return similarity
