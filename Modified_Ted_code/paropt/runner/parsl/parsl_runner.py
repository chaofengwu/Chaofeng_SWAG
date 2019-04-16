import logging
import os
import time
import traceback
from string import Template

import parsl
import numpy as np

from paropt import setFileLogger

logger = logging.getLogger(__name__)

class ParslRunner:
    def __init__(self, experiment, parsl_config, parsl_app, optimizer, storage):
        """
        experiment: a dictionary for information of the experiments, including id, tool, parameters, and script_template_path
        parsl_config: a dictionary which shows config for parsl. used in parsl.load. example of local config in runner/parsl/config.py
        parsl_app: an user defined application. example is in runner/parsl/lib.py
        optimizer: optimization methods. in optimizer/
        storage: where to store the results.
        """
        
        self.experiment = experiment
        self.parsl_config = parsl_config
        self.parsl_app = parsl_app
        self.script_template_path = experiment['script_template_path']
        with open(self.script_template_path, 'r') as f:
            self.command = f.read()
        self.optimizer = optimizer
        self.storage = storage

        # setup paropt info directories
        self.paropt_dir = f'./optinfo'
        if not os.path.exists(self.paropt_dir):
            os.mkdir(self.paropt_dir)

        run_number = 0
        run_dir = f'{self.paropt_dir}/{run_number:03}'
        while os.path.exists(run_dir):
            run_number += 1
            run_dir = f'{self.paropt_dir}/{run_number:03}'
        self.run_dir = run_dir
        os.mkdir(self.run_dir)

        self.templated_scripts_dir = f'{self.run_dir}/templated_scripts'
        os.mkdir(self.templated_scripts_dir)

        setFileLogger(f'{self.run_dir}/paropt.log')

    def _validateResult(self, params, res):
        pass
        # if process.returncode != 0:
        #     raise CalledProcessError(process.returncode, cmd, output=output)
        # if res[0] != 0:
        #     raise Exception("NON_ZERO_EXIT:\n    PARAMS: {}\n    OUT: {}".format(params, res[1]))

    def _writeScript(self, params):
        script = Template(self.command).safe_substitute(params)
        script_path = f'{self.templated_scripts_dir}/timeScript_{self.experiment["tool"]["name"]}_{int(time.time())}.sh'
        with open(script_path, "w") as f:
            f.write(script)
        return script_path, script
    
    def run(self, debug=False):
        if debug:
            parsl.set_stream_logger()
        parsl.load(self.parsl_config)
        try:
            for i in range(self.optimizer.n_iter):
                list_configs, param_configs = self.optimizer.suggest()
                tmp_y = np.array([])

                for idx, config in enumerate(list_configs):
                    print(f'#####This is config: {param_configs[idx]}')
                    ###### TODO: add record for running time, etc.
                    logger.info(f'Writing script with config {param_configs[idx]}')
                    ###### TODO: modify writing script so that it could fit my script
                    script_path, script_content = self._writeScript(param_configs[idx])
                    logger.info(f'Running script {script_path}')
                    result = self.parsl_app(script_content).result()
                    print(f'#####THis is result: {result}')
                    self._validateResult(config, result)
                    tmp_y = np.append(tmp_y, result[-1])
                    self.storage.saveResult(config, result)
                print(f'#####This is tmp_y:')
                for i in tmp_y:
                    print(i)
                self.optimizer.update(list_configs, tmp_y)

        except Exception as e:
            logger.info('Whoops, something went wrong... {e}')
            logger.exception(traceback.format_exc())
        logger.info('Exiting program')
    
    def getMax(self):
        return self.optimizer.getResult()
