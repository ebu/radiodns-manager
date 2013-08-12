import unittest
from nose.tools import *
import psutil, subprocess
import time
import socket
import uuid

class Main():
    """Utils to do test"""

    def __init__(self):
        """Initlialzse values"""
        self.incomingData = ''

    def tcp_connect(self):
        self.socket = socket.socket()
        self.socket.connect(('127.0.0.1', 61424))

    def get_frame(self):
        """Get one stomp frame"""
        
        while not "\x00" in self.incomingData:
            data = self.socket.recv(1024)
            if data is None or data == '':
               raise Exception("Socket seem closed.")
            else:
               self.incomingData += data

        # Get only one frame
        splited_data = self.incomingData.split('\x00', 1)

        # Save the rest for later
        self.incomingData = splited_data[1]

        # Get command, headers and body
        frame_splited = splited_data[0].split('\n')

        command = frame_splited[0]

        headers = []
        body = ""
        headerMode = True

        for x in frame_splited[1:]:
            if x == '' and headerMode:  # Switch from headers to body
                headerMode = False
            elif headerMode:  # Add header to the lsit 
                key, value = x.split(':', 1)
                headers.append((key, value))
            else:  # Compute the body
                body += x + '\n'

        # Remove last '\n'
        body = body[:-1]

        # Return everything
        return (command, headers, body)

    def send_frame(self, command, headers, body):
        """Send a frame to the SERVER"""
        self.socket.send(command + '\n')
        for (header, value) in headers:
            self.socket.send(header + ':' + value + '\n')

        self.socket.send('\n')

        self.socket.send(body)

        self.socket.send('\x00')

    def send_connect(self, args):
        self.send_frame('CONNECT', args, '')


    def __del__(self):
        """Delete the socket when we're done"""
        try:
            self.socket.close()
        except:
            pass

class MainTests(unittest.TestCase):

    @classmethod
    def setup_class(cls):
        """Setup the testcase"""
        cls.subp = subprocess.Popen('python server.py --test')
        cls.proc = psutil.Process(cls.subp.pid)
        time.sleep(2)

    @classmethod
    def teardown_class(cls):
        """Shutdown the testcase"""
        cls.proc.kill()

    def test_tcp_cox_stomp(self):
        """Test the tcp connection to the stomp server"""
        m = Main()
        m.tcp_connect()

    @timed(2)
    def test_cox_stomp_with_nothing(self):
        """Test the connection to the stomp server with no parameters"""
        m = Main()
        m.tcp_connect()
        m.send_connect({})
        (result, headers, body) = m.get_frame()
        eq_(result, 'CONNECTED')

    @timed(2)
    def test_cox_stomp_send_session(self):
        """Test if the connection to the stomp server send a session"""
        m = Main()
        m.tcp_connect()
        m.send_connect({})
        (result, headers, body) = m.get_frame()
        for (name, value) in headers:
            if name == 'session':
                return
        raise Exception('No session')

    @timed(2)
    def test_cox_stomp_send_response_id(self):
        """Test if the connection to the stomp server send back response_id"""
        m = Main()
        m.tcp_connect()
        tmpId = str(uuid.uuid4())
        m.send_connect([('request-id', tmpId)])
        (result, headers, body) = m.get_frame()
        for (name, value) in headers:
            if name == 'response-id':
                eq_(value, tmpId)
                return
        raise Exception('No response-id')

    @timed(2)
    def test_cox_stomp_send_receipt_id(self):
        """Test if the connection to the stomp server send back receipt_id"""
        m = Main()
        m.tcp_connect()
        tmpId = str(uuid.uuid4())
        m.send_connect([('receipt', tmpId)])
        (result, headers, body) = m.get_frame()
        for (name, value) in headers:
            if name == 'receipt-id':
                eq_(value, tmpId)
                return
        raise Exception('No receipt-id')

    @timed(2)
    def test_cox_stomp_with_emptypassword(self):
        """Test the connection to the stomp server with an empty password"""
        m = Main()
        m.tcp_connect()
        m.send_connect([('login', ''), ('passcode', '')])
        (result, headers, body) = m.get_frame()
        eq_(result, 'CONNECTED')

    @timed(2)
    def test_cox_stomp_with_goodpassword(self):
        """Test the connection to the stomp server with a good password"""
        m = Main()
        m.tcp_connect()
        m.send_connect([('login', 'test'), ('passcode', 'test')])
        (result, headers, body) = m.get_frame()
        eq_(result, 'CONNECTED')

    @timed(2)
    def test_cox_stomp_with_wrongpassword(self):
        """Test the connection to the stomp server with a wrong password"""
        m = Main()
        m.tcp_connect()
        m.send_connect([('login', 'test'), ('passcode', 'wrong')])
        (result, headers, body) = m.get_frame()
        eq_(result, 'ERROR')

    @timed(2)
    def test_cox_stomp_with_goodip(self):
        """Test the connection to the stomp server with a good ip"""
        m = Main()
        m.tcp_connect()
        m.send_connect([('login', 'testip'), ('passcode', '127.0.0.1')])
        (result, headers, body) = m.get_frame()
        eq_(result, 'CONNECTED')

    @timed(2)
    def test_cox_stomp_with_wrongip(self):
        """Test the connection to the stomp server with a wrong ip"""
        m = Main()
        m.tcp_connect()
        m.send_connect([('login', 'testip'), ('passcode', '0.0.0.0')])
        (result, headers, body) = m.get_frame()
        eq_(result, 'ERROR')

    @raises(Exception)  # Test must fail :)
    @timed(2)
    def test_stomp_randomcommand(self):
        """Test  if the server dosen't reply to an unknow commnad"""
        m = Main()
        m.tcp_connect()
        m.send_connect({})
        m.get_frame()  # Connected frame
        m.send_frame('_THIS_IS_A_TEST_', [], '')
        # Wait for a reply
        m.socket.settimeout(3)
        m.get_frame()

    @nottest
    def test_receipt(self, command):
        """Test if the server send RECEIPT for a command"""
        m = Main()
        m.tcp_connect()
        m.send_connect({})
        m.get_frame()  # Connected frame

        tmpId = str(uuid.uuid4())
        m.send_frame(command, [('receipt', tmpId)], '')
        (result, headers, body) = m.get_frame()
        eq_(result, 'RECEIPT')

        for (name, value) in headers:
            if name == 'receipt-id':
                eq_(value, tmpId)
                return
        raise Exception('No receipt-id')

    @timed(2)
    def test_stomp_randomcommand_receipt(self):
        """Test if the server send RECEIPT for any command"""
        self.test_receipt('_THIS_IS_A_TEST_')

    @timed(2)
    def test_stomp_disconnect_receipt(self):
        """Test the connection if the server send RECEIPT for DISCONNECT"""
        self.test_receipt('DISCONNECT')

    @timed(2)
    def test_stomp_subscribe_receipt(self):
        """Test the connection if the server send RECEIPT for SUBSCRIBE"""
        self.test_receipt('SUBSCRIBE')

    @timed(2)
    def test_stomp_unsubscribe_receipt(self):
        """Test the connection if the server send RECEIPT for UNSUBSCRIBE"""
        self.test_receipt('UNSUBSCRIBE')

    @timed(2)
    def test_stomp_send_receipt(self):
        """Test the connection if the server send RECEIPT for SEND"""
        self.test_receipt('SEND')
