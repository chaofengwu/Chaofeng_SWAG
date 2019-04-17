import os

import paropt
from paropt.runner import ParslRunner
from paropt.storage import LocalFile
from paropt.optimizer import bayesian_optimizer
from paropt.optimizer import GridSearch
from paropt.runner.parsl import timeCmd
from paropt.runner.parsl import local_config

import numpy as np
import pyGPGO
from pyGPGO.covfunc import matern32
from pyGPGO.acquisition import Acquisition
from pyGPGO.surrogates.GaussianProcess import GaussianProcess
from pyGPGO.GPGO import GPGO

# log events to console for debugging
paropt.setConsoleLogger()

# experiment configuration
tool = {
  'name': 'faketool',
  'version': '1.2.3'
}
# path to our bash file
script_path = f'{os.path.dirname(os.path.realpath(__file__))}/echoTemplate.sh'
# parameters we want to optimize
command_params = {
  "parameterA": [0, 5],
  "parameterB": [0, 5]
}
experiment = {
  'id': 1234,
  'tool': tool,
  'parameters': command_params,
  'script_template_path': script_path
}

# storage for results
file_storage = LocalFile('testFile.txt')

# optimizer
cov = matern32()
gp = GaussianProcess(cov)
acq = Acquisition(mode='ExpectedImprovement')
param = {'a': ('cont', [0, 1]),
         'b': ('cont', [0, 1])}
n_iter = 10

opt = bayesian_optimizer.BayesianOptimizer(gp, acq, param, storage=file_storage, n_iter=n_iter)
# bayesian_optimizer = BayesianOptimizer(
#   command_params,
#   n_init=2,
#   n_iter=3,
#   storage=file_storage
# )

# runner
po = ParslRunner(experiment, local_config, timeCmd, opt, file_storage)

# start the optimization
po.run()