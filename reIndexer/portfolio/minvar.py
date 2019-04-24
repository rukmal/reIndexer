from ..cfg import config

from scipy.optimize import minimize
import logging
import numpy as np


class MinimumVariance():

    def __init__(self):
        # See: http://bit.ly/2IzJWE0 and http://bit.ly/2IPlTQP for more on this
        # NOTE: Ineq constraints are tested for negativity, so this sums
        #       to < 1 if any of the elements in the weights array are
        #       negative (i.e. no short sales)
        # NOTE: Equality constraints are tested to be equal to zero, so the sum
        #       of the weights - 1 must be 0
        # NOTE: (to self) Spent HOURS on this; the constraints were fucked up
        #       with list comprehensions. Constraint functions will not work
        #       with list comprehensions, because of Python's Late Binding
        #       closures. See: http://bit.ly/2KWxhwW
        #       Ineq constraint was:
        #       lambda x: np.sum([-1 if i < 0 else 0 for i in x]); did not work
        #       New formulation literally does the same thing
        self.optim_constraints = (
            {
                'type': 'ineq',
                'fun': lambda x: np.any(x < 0) * -1
            },
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

        # Defining constraints
        optim_constraints = (
            {
                'type': 'eq',
                'fun': lambda x: np.sum(x) - 1
            }
        )

        # Initial guess; previous weights if available, if not equal weight
        if not prev_weights:
            prev_weights = np.full(
                shape=cov_mat.shape[0],
                fill_value=1 / cov_mat.shape[0]
            )
            prev_weights = np.random.dirichlet(np.ones(cov_mat.shape[0]), 1)[0]

        logging.debug('Optimizing with initial weights {0}'.format(prev_weights))

        # Run optimization
        port_weights = minimize(
            fun=objective,
            x0=prev_weights,
            constraints=optim_constraints,
            options={
                'disp': True,
                'maxiter': 1e3,
            },
            bounds=self.bounds_base * cov_mat.shape[0],
            tol=1e-4
        )

        logging.debug('Computed minvar weights {0}'.format(port_weights.x))

        return port_weights.x
