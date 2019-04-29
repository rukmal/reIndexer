import os
import sys

try:
    import reIndexer
except ImportError:
    sys.path.insert(0, os.path.abspath('../'))
    os.chdir(os.path.abspath('../'))
    import reIndexer
