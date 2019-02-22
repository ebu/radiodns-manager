#!/usr/bin/env bash

# installing RadioDns-PlugIt
cd RadioDns-PlugIt/ &&
virtualenv --python=$(which python2) venv &&
source venv/bin/activate &&
pip install . &&
deactivate &&

# installing tests
cd ../tests &&
virtualenv --python=$(which python3) venv &&
source venv/bin/activate &&
pip install . &&
deactivate &&

# installing LightweightPlugitProxy
cd ../LightweightPlugitProxy &&
virtualenv --python=$(which python3) venv &&
source venv/bin/activate &&
pip install . &&
deactivate &&

# installing mockAPI
cd ../MockApi &&
virtualenv --python=$(which python3) venv &&
source venv/bin/activate &&
pip install . &&
deactivate
