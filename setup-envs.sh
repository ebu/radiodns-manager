#!/usr/bin/env bash

# installing tests
cd tests &&
virtualenv --python=/usr/local/bin/python3.7 venv &&
source venv/bin/activate &&
pip install . &&
deactivate &&

# installing RadioDns-PlugIt
cd ../RadioDns-PlugIt/ &&
virtualenv --python=/usr/bin/python2.7 venv &&
source venv/bin/activate &&
pip install . &&
deactivate &&

# installing standalone proxy
cd ../standalone_proxy &&
virtualenv --python=/usr/bin/python2.7 venv &&
source venv/bin/activate &&
pip install -r pip_requirements.txt &&
deactivate &&

# installing mockAPI
cd ../MockApi &&
virtualenv --python=/usr/local/bin/python3.7 venv &&
source venv/bin/activate &&
pip install . &&
deactivate
