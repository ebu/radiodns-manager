# Tests for RadioDNS
This project hosts the integration tests with automated browser testing for the RadioDns manager.

## Setup

If you successfully ran the `setup-envs.sh` script from the scripts folder you may go to 
the run section directly.

This environment supports firefox and google chrome as remote controlled headless browser.

You also need the following dependencies:
- python 3.7
- docker 18.06.1+
- virtualenv 16.0.0+
- docker-compose 1.23.2+

Next you have to setup the virtualenv:

    virtualenv --python=$(which python3) venv
    source venv/bin/activate
    
And then install the required PIP dependencies

    pip install .
    
To deactivate the running environment

    deactivate
    
You'll find in the root project a script installing every project with their dependencies.
    
This test suite assumes that you have already installed the following projects (located in the root folder of this repository) 
along with their dependencies:
- MockApi
- RadioDns-PlugIt
- LightweightPlugitProxy

## Configuration
You can set the following environment variables:

- **TEST_BROWSER**: Sets the tests browser. Can be `chrome` or `firefox`. Defaults to `chrome`.
- **HEADLESS**: If `True` the browser will run in a headless mode. If `False` you will be able to see the browser being
controlled.

## Run
First make sure you activated the correct virtual env (Ignore the deactivate error if any).

    deactivate
    source venv/bin/activate

To run the test suite run

    python run.py
    
## Marking tests dependencies
Sometimes a test is required to run before an other. In order to do
so one must use the run decorator to specify the runtime order like this:

    @pytest.mark.run(order=1)
    
The first test to run os the service provider test. The second is the station test. Theses test
populate the database for further usage.

The run(order=1) decorator should be used only to mark tests dependencies between files.
To mark dependencies in the same module (class or file) it is advised to use the

    @pytest.mark.run(before='<name_of_the_test>')
  
or the 

    @pytest.mark.run(after='<name_of_the_test>')
    
decorator.
