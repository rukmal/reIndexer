from ..cfg import config

from scipy.optimize import minimize
import logging
import numpy as np


class MinimumVariance():

    def __init__(self):
        # See: http://bit.ly/2IzJWE0 and http://bit.ly/2IPlTQP for more on this
        # NOTE: Equality constraints are tested to be equal to zero, so the sum
        #       of the weights - 1 must be 0
        # NOTE: (to self) Spent HOURS on this; the constraints were fucked up
        #       with list comprehensions. Constraint functions will not work
        #       with list comprehensions, because of Python's Late Binding
        #       closures. See: http://bit.ly/2KWxhwW
        self.optim_constraints = (
            {
                'type': 'eq',
                'fun': lambda x: np.sum(x) - 1
            }
        )

        # Bounds do not allow flr
        self.bounds_base = ((0, 1),)

    def computeWeights(self, log_rets: np.ndarray, prev_weights: np.array=None)\
        -> np.array:
        # Computing covariance matrix
        cov_mat = np.cov(log_rets) * config.setf_lookback_window

        # Defining objective function for optimization
        def objective(x: np.array) -> float:
            return np.dot(x.T, np.dot(cov_mat, x))

        # Initial guess; previous weights if available, if not random weights
        if not prev_weights:
            prev_weights = np.random.dirichlet(np.ones(cov_mat.shape[0]), 1)[0]

        logging.debug('Optimizing with initial weights {0}'.
            format(prev_weights))

        # Run optimization
        port_weights = minimize(
            fun=objective,
            x0=prev_weights,
            constraints=self.optim_constraints,
            options={
                'maxiter': 1e4,
            },
            bounds=self.bounds_base * cov_mat.shape[0],
            tol=config.optim_tol
        )

        logging.debug('Computed minvar weights {0}'.format(port_weights.x))

        return port_weights.x
