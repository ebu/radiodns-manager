import unittest
from nose.tools import *
import psutil, subprocess
import time
import socket
import uuid
import config
import json


def get_header_value(headers, header):
    """Return the value of an header"""
    for (headerName, value) in headers:
        if headerName == header:
            return value
    return None


class Main():
    """Utils to do test"""

    def __init__(self):
        """Initialize values"""
        self.incomingData = ''

    def tcp_connect(self):
        self.socket = socket.socket()
        self.socket.connect(('127.0.0.1', 61424))

    def get_frame(self):
        """Get one stomp frame"""

        while not "\x00" in self.incomingData:
            data = self.socket.recv(1024)
            if not data:
                raise Exception("Socket seem closed.")
            else:
                self.incomingData += data

        # Get only one frame
        split_data = self.incomingData.split('\x00', 1)

        # Save the rest for later
        self.incomingData = split_data[1]

        # Get command, headers and body
        frame_split = split_data[0].split('\n')

        command = frame_split[0]

        headers = []
        body = ""
        headerMode = True

        for x in frame_split[1:]:
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

    def build_frame(self, command, headers, body):
        """Build a stom frame"""

        message = command + '\n'

        for (header, value) in headers:
            message += header + ':' + value + '\n'

        message += '\n'
        message += body
        message += '\x00'

        return message

    def send_frame(self, command, headers, body):
        """Send a frame to the SERVER"""
        self.socket.send(self.build_frame(command, headers, body))

    def send_connect(self, args):
        self.send_frame('CONNECT', args, '')

    def get_watchdogsocket(self):
        watchdogsock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        watchdogsock.bind(('127.0.0.1', 61422))
        return watchdogsock

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
        cls.subp = subprocess.Popen(['python2', 'server.py', '--test'])
        cls.proc = psutil.Process(cls.subp.pid)

        cls.subpWD = subprocess.Popen(['python2',  'fallback.py', '--test'])
        cls.procWD = psutil.Process(cls.subpWD.pid)

        time.sleep(2)

    @classmethod
    def teardown_class(cls):
        """Shutdown the testcase"""
        cls.proc.kill()
        cls.procWD.kill()

    def test_tcp_cox_stomp(self):
        """Test the tcp connection to the stomp server"""
        m = Main()
        m.tcp_connect()

    @nottest
    def test_bogus_frame(self, frame):
        """Generic function to test if the stomp client is able to handle a bogus frame"""
        m = Main()
        m.tcp_connect()
        m.send_connect({})
        m.get_frame()  # Cox frame

        m.socket.send(frame)

        # Server should still ack our commands
        tmpId = str(uuid.uuid4())
        m.send_frame("_TEST_NOCOMMAND", [('receipt', tmpId)], '')
        (result, headers, body) = m.get_frame()
        eq_(result, 'RECEIPT')

    @timed(2)
    def test_cox_stomp_bogus_frame_1(self):
        """Test the connection to the stomp server sending a bogus frame, with an empty command"""
        self.test_bogus_frame('\n\n\x00')

    @timed(2)
    def test_cox_stomp_bogus_frame_2(self):
        """Test the connection to the stomp server sending a bogus frame, with no headers command"""
        self.test_bogus_frame('TEST\x00')

    @timed(2)
    def test_cox_stomp_bogus_frame_3(self):
        """Test the connection to the stomp server sending a bogus frame, with an empty frame"""
        self.test_bogus_frame('\x00')

    @timed(2)
    def test_cox_no_cox_first(self):
        """Test if the sever need CONNECT first"""
        m = Main()
        m.tcp_connect()
        m.send_frame("_TEST_NOCOMMAND", [], '')
        (result, headers, body) = m.get_frame()
        eq_(result, 'ERROR')

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
        m.send_connect([('login', '1.test'), ('passcode', 'test')])
        (result, headers, body) = m.get_frame()
        eq_(result, 'CONNECTED')

    @timed(2)
    def test_cox_stomp_with_wrongpassword(self):
        """Test the connection to the stomp server with a wrong password"""
        m = Main()
        m.tcp_connect()
        m.send_connect([('login', '1.test'), ('passcode', 'wrong')])
        (result, headers, body) = m.get_frame()
        eq_(result, 'ERROR')

    @timed(2)
    def test_cox_stomp_with_goodip(self):
        """Test the connection to the stomp server with a good ip"""
        m = Main()
        m.tcp_connect()
        m.send_connect([('login', '2.testip'), ('passcode', '127.0.0.1')])
        (result, headers, body) = m.get_frame()
        eq_(result, 'CONNECTED')

    @timed(2)
    def test_cox_stomp_with_wrongip(self):
        """Test the connection to the stomp server with a wrong ip"""
        m = Main()
        m.tcp_connect()
        m.send_connect([('login', '2.testip'), ('passcode', '0.0.0.0')])
        (result, headers, body) = m.get_frame()
        eq_(result, 'ERROR')

    @raises(socket.timeout)  # Test must fail :)
    @timed(2)
    def test_stomp_randomcommand(self):
        """Test  if the server doesn't reply to an unknown command"""
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

    @raises(socket.timeout)  # Test must fail :)
    @timed(2)
    def test_send_message_auth(self):
        """Test if the server accept a send on a good topic, authentified"""
        m = Main()
        m.tcp_connect()
        m.send_connect([('login', '1.test'), ('passcode', 'test')])
        m.get_frame()  # Connected frame
        m.send_frame('SEND', [('destination', config.TEST_TOPICS[0])], 'TEST')
        # Wait for a reply
        m.socket.settimeout(3)
        m.get_frame()

    @raises(socket.timeout)  # Test must fail :)
    @timed(2)
    def test_send_message_subtopic_auth(self):
        """Test if the server accept a send on a good topic, subtopic, authentified"""
        m = Main()
        m.tcp_connect()
        m.send_connect([('login', '1.test'), ('passcode', 'test')])
        m.get_frame()  # Connected frame
        m.send_frame('SEND', [('destination', config.TEST_TOPICS[0] + 'testtingsubtopic')], 'TEST')
        # Wait for a reply
        m.socket.settimeout(3)
        m.get_frame()

    @timed(2)
    def test_send_message_unauth(self):
        """Test if the server refuse a send on a good topic, unauthentified"""
        m = Main()
        m.tcp_connect()
        m.send_connect([])
        m.get_frame()  # Connected frame
        m.send_frame('SEND', [('destination', config.TEST_TOPICS[0])], 'TEST')
        (result, headers, body) = m.get_frame()
        eq_(result, 'ERROR')

    @timed(2)
    def test_send_message_unallowd(self):
        """Test if the server refuse a send on a wrong topic, authentified"""
        m = Main()
        m.tcp_connect()
        m.send_connect([])
        m.get_frame()  # Connected frame
        m.send_frame('SEND', [('destination', '/thisisnotavalidtopic')], 'TEST')
        (result, headers, body) = m.get_frame()
        eq_(result, 'ERROR')

    @raises(socket.timeout)  # Test must fail :)
    @timed(2)
    def test_send_message_auth_to_all(self):
        """Test if the server accept a send on all topics, authentified"""
        m = Main()
        m.tcp_connect()
        m.send_connect([('login', '1.test'), ('passcode', 'test')])
        m.get_frame()  # Connected frame
        m.send_frame('SEND', [('destination', '/topic/*/')], 'TEST')
        # Wait for a reply
        m.socket.settimeout(3)
        m.get_frame()

    @timed(2)
    def test_send_message_unauth_to_all(self):
        """Test if the server refuse a send on a all topics, unauthentified"""
        m = Main()
        m.tcp_connect()
        m.send_connect([])
        m.get_frame()  # Connected frame
        m.send_frame('SEND', [('destination', '/topic/*/')], 'TEST')
        (result, headers, body) = m.get_frame()
        eq_(result, 'ERROR')

    @raises(socket.timeout)  # Test must fail :)
    @timed(2)
    def test_subscrible(self):
        """Test if the server accept a subscritpion"""
        m = Main()
        m.tcp_connect()
        m.send_connect([])
        m.get_frame()  # Connected frame
        m.send_frame('SUBSCRIBE', [('destination', config.TEST_TOPICS[0]), ('x-ebu-nofastreply', 'yes')], '')
        # Wait for a reply
        m.socket.settimeout(3)
        m.get_frame()

    @raises(socket.timeout)  # Test must fail :)
    @timed(2)
    def test_subscrible_with_id(self):
        """Test if the server accept a subscritpion with an id"""
        m = Main()
        m.tcp_connect()
        m.send_connect([])
        m.get_frame()  # Connected frame
        m.send_frame('SUBSCRIBE',
                     [('destination', config.TEST_TOPICS[0]), ('x-ebu-nofastreply', 'yes'), ('id', str(uuid.uuid4()))],
                     '')
        # Wait for a reply
        m.socket.settimeout(3)
        m.get_frame()

    @timed(2)
    def test_subscrible_without_dest(self):
        """Test if the server refuse a subscription without destination"""
        m = Main()
        m.tcp_connect()
        m.send_connect([])
        m.get_frame()  # Connected frame
        m.send_frame('SUBSCRIBE', [], '')
        (result, headers, body) = m.get_frame()
        eq_(result, 'ERROR')

    @timed(2)
    def test_subscrible_message_self(self):
        """Test if we get our message back on the same connection if we send a message"""
        m = Main()
        m.tcp_connect()
        m.send_connect([('login', '1.test'), ('passcode', 'test')])
        m.get_frame()  # Connected frame
        m.send_frame('SUBSCRIBE', [('destination', config.TEST_TOPICS[0]), ('x-ebu-nofastreply', 'yes')], '')

        msg = str(uuid.uuid4())

        m.send_frame('SEND', [('destination', config.TEST_TOPICS[0])], msg)

        (result, headers, body) = m.get_frame()
        eq_(result, 'MESSAGE')
        eq_(body, msg)
        eq_(get_header_value(headers, 'destination'), config.TEST_TOPICS[0])

    @timed(2)
    def test_subscrible_message_dual(self):
        """Test if we get our message back on the others connection if we send a message"""
        m = Main()
        m.tcp_connect()
        m.send_connect([('login', '1.test'), ('passcode', 'test')])
        m.get_frame()  # Connected frame

        m2 = Main()
        m2.tcp_connect()
        m2.send_connect([])
        m2.get_frame()  # Connected frame

        m2.send_frame('SUBSCRIBE', [('destination', config.TEST_TOPICS[0]), ('x-ebu-nofastreply', 'yes')], '')

        msg = str(uuid.uuid4())

        m.send_frame('SEND', [('destination', config.TEST_TOPICS[0])], msg)

        (result, headers, body) = m2.get_frame()
        eq_(result, 'MESSAGE')
        eq_(body, msg)
        eq_(get_header_value(headers, 'destination'), config.TEST_TOPICS[0])

    @timed(2)
    def test_message_then_subscrible(self):
        """Test if we get the last message when we subscrible"""
        m = Main()
        m.tcp_connect()
        m.send_connect([('login', '1.test'), ('passcode', 'test')])
        m.get_frame()  # Connected frame

        msg = str(uuid.uuid4())

        m.send_frame('SEND', [('destination', config.TEST_TOPICS[0])], msg)
        time.sleep(0.5)
        m.send_frame('SUBSCRIBE', [('destination', config.TEST_TOPICS[0])], '')
        (result, headers, body) = m.get_frame()
        eq_(result, 'MESSAGE')
        eq_(body, msg)
        eq_(get_header_value(headers, 'destination'), config.TEST_TOPICS[0])

    @timed(2)
    def test_message_then_subscrible_cc_to_gcc(self):
        """Test if we get the last message when we subscrible, mixing CC and GCC"""
        m = Main()
        m.tcp_connect()
        m.send_connect([('login', '3.test'), ('passcode', 'test')])
        m.get_frame()  # Connected frame

        msg = str(uuid.uuid4())

        m.send_frame('SEND', [('destination', config.TEST_ECC_TOPIC_CC)], msg)
        time.sleep(0.5)
        m.send_frame('SUBSCRIBE', [('destination', config.TEST_ECC_TOPIC_GCC)], '')
        (result, headers, body) = m.get_frame()
        eq_(result, 'MESSAGE')
        eq_(body, msg)
        eq_(get_header_value(headers, 'destination'), config.TEST_ECC_TOPIC_GCC)

    @timed(2)
    def test_message_then_subscrible_gcc_to_cc(self):
        """Test if we get the last message when we subscrible, mixing CC and GCC"""
        m = Main()
        m.tcp_connect()
        m.send_connect([('login', '3.test'), ('passcode', 'test')])
        m.get_frame()  # Connected frame

        msg = str(uuid.uuid4())

        m.send_frame('SEND', [('destination', config.TEST_ECC_TOPIC_GCC)], msg)
        time.sleep(0.5)
        m.send_frame('SUBSCRIBE', [('destination', config.TEST_ECC_TOPIC_CC)], '')
        (result, headers, body) = m.get_frame()
        eq_(result, 'MESSAGE')
        eq_(body, msg)
        eq_(get_header_value(headers, 'destination'), config.TEST_ECC_TOPIC_CC)

    @raises(socket.timeout)  # Test must fail :)
    @timed(2)
    def test_subscrible_other_message(self):
        """Test if we don't get our message back on the same connection if we send a message to a unsubscribed topic"""
        m = Main()
        m.tcp_connect()
        m.send_connect([('login', '1.test'), ('passcode', 'test')])
        m.get_frame()  # Connected frame
        m.send_frame('SUBSCRIBE', [('destination', config.TEST_TOPICS[0]), ('x-ebu-nofastreply', 'yes')], '')

        msg = str(uuid.uuid4())

        m.send_frame('SEND', [('destination', config.TEST_TOPICS[1])], msg)

        m.socket.settimeout(3)

        (result, headers, body) = m.get_frame()
        eq_(result, 'MESSAGE')
        eq_(body, msg)
        eq_(get_header_value(headers, 'destination'), config.TEST_TOPICS[0])

    @timed(2)
    def test_subscrible_message_on_all(self):
        """Test if we get message back on all topics if we send a message to /topic/*/"""
        m = Main()
        m.tcp_connect()
        m.send_connect([('login', '1.test'), ('passcode', 'test')])
        m.get_frame()  # Connected frame

        clients = {}

        for t in config.TEST_TOPICS:
            m2 = Main()
            m2.tcp_connect()
            m2.send_connect([])
            m2.get_frame()  # Connected frame
            m2.send_frame('SUBSCRIBE', [('destination', t), ('x-ebu-nofastreply', 'yes')], '')

            clients[t] = m2

        msg = str(uuid.uuid4())
        m.send_frame('SEND', [('destination', '/topic/*/')], msg)

        for t in config.TEST_TOPICS:
            (result, headers, body) = clients[t].get_frame()
            eq_(result, 'MESSAGE')
            eq_(body, msg)
            eq_(get_header_value(headers, 'destination'), t)

    @timed(2)
    def test_subscribe_with_id_message(self):
        """Test if we get our message back on the same connection if we send a message and subscribe with an id"""
        m = Main()
        m.tcp_connect()
        m.send_connect([('login', '1.test'), ('passcode', 'test')])
        m.get_frame()  # Connected frame

        subscribleId = str(uuid.uuid4())

        m.send_frame('SUBSCRIBE',
                     [('destination', config.TEST_TOPICS[0]), ('x-ebu-nofastreply', 'yes'), ('id', subscribleId)], '')

        msg = str(uuid.uuid4())

        m.send_frame('SEND', [('destination', config.TEST_TOPICS[0])], msg)

        (result, headers, body) = m.get_frame()
        eq_(result, 'MESSAGE')
        eq_(body, msg)
        eq_(get_header_value(headers, 'destination'), config.TEST_TOPICS[0])
        eq_(get_header_value(headers, 'subscription'), subscribleId)

    @timed(2)
    def test_message_forward_link(self):
        """Test link header is forwarder when we send a message"""
        m = Main()
        m.tcp_connect()
        m.send_connect([('login', '1.test'), ('passcode', 'test')])
        m.get_frame()  # Connected frame
        m.send_frame('SUBSCRIBE', [('destination', config.TEST_TOPICS[0]), ('x-ebu-nofastreply', 'yes')], '')

        msg = str(uuid.uuid4())
        link = str(uuid.uuid4())

        m.send_frame('SEND', [('destination', config.TEST_TOPICS[0]), ('link', link)], msg)

        (result, headers, body) = m.get_frame()
        eq_(result, 'MESSAGE')
        eq_(body, msg)
        eq_(get_header_value(headers, 'destination'), config.TEST_TOPICS[0])
        eq_(get_header_value(headers, 'link'), link)

    @timed(2)
    def test_message_forward_trigger_time(self):
        """Test trigger-time header is forwarder when we send a message"""
        m = Main()
        m.tcp_connect()
        m.send_connect([('login', '1.test'), ('passcode', 'test')])
        m.get_frame()  # Connected frame
        m.send_frame('SUBSCRIBE', [('destination', config.TEST_TOPICS[0]), ('x-ebu-nofastreply', 'yes')], '')

        msg = str(uuid.uuid4())
        trigger_time = str(uuid.uuid4())

        m.send_frame('SEND', [('destination', config.TEST_TOPICS[0]), ('trigger-time', trigger_time)], msg)

        (result, headers, body) = m.get_frame()
        eq_(result, 'MESSAGE')
        eq_(body, msg)
        eq_(get_header_value(headers, 'destination'), config.TEST_TOPICS[0])
        eq_(get_header_value(headers, 'trigger-time'), trigger_time)

    @timed(2)
    def test_message_id_is_created(self):
        """Test if message-id is set if we don't"""
        m = Main()
        m.tcp_connect()
        m.send_connect([('login', '1.test'), ('passcode', 'test')])
        m.get_frame()  # Connected frame
        m.send_frame('SUBSCRIBE', [('destination', config.TEST_TOPICS[0]), ('x-ebu-nofastreply', 'yes')], '')

        msg = str(uuid.uuid4())

        m.send_frame('SEND', [('destination', config.TEST_TOPICS[0])], msg)

        (result, headers, body) = m.get_frame()
        eq_(result, 'MESSAGE')
        eq_(body, msg)
        eq_(get_header_value(headers, 'destination'), config.TEST_TOPICS[0])
        assert get_header_value(headers, 'message-id') is not None

    @timed(2)
    def test_message_id_is_forwarder(self):
        """Test if message-id is set to our value if we sent it"""
        m = Main()
        m.tcp_connect()
        m.send_connect([('login', '1.test'), ('passcode', 'test')])
        m.get_frame()  # Connected frame
        m.send_frame('SUBSCRIBE', [('destination', config.TEST_TOPICS[0]), ('x-ebu-nofastreply', 'yes')], '')

        msg = str(uuid.uuid4())
        message_id = str(uuid.uuid4())

        m.send_frame('SEND', [('destination', config.TEST_TOPICS[0]), ('message-id', message_id)], msg)

        (result, headers, body) = m.get_frame()
        eq_(result, 'MESSAGE')
        eq_(body, msg)
        eq_(get_header_value(headers, 'destination'), config.TEST_TOPICS[0])
        eq_(get_header_value(headers, 'message-id'), message_id)

    @timed(2)
    def test_message_flooding_is_ok(self):
        """Test if multiple messages are send in one frame, it's ok."""
        m = Main()
        m.tcp_connect()

        connect_frame = m.build_frame('CONNECT', [], '')
        subscrible_frame_1 = m.build_frame('SUBSCRIBE', [('destination', config.TEST_TOPICS[0]), ('x-ebu-nofastreply', 'yes')], '')

        m.socket.send(connect_frame + subscrible_frame_1)

        # Send a frame, we should be subscribled.
        msg = str(uuid.uuid4())
        message_id = str(uuid.uuid4())

        m2 = Main()
        m2.tcp_connect()
        m2.send_connect([('login', '1.test'), ('passcode', 'test')])
        m2.get_frame()  # Connected frame
        m2.send_frame('SEND', [('destination', config.TEST_TOPICS[0]), ('message-id', message_id)], msg)

        # Connect frame should be here
        (result, headers, body) = m.get_frame()
        eq_(result, 'CONNECTED')

        # And the message
        (result, headers, body) = m.get_frame()
        eq_(result, 'MESSAGE')
        eq_(body, msg)
        eq_(get_header_value(headers, 'destination'), config.TEST_TOPICS[0])
        eq_(get_header_value(headers, 'message-id'), message_id)

    @timed(2)
    def test_message_flooding_with_slashn_is_ok(self):
        """Test if multiple messages are send in one frame, with a \n return between, it's ok."""
        m = Main()
        m.tcp_connect()

        connect_frame = m.build_frame('CONNECT', [], '')
        subscrible_frame_1 = m.build_frame('SUBSCRIBE', [('destination', config.TEST_TOPICS[0]), ('x-ebu-nofastreply', 'yes')], '')

        m.socket.send(connect_frame + '\n' + subscrible_frame_1)
        m.socket.settimeout(3)

        # Send a frame, we should be subscribled.
        msg = str(uuid.uuid4())
        message_id = str(uuid.uuid4())

        m2 = Main()
        m2.tcp_connect()
        m2.send_connect([('login', '1.test'), ('passcode', 'test')])
        m2.get_frame()  # Connected frame
        m2.send_frame('SEND', [('destination', config.TEST_TOPICS[0]), ('message-id', message_id)], msg)

        # Connect frame should be here
        (result, headers, body) = m.get_frame()
        eq_(result, 'CONNECTED')

        # And the message
        (result, headers, body) = m.get_frame()
        eq_(result, 'MESSAGE')
        eq_(body, msg)
        eq_(get_header_value(headers, 'destination'), config.TEST_TOPICS[0])
        eq_(get_header_value(headers, 'message-id'), message_id)

    @timed(2)
    def test_randomheaders_arent_forwarded(self):
        """Test if random headers aren't forwarded"""
        m = Main()
        m.tcp_connect()
        m.send_connect([('login', '1.test'), ('passcode', 'test')])
        m.get_frame()  # Connected frame
        m.send_frame('SUBSCRIBE', [('destination', config.TEST_TOPICS[0]), ('x-ebu-nofastreply', 'yes')], '')

        msg = str(uuid.uuid4())

        m.send_frame('SEND', [('destination', config.TEST_TOPICS[0]), ('_test_header_42', '_test_header_42')], msg)

        (result, headers, body) = m.get_frame()
        eq_(result, 'MESSAGE')
        eq_(body, msg)
        eq_(get_header_value(headers, 'destination'), config.TEST_TOPICS[0])
        eq_(get_header_value(headers, '_test_header_42'), None)

    @timed(2)
    def test_when_is_created(self):
        """Test if when header is set"""
        m = Main()
        m.tcp_connect()
        m.send_connect([('login', '1.test'), ('passcode', 'test')])
        m.get_frame()  # Connected frame
        m.send_frame('SUBSCRIBE', [('destination', config.TEST_TOPICS[0]), ('x-ebu-nofastreply', 'yes')], '')

        msg = str(uuid.uuid4())

        m.send_frame('SEND', [('destination', config.TEST_TOPICS[0])], msg)

        (result, headers, body) = m.get_frame()
        eq_(result, 'MESSAGE')
        eq_(body, msg)
        eq_(get_header_value(headers, 'destination'), config.TEST_TOPICS[0])
        assert get_header_value(headers, 'when') is not None

    @timed(2)
    def test_disconnect(self):
        """Test we can disconnect"""
        m = Main()
        m.tcp_connect()
        m.send_connect([('login', '1.test'), ('passcode', 'test')])
        m.get_frame()  # Connected frame

        m.send_frame('DISCONNECT', [], '')

        m.socket.settimeout(3)
        data = m.socket.recv(1024)
        eq_(data, '')  # Closed socket return None

    @nottest
    def test_if_message_is_send(self, topicSend, topicSubcrible):
        """Generic function for GCC/CC tests, testing if a message is got using a topic for sending and a topic to subscrible"""
        m = Main()
        m.tcp_connect()
        m.send_connect([('login', '3.test'), ('passcode', 'test')])
        m.get_frame()  # Connected frame
        m.send_frame('SUBSCRIBE', [('destination', topicSubcrible), ('x-ebu-nofastreply', 'yes')], '')

        msg = str(uuid.uuid4())

        m.send_frame('SEND', [('destination', topicSend)], msg)

        (result, headers, body) = m.get_frame()
        eq_(result, 'MESSAGE')
        eq_(body, msg)
        eq_(get_header_value(headers, 'destination'), topicSubcrible)

    @timed(2)
    def test_gcc_gcc(self):
        """Test that if we subscribe using a GCC topic and send a message using a GCC topic, we still get the message"""
        self.test_if_message_is_send(config.TEST_ECC_TOPIC_GCC, config.TEST_ECC_TOPIC_GCC)

    @timed(2)
    def test_gcc_cc(self):
        """Test that if we subscribe using a GCC topic and send a message using a CC topic, we still get the message"""
        self.test_if_message_is_send(config.TEST_ECC_TOPIC_CC, config.TEST_ECC_TOPIC_GCC)

    @timed(2)
    def test_cc_gcc(self):
        """Test that if we subscribe using a CC topic and send a message using a GCC topic, we still get the message"""
        self.test_if_message_is_send(config.TEST_ECC_TOPIC_GCC, config.TEST_ECC_TOPIC_CC)

    @timed(2)
    def test_cc_cc(self):
        """Test that if we subscribe using a CC topic and send a message using a CC topic, we still get the message"""
        self.test_if_message_is_send(config.TEST_ECC_TOPIC_CC, config.TEST_ECC_TOPIC_CC)

    @timed(2)
    def test_unsubscribe_no_subscribed(self):
        """Test we cannot unsubscribe if we're not subscribed"""
        m = Main()
        m.tcp_connect()
        m.send_connect([])
        m.get_frame()  # Connected frame

        m.send_frame('UNSUBSCRIBE', [('destination', config.TEST_TOPICS[0])], '')

        (result, headers, body) = m.get_frame()
        eq_(result, 'ERROR')

    @timed(2)
    def test_unsubscribe_id_no_subscribed(self):
        """Test we cannot unsubscribe (using id) if we're not subscribed"""
        m = Main()
        m.tcp_connect()
        m.send_connect([])
        m.get_frame()  # Connected frame

        m.send_frame('SUBSCRIBE', [('destination', config.TEST_TOPICS[0]), ('x-ebu-nofastreply', 'yes')], '')
        m.send_frame('UNSUBSCRIBE', [('id', '_test_id')], '')

        (result, headers, body) = m.get_frame()
        eq_(result, 'ERROR')

    @timed(2)
    def test_unsubscribe_withnothing(self):
        """Test we cannot unsubscribe if we don't specify a parameter"""
        m = Main()
        m.tcp_connect()
        m.send_connect([])
        m.get_frame()  # Connected frame

        m.send_frame('SUBSCRIBE', [('destination', config.TEST_TOPICS[0]), ('x-ebu-nofastreply', 'yes')], '')
        m.send_frame('UNSUBSCRIBE', [], '')

        (result, headers, body) = m.get_frame()
        eq_(result, 'ERROR')

    @raises(socket.timeout)
    @timed(2)
    def test_unsubscribe(self):
        """Test we can unsubscribe"""
        m = Main()
        m.tcp_connect()
        m.send_connect([])
        m.get_frame()  # Connected frame

        m.send_frame('SUBSCRIBE', [('destination', config.TEST_TOPICS[0]), ('x-ebu-nofastreply', 'yes')], '')
        m.send_frame('UNSUBSCRIBE', [('destination', config.TEST_TOPICS[0])], '')

        m.socket.settimeout(3)
        m.get_frame()

    @raises(socket.timeout)
    @timed(2)
    def test_unsubscribe_id(self):
        """Test we can unsubscribe, using ids"""
        m = Main()
        m.tcp_connect()
        m.send_connect([])
        m.get_frame()  # Connected frame

        id = str(uuid.uuid4())

        m.send_frame('SUBSCRIBE', [('destination', config.TEST_TOPICS[0]), ('id', id), ('x-ebu-nofastreply', 'yes')],
                     '')
        m.send_frame('UNSUBSCRIBE', [('id', id)], '')

        m.socket.settimeout(3)
        m.get_frame()

    @raises(socket.timeout)
    @timed(2)
    def test_unsubscribe_id_sub_only(self):
        """Test we can unsubscribe, using id for subscription only"""
        m = Main()
        m.tcp_connect()
        m.send_connect([])
        m.get_frame()  # Connected frame

        id = str(uuid.uuid4())

        m.send_frame('SUBSCRIBE', [('destination', config.TEST_TOPICS[0]), ('id', id), ('x-ebu-nofastreply', 'yes')],
                     '')
        m.send_frame('UNSUBSCRIBE', [('destination', config.TEST_TOPICS[0])], '')

        m.socket.settimeout(3)
        m.get_frame()

    @raises(socket.timeout)
    @timed(2)
    def test_unsubscribe_dontmnessage(self):
        """Test if we're unsubscribed, we don't get messages"""
        m = Main()
        m.tcp_connect()
        m.send_connect([('login', '1.test'), ('passcode', 'test')])
        m.get_frame()  # Connected frame

        m.send_frame('SUBSCRIBE', [('destination', config.TEST_TOPICS[0]), ('x-ebu-nofastreply', 'yes')], '')
        m.send_frame('UNSUBSCRIBE', [('destination', config.TEST_TOPICS[0])], '')

        m.send_frame('SEND', [('destination', config.TEST_TOPICS[0])], str(uuid.uuid4()))

        m.socket.settimeout(3)
        m.get_frame()

    @raises(socket.timeout)
    @timed(2)
    def test_unsubscribe_dontmnessage_withid(self):
        """Test if we're unsubscribed (using ids), we don't get messages"""
        m = Main()
        m.tcp_connect()
        m.send_connect([('login', '1.test'), ('passcode', 'test')])
        m.get_frame()  # Connected frame

        id = str(uuid.uuid4())

        m.send_frame('SUBSCRIBE', [('destination', config.TEST_TOPICS[0]), ('id', id), ('x-ebu-nofastreply', 'yes')],
                     '')
        m.send_frame('UNSUBSCRIBE', [('id', id)], '')

        m.send_frame('SEND', [('destination', config.TEST_TOPICS[0])], str(uuid.uuid4()))

        m.socket.settimeout(3)
        m.get_frame()

    @raises(socket.timeout)
    @timed(2)
    def test_unsubscribe_dontmessage_withsubid(self):
        """Test if we're unsubscribed (using id only for subscription), we don't get messages"""
        m = Main()
        m.tcp_connect()
        m.send_connect([('login', '1.test'), ('passcode', 'test')])
        m.get_frame()  # Connected frame

        id = str(uuid.uuid4())

        m.send_frame('SUBSCRIBE', [('destination', config.TEST_TOPICS[0]), ('id', id), ('x-ebu-nofastreply', 'yes')],
                     '')
        m.send_frame('UNSUBSCRIBE', [('destination', config.TEST_TOPICS[0])], '')

        m.send_frame('SEND', [('destination', config.TEST_TOPICS[0])], str(uuid.uuid4()))

        m.socket.settimeout(3)
        m.get_frame()

    @timed(2)
    def test_watchdog_send_logs(self):
        """Test if the watchdog send logs"""

        m = Main()
        watchdogsock = m.get_watchdogsocket()
        m.tcp_connect()
        m.send_connect([('login', '4.test'), ('passcode', 'test')])
        m.get_frame()  # Connected frame

        msg = str(uuid.uuid4())

        # Empty logs
        watchdogsock.settimeout(0.1)
        try:
            while watchdogsock.recvfrom(4096):
                pass
        except socket.timeout:
            pass

        m.send_frame('SEND', [('destination', config.TEST_WATCHDOG_TOPIC[0][0])], msg)

        # Check if we got logs (maximum for 3 seconds)
        start = time.time()

        watchdogsock.settimeout(1)

        while time.time() < (start + 3):
            frame, _ = watchdogsock.recvfrom(4096)
            if frame != '':
                jframe = json.loads(frame)

                if jframe['type'] == 'log':
                    if jframe['topic'] == config.TEST_WATCHDOG_TOPIC[0][0] and jframe['message'] == msg:
                        watchdogsock.close()
                        return
        watchdogsock.close()
        raise Exception("No logs")

    @timed(config.TEST_FB_LOGS_CLEANUP + 3)
    def test_watchdog_send_cleanup_logs(self):
        """Test if the watchdog send cleanup_logs"""

        m = Main()
        watchdogsock = m.get_watchdogsocket()

        # Empty logs
        watchdogsock.settimeout(0.1)
        try:
            while watchdogsock.recvfrom(4096):
                pass
        except socket.timeout:
            pass

        watchdogsock.settimeout(1)

        # Check if we got logs (maximum for TEST_FB_LOGS_CLEANUP+2 seconds)
        start = time.time()

        while time.time() < (start + config.TEST_FB_LOGS_CLEANUP + 2):
            try:
                frame, _ = watchdogsock.recvfrom(4096)
            except socket.timeout:
                frame = ''

            if frame != '':
                jframe = json.loads(frame)

                if jframe['type'] == 'cleanup_logs':
                    watchdogsock.close()
                    return
        watchdogsock.close()
        raise Exception("No cleanup_logs")

    def test_watchdog_is_watchdoging(self):
        """Test if the watchdog: doesn't send message if one was sent, and send one if the channel is timing out."""

        m = Main()
        m.tcp_connect()
        m.send_connect([('login', '4.test'), ('passcode', 'test')])
        m.get_frame()  # Connected frame

        ownMessage = str(uuid.uuid4())

        # Send a message, then subscrible
        m.send_frame('SEND', [('destination', config.TEST_WATCHDOG_TOPIC[0][0] + 'text')], ownMessage)
        m.send_frame('SUBSCRIBE',
                     [('destination', config.TEST_WATCHDOG_TOPIC[0][0] + 'text'), ('x-ebu-nofastreply', 'yes')], '')

        # There should be no message for TEST_FB_FALLBACK_TIME/2
        m.socket.settimeout(config.TEST_FB_FALLBACK_TIME / 2)

        ok = True

        try:
            while True:
                (result, _, body) = m.get_frame()
                if result != 'MESSAGE' or body != ownMessage:
                    ok = False
        except Exception:
            pass

        if not ok:
            raise Exception("Socket didn't timeout !")

        m.send_frame('SEND', [('destination', config.TEST_WATCHDOG_TOPIC[0][0] + 'text')], ownMessage)

        # There should be no message (except our message) for TEST_FB_FALLBACK_TIME-1
        m.socket.settimeout(config.TEST_FB_FALLBACK_TIME - 1)
        try:
            while True:
                (result, _, body) = m.get_frame()
                if result != 'MESSAGE' or body != ownMessage:
                    ok = False
        except Exception:
            pass

        if not ok:
            raise Exception("Socket didn't timeout !")

        # There should be a message if we wait for at least 1 + TEST_FB_FALLBACK_CHECK*2
        time.sleep(1 + config.TEST_FB_FALLBACK_CHECK * 2)
        m.socket.settimeout(1)
        (result, headers, body) = m.get_frame()
        eq_(result, 'MESSAGE')

    def test_watchdog_send_good_data_image(self):
        """Test if the watchdog send excepted data on topic /image"""

        m = Main()
        m.tcp_connect()
        m.send_connect([('login', '4.test'), ('passcode', 'test')])
        m.get_frame()  # Connected frame

        # Send a message, then subscribe
        m.send_frame('SUBSCRIBE',
                     [('destination', config.TEST_WATCHDOG_TOPIC[0][0] + 'image'), ('x-ebu-nofastreply', 'yes')], '')

        m.socket.settimeout(config.TEST_FB_FALLBACK_TIME + config.TEST_FB_FALLBACK_CHECK)

        (result, headers, body) = m.get_frame()
        eq_(result, 'MESSAGE')
        eq_(body, 'SHOW ' + config.FB_IMAGE_LOCATIONS + config.TEST_CHANNEL_DEFAULT['filename'])
        eq_(get_header_value(headers, 'trigger-time'), 'NOW')
        eq_(get_header_value(headers, 'link'), config.TEST_CHANNEL_DEFAULT['radiolink'])

    def test_watchdog_send_good_data_text(self):
        """Test if the watchdog send excepted data on topic /text"""

        m = Main()
        m.tcp_connect()
        m.send_connect([('login', '4.test'), ('passcode', 'test')])
        m.get_frame()  # Connected frame

        # Send a message, then subscrible
        m.send_frame('SUBSCRIBE',
                     [('destination', config.TEST_WATCHDOG_TOPIC[0][0] + 'text'), ('x-ebu-nofastreply', 'yes')], '')

        m.socket.settimeout(config.TEST_FB_FALLBACK_TIME + config.TEST_FB_FALLBACK_CHECK)

        (result, headers, body) = m.get_frame()
        eq_(result, 'MESSAGE')
        eq_(body, 'TEXT ' + config.TEST_CHANNEL_DEFAULT['radiotext'])
        eq_(get_header_value(headers, 'trigger-time'), 'NOW')
        eq_(get_header_value(headers, 'link'), config.TEST_CHANNEL_DEFAULT['radiolink'])
