import sys
import os
import json
import LGMaster
import ProfilingAgentMaster
import AutoPerf

class AutomatedLoadTestingKit:

    auto_conf={}
    load_generator_master_obj=""


    def start(self):
        automated_configurations="input-configurations/auto-load-testing-conf.json"
        with open(automated_configurations,'rb') as file:
            auto_conf_content=file.read()
        auto_conf_json_content=auto_conf_content.decode('utf-8')
        self.auto_conf=json.loads(auto_conf_json_content)
        self.runLoadTest()

    def runLoadTest(self):
        load_generator_details=self.auto_conf['loadGeneratorDetails']
        user_session=self.auto_conf['sessionDetails']
        processes_details=self.auto_conf['processToProfileDetails']
        core_details=self.auto_conf['coresDetails']
        self.load_generator_master_obj=LGMaster.LGMaster()
        profiling_agent_master_obj=ProfilingAgentMaster.ProfilingAgentMaster()
        self.load_generator_master_obj.initialize(load_generator_details["loadGenerator"],user_session["filePath"])
        profiling_agent_master_obj.initialize(processes_details["names"])
        autoperf_obj=AutoPerf.AutoPerf()
        autoperf_obj.initialize(user_session['thinkTime'],core_details['activeCores'],self.load_generator_master_obj,profiling_agent_master_obj)
        autoperf_obj.automatedLoadTesting()



