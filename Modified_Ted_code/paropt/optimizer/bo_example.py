import bayesian_optimizer

import numpy as np
import pyGPGO
from pyGPGO.covfunc import matern32
from pyGPGO.acquisition import Acquisition
from pyGPGO.surrogates.GaussianProcess import GaussianProcess
from pyGPGO.GPGO import GPGO


def f(x, y):
    # Franke's function (https://www.mathworks.com/help/curvefit/franke.html)
    one = 0.75 * np.exp(-(9 * x - 2) ** 2 / 4 - (9 * y - 2) ** 2 / 4)
    two = 0.75 * np.exp(-(9 * x + 1) ** 2/ 49 - (9 * y + 1) / 10)
    three = 0.5 * np.exp(-(9 * x - 7) ** 2 / 4 - (9 * y -3) ** 2 / 4)
    four = 0.25 * np.exp(-(9 * x - 4) ** 2 - (9 * y - 7) ** 2)
    return one + two + three - four

cov = matern32()
gp = GaussianProcess(cov)
acq = Acquisition(mode='ExpectedImprovement')
param = {'x': ('cont', [0, 1]),
         'y': ('cont', [0, 1])}
n_iter = 10
np.random.seed(1337)

def self_designed():
    np.random.seed(1337)
    opt = bayesian_optimizer.BayesianOptimizer(gp, acq, param, storage='local', n_iter=n_iter)

    for i in range(opt.n_iter):
        tmp_X = opt.suggest()
        tmp_y = np.array([])
        print(tmp_X)
        for i in tmp_X:
            kw = {par: i[j] for j, par in enumerate(param.keys())}
            tmp_y = np.append(tmp_y, f(**kw))
        # print(tmp_X.shape)
        # print(tmp_y.shape)
        opt.update(tmp_X, tmp_y)



def original():
    np.random.seed(1337)
    gpgo = GPGO(gp, acq, f, param)
    gpgo.run(max_iter=10)

original()
self_designed()