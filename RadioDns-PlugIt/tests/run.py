import os
import sys

import pytest

os.chdir("../")
sys.path.append(os.getcwd() + "../venv/lib/python2.7/site-packages")
os.chdir(os.getcwd() + "/tests/")

exit(pytest.main(['./']))
