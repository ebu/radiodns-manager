import os

DEBUG = "True" == os.environ.get('DEBUG', 'True')

MOCK_API_HOST = os.environ.get('MOCK_API_HOST', '0.0.0.0')
MOCK_API_PORT = int(os.environ.get('MOCK_API_PORT', '8000'))
