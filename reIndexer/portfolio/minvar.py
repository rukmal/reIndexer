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
        self.optim_constraints = [
            {
                'type': 'ineq',
                'fun': lambda x: np.sum([-1 if i < 0 else 0 for i in x])
            },
            {
                'type': 'eq',
                'fun': lambda x: np.sum(x) - 1
            }
        ]

    def computeWeights(self, log_rets: np.ndarray, prev_weights: np.array=None)\
        -> np.array:
        # Computing covariance matrix
        cov_mat = np.cov(log_rets)

        # Defining objective function for optimization
        objective = lambda x: np.matmul(x, np.matmul(cov_mat, x))

        # Initial guess; previous weights if available, if not equal weight
        if not prev_weights:
            prev_weights = np.full(
                shape=cov_mat.shape[0],
                fill_value=1 / cov_mat.shape[0]
            )

        # Run optimization
        port_weights = minimize(
            fun=objective,
            x0=np.full(11, 0),
            constraints=self.optim_constraints
        )

        logging.debug('Computed minvar weights {0}'.format(port_weights.x))

        return port_weights.x
