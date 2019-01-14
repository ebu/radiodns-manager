#!/usr/bin/env bash

# installing tests
cd tests &&
virtualenv --python=$(which python3) venv &&
source venv/bin/activate &&
pip install . &&
deactivate &&

# installing RadioDns-PlugIt
cd ../RadioDns-PlugIt/ &&
virtualenv --python=$(which python2) venv &&
source venv/bin/activate &&
pip install . &&
deactivate &&

# installing standalone proxy
cd ../standalone_proxy &&
virtualenv --python=$(which python2) venv &&
source venv/bin/activate &&
pip install -r pip_requirements.txt &&
deactivate &&

# installing mockAPI
cd ../MockApi &&
virtualenv --python=$(which python3) venv &&
source venv/bin/activate &&
pip install . &&
deactivate
