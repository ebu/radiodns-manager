import os
import sys

import pytest

sys.path.append(os.getcwd() + "/venv/lib/python3.7/site-packages")
os.chdir(os.getcwd() + "/tests/")

exit(pytest.main(['./']))
