import logging
import random
import pyGPGO

from .base_optimizer import BaseOptimizer

logger = logging.getLogger(__name__)


from collections import OrderedDict

import numpy as np
from joblib import Parallel, delayed
from scipy.optimize import minimize


class BayesianOptimizer(BaseOptimizer):
    def __init__(self, surrogate='', acquisition='', parameter_dict='', storage='', n_iter=10, n_jobs=1):
        """
        Bayesian Optimization class.
        Parameters
        ----------
        Surrogate: Surrogate model instance
            Gaussian Process surrogate model instance.
        Acquisition: Acquisition instance
            Acquisition instance.
        parameter_dict: dict
            Dictionary specifying parameter, their type and bounds.
        n_jobs: int. Default 1
            Parallel threads to use during acquisition optimization.
        storage: where to store 
        n_iter: number of iteration
        Attributes
        ----------
        parameter_key: list
            Parameters to consider in optimization
        parameter_type: list
            Parameter types.
        parameter_range: list
            Parameter bounds during optimization
        history: list
            Target values evaluated along the procedure.
        """

        self.surrogate = surrogate
        self.A = acquisition
        self.parameters = parameter_dict
        self.n_jobs = n_jobs
        self.storage = storage
        self.fitted = False
        self.n_iter = n_iter

        # param = {'a': ('cont', [0, 1]), 'b': ('cont', [0, 1])}
        self.parameter_key = list(parameter_dict.keys())
        self.parameter_value = list(parameter_dict.values())
        self.parameter_type = [p[0] for p in self.parameter_value]
        self.parameter_range = [p[1] for p in self.parameter_value]

        self.history = []


    def list2param(self, param_list):
        """
        transform a list of parameters into param format, {'a':1, 'b':2}
        -------
        param_list:
            a tmp_X, a list of configurations
        """
        res = []
        for config in param_list:
            param = {}
            for idx, key in enumerate(self.parameter_key):
                param[key] = config[idx]
            res.append(param)
        return res


    def _sampleParam(self):
        """
        Randomly samples parameters over bounds.
        Returns
        -------
        dict:
            A random sample of specified parameters.
        """
        d = OrderedDict()
        for index, param in enumerate(self.parameter_key):
            if self.parameter_type[index] == 'int':
                d[param] = np.random.randint(
                    self.parameter_range[index][0], self.parameter_range[index][1])
            elif self.parameter_type[index] == 'cont':
                d[param] = np.random.uniform(
                    self.parameter_range[index][0], self.parameter_range[index][1])
            elif self.parameter_type[index] == 'list':
                d[param] = random.choice(self.parameter_range[index])
            else:
                raise ValueError('Unsupported variable type.')
        return d


    def _acqWrapper(self, xnew):
        """
        Evaluates the acquisition function on a point.
        Parameters
        ----------
        xnew: np.ndarray, shape=((len(self.parameter_key),))
            Point to evaluate the acquisition function on.
        Returns
        -------
        float
            Acquisition function value for `xnew`.
        """
        new_mean, new_var = self.surrogate.predict(xnew, return_std=True)
        new_std = np.sqrt(new_var + 1e-6)
        return -self.A.eval(self.tau, new_mean, new_std)


    def _optimizeAcq(self, method='L-BFGS-B', n_start=100):
        """
        Optimizes the acquisition function using a multistart approach.
        Parameters
        ----------
        method: str. Default 'L-BFGS-B'.
            Any `scipy.optimize` method that admits bounds and gradients. Default is 'L-BFGS-B'.
        n_start: int.
            Number of starting points for the optimization procedure. Default is 100.
        """
        start_points_dict = [self._sampleParam() for i in range(n_start)]
        start_points_arr = np.array([list(s.values())
                                     for s in start_points_dict])
        x_best = np.empty((n_start, len(self.parameter_key)))
        f_best = np.empty((n_start,))
        if self.n_jobs == 1:
            for index, start_point in enumerate(start_points_arr):
                res = minimize(self._acqWrapper, x0=start_point, method=method,
                               bounds=self.parameter_range)
                x_best[index], f_best[index] = res.x, np.atleast_1d(res.fun)[0]
        else:
            opt = Parallel(n_jobs=self.n_jobs)(delayed(minimize)(self._acqWrapper, x0=start_point, method=method, bounds=self.parameter_range) for start_point in start_points_arr)
            x_best = np.array([res.x for res in opt])
            f_best = np.array([np.atleast_1d(res.fun)[0] for res in opt])

        self.best = x_best[np.argmin(f_best)]


    def getResult(self):
        """
        Prints best result in the Bayesian Optimization procedure.
        Returns
        -------
        OrderedDict
            Point yielding best evaluation in the procedure.
        float
            Best function evaluation.
        """
        argtau = np.argmax(self.surrogate.y)
        opt_x = self.surrogate.X[argtau]
        res_d = OrderedDict()
        for i, (key, param_type) in enumerate(zip(self.parameter_key, self.parameter_type)):
            if param_type == 'int':
                res_d[key] = int(opt_x[i])
            else:
                res_d[key] = opt_x[i]
        return res_d, self.tau


    def suggest(self, n_eval=3):
        """
        Suggest evaluations. For initial evaluations, randomly select n_eval points to evaluate. For others, suggest one point to evaluate.
        Parameters
        ----------
        n_eval: int
            Number of initial evaluations to perform. Default is 3.
        """

        if not self.fitted: # at the beginning, randomly select several points
            tmp_X = np.empty((n_eval, len(self.parameter_key)))
            for i in range(n_eval):
                s_param = self._sampleParam()
                s_param_val = list(s_param.values())
                tmp_X[i] = s_param_val
        else:
            # update the optimizer
            self._optimizeAcq()
            tmp_X = np.array([self.best])
        # self.logger._printInit(self)

        return tmp_X, self.list2param(tmp_X)


    def update(self, tmp_X, tmp_y):
        """
        update the model with new samples.

        Parameters
        ----------
        prev_X: list of list
            list of set of parameters (list of configurations) in the order of parameter_key
        prev_y: list
            list of values(the target function values) for configurations
        """
        if not self.fitted:
            self.X = tmp_X
            self.y = tmp_y
            self.surrogate.fit(self.X, self.y)
            self.tau = np.max(self.y)
            self.fitted = True
        else:
            self.X = np.concatenate((self.X, tmp_X))
            self.y = np.concatenate((self.y, tmp_y))
            self.surrogate.update(np.atleast_2d(self.best), np.atleast_1d(tmp_y))
            self.tau = np.max(self.surrogate.y)
        
        self.history.append(self.tau)
        # self.logger._printInit(self)
    