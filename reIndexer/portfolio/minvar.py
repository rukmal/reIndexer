from scipy.optimize import minimize
import logging
import numpy as np


class MinimumVariance():
    def __init__(self):
        pass

        self.optim_constraints = [
            {
                'type': 'ineq',
                'ineq': lambda x: all((i >= 0) for i in x)
            }
        ]

    def computeWeights(self, log_rets: np.ndarray) -> np.array:
        pass
        # cov_mat = 
        # optim_func = lambda x: np.dot(log_ret, np.dot(cov_mat, log_ret))
