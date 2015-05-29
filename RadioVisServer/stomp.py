
import uuid
import logging
import time

from gevent.coros import RLock

from gevent import spawn, queue

from radiodns import RadioDns

# API
radioDns = RadioDns()

logger = logging.getLogger('radiovisserver.stompserver')


class StompServer():
    """A basic stomp server"""

    def __init__(self, socket, LAST_MESSAGES, rabbitcox, monitoring):
        (self.info_ip, self.info_port) = socket.getpeername()

        # logger = %s:%s logging.getLogger('radiovisserver.%s:%s stompserver.' + ip + '.' + str(port))

        self.socket = socket
        # Buffer for icoming data
        self.incomingData = ''
        # Topic the client subscribled to
        self.topics = []

        # Queue of messages
        self.queue = queue.Queue(maxsize=250)
        # Lock to send frame
        self.lock = RLock()

        # Mapping channel -> id for subscritions
        self.idsByChannels = {}

        # Mapping id- -> channel for subscritions
        self.channelsByIds = {}

        # Last messages
        self.LAST_MESSAGES = LAST_MESSAGES

        # RabbitCox
        self.rabbitcox = rabbitcox

        # Monitoring
        self.monitoring = monitoring

        # Create a session id
        self.session_id = str(uuid.uuid4())

        # Station id, if authenticated
        self.station_id = None

        # True if threads should be stopped
        self.sucide = False


    def close(self):

        if not self.sucide:
            self.sucide = True

            while len(self.topics) > 0:
                self.monitoring.count("radiovis.global.unsubscriptions", {
                    "topic": self.topics.pop(),
                    "session_id": self.session_id,
                    "ip": self.info_ip + ':' + str(self.info_port)
                })
            self.socket.close()

    def get_frame(self):
        """Get one stomp frame"""

        while not "\x00" in self.incomingData:
            time.sleep(0)  # Switch context
            data = self.socket.recv(1024)
            if not data:
                logger.info("%s:%s Socket seem closed" % (self.info_ip, self.info_port))
                raise Exception("Socket seem closed.")
            else:
                self.incomingData += data

        # Get only one frame
        splited_data = self.incomingData.split('\x00', 1)

        # Save the rest for later
        self.incomingData = splited_data[1]

        # Get command, headers and body

        frame = splited_data[0].lstrip()  # Remove \n at the begining

        frame_splited = frame.replace('\r', '').split('\n')

        command = frame_splited[0].strip()

        headers = []
        body = ""
        headerMode = True

        for x in frame_splited[1:]:
            if x == '' and headerMode:  # Switch from headers to body
                headerMode = False
            elif headerMode:  # Add header to the lsit
                if x:
                    if ':' in x:
                        key, value = x.split(':', 1)
                        headers.append((key, value))
                    else:  # No value
                        headers.append((x, ''))
            else:  # Compute the body
                body += x + '\n'

        # Remove last '\n'
        body = body[:-1]

        logger.debug("%s:%s Got one frame: %s %s %s" % (self.info_ip, self.info_port, command, headers, body))

        # Return everything
        return (command, headers, body)

    def send_frame(self, command, headers, body):
        """Send a frame to the client"""

        # Lock the send, so we don't send a command inside a command
        logger.debug("%s:%s Wait for lock to send frame: %s %s %s" % (self.info_ip, self.info_port, command, headers, body))
        with self.lock:

            message_to_send = ''

            message_to_send += command + '\n'

            for (header, value) in headers:
                message_to_send += header + ':' + value + '\n'

            message_to_send += '\n'

            message_to_send += body

            message_to_send += '\x00'

            self.socket.send(message_to_send)

        logger.debug("%s:%s Frame send !" % (self.info_ip, self.info_port))

    def new_message(self, topic, message, headers):
        """Handle a new message"""

        if self.sucide:  # Don't add message to the queue if connection is closed
            return

        def put_in_queue():
            try:
                self.queue.put_nowait((topic, message, headers))
                return True
            except:
                return False


        # If queue is not full, put it directry
        if not self.queue.full():
            if put_in_queue():  # Another thread can fill the queue
                return True

        # Queue is full: Sleep a little bit
        logger.warn("%s:%s Queue is full: Switching context." % (self.info_ip, self.info_port))
        time.sleep(0)  # Client will probably try to process his queue :)

        # Last try
        if not put_in_queue():
            logger.error("%s:%s Queue is full: Destroying the stom server" % (self.info_ip, self.info_port))
            self.close()

    def consume_queue(self):
        """A thread who read topics from the queue of message and send them to the client, if requested"""

        try:
            while not self.sucide:
                logger.debug("%s:%s Waiting for message in queue" % (self.info_ip, self.info_port))

                try:
                    result = self.queue.get(timeout=10)
                except queue.Empty:
                    result = None

                if result:
                    topic, message, bonusHeaders = result
                    logger.debug("%s:%s Got a message on topic %s: %s (headers: %s)" % (self.info_ip, self.info_port, topic, message, bonusHeaders))

                    # Is the user subscribed ?
                    if topic in self.topics:
                        topicMatching = topic
                    else:  # Is the user subscribled because of a special case ?
                        topicMatching = radioDns.check_special_matchs(topic, self.topics)

                    if topicMatching is not None:
                        logger.debug("%s:%s Sending the message to the client !" % (self.info_ip, self.info_port))
                        headers = [('destination', topicMatching)]

                        for header in bonusHeaders:
                            headers.append(header)

                        # If subscribled with an ID, add the subscription header
                        if topicMatching in self.idsByChannels:
                            headers.append(('subscription', self.idsByChannels[topicMatching]))

                        self.monitoring.count("radiovis.global.messages", {
                            "topic": topicMatching,
                            "session_id": self.session_id,
                            "body": str(message),
                            "ip": self.info_ip + ':' + str(self.info_port)
                        })

                        self.send_frame("MESSAGE", headers, message)

                    time.sleep(0)  # Switch context

        except Exception as e:
            logger.error("%s:%s Error in consume_queue: %s" % (self.info_ip, self.info_port, e))
        finally:
            self.close()

    def run(self):
        """Main function to run the stompserver"""

        def get_header_value(headers, header):
            """Return the value of an header"""
            for (headerName, value) in headers:
                if headerName == header:
                    return value
            return None

        try:

            # A: Connection. Wait for a connect
            logger.debug("%s:%s Waiting for CONNECT" % (self.info_ip, self.info_port))
            (command, headers, body) = self.get_frame()

            if command != 'CONNECT':
                logger.error("%s:%s Unexcepted command, %s instead of CONNECT" % (self.info_ip, self.info_port, command))
                self.send_frame('ERROR', [('message', 'Excepted CONNECT')], '')
                return


            # Check username and password, if any
            user = get_header_value(headers, 'login')
            password = get_header_value(headers, 'passcode')

            if user is None:
                user = ''
            if password is None:
                password = ''

            user = user.strip()
            password = password.strip()

            if user != '' or password != '':
                if radioDns.check_auth(user, password, self.socket.getpeername()[0]):
                    self.station_id = user.split('.')[0]
                    logger.info("%s:%s Logged as station #%s" % (self.info_ip, self.info_port, self.station_id))
                else:
                    logger.warning("%s:%s Wrong password, closing connexion..." % (self.info_ip, self.info_port))
                    self.send_frame('ERROR', [('message', 'Wrong credentials')], '')
                    return

            else:
                logger.info("%s:%s Anonymous user" % (self.info_ip, self.info_port))

            logger.debug("%s:%s Session ID is %s" % (self.info_ip, self.info_port, self.session_id))

            # Prepase the response
            response_headers = []

            request_id = get_header_value(headers, "request-id")
            if request_id:
                response_headers.append(('response-id', request_id))

            receipt_id = get_header_value(headers, "receipt")
            if receipt_id:
                response_headers.append(('receipt-id', receipt_id))

            response_headers.append(('session', self.session_id))

            self.send_frame('CONNECTED', response_headers, '')

            logger.info("%s:%s Stomp client connected !" % (self.info_ip, self.info_port))

            # Spawn queue consumer
            spawn(self.consume_queue)

            # Now we just wait for a command
            while not self.sucide:

                logger.debug("%s:%s Waiting for a command" % (self.info_ip, self.info_port))
                (command, headers, body) = self.get_frame()

                logger.debug("%s:%s Processing command %s" % (self.info_ip, self.info_port, command))

                # If the client want us to ack the server, ackit
                receipt = get_header_value(headers, 'receipt')
                if receipt:
                    logger.debug("%s:%s Sending RECEIPT as requested (R-id: %s)" % (self.info_ip, self.info_port, receipt))
                    self.send_frame('RECEIPT', [('receipt-id', receipt)], '')

                # Parse the command
                if command == 'DISCONNECT':
                    # Close and finish
                    logger.info("%s:%s Client send a DISCONNECT" % (self.info_ip, self.info_port))
                    self.close()
                    return

                elif command == 'SUBSCRIBE':
                    # New subscription
                    channel = get_header_value(headers, 'destination')

                    if channel is None:

                        logger.warning("%s:%s SUBSCRIBE without a destination" % (self.info_ip, self.info_port))
                        self.send_frame('ERROR', [('message', 'I need a destination')], '')
                    else:
                        channel = channel.strip()

                        id = get_header_value(headers, 'id')

                        if id:
                            self.channelsByIds[id] = channel
                            self.idsByChannels[channel] = id

                        self.topics.append(channel)
                        logger.debug("%s:%s Client is now subscribed to %s [ID: %s]" % (self.info_ip, self.info_port, channel, id))

                        self.monitoring.count("radiovis.global.subscriptions", {
                            "topic": channel,
                            "session_id": self.session_id,
                            "ip": self.info_ip + ':' + str(self.info_port)
                        })

                        # Send the last message from the topic. A message may be send twice, but that should be ok
                        if get_header_value(headers, 'x-ebu-nofastreply') != 'yes':

                            converted_channel = radioDns.convert_fm_topic_to_gcc(channel)

                            if converted_channel in self.LAST_MESSAGES:
                                body, headers = self.LAST_MESSAGES[converted_channel]
                                logger.debug("%s:%s Quick sending the previous message %s (headers: %s)" % (self.info_ip, self.info_port, body, headers))
                                self.new_message(channel, body, headers)

                elif command == 'UNSUBSCRIBE':
                    # Remove subscription
                    channel = get_header_value(headers, 'destination')
                    id = get_header_value(headers, 'id')

                    if channel is None:
                        if id is None:
                            logger.error("%s:%s Unsubscribe without channel and id !" % (self.info_ip, self.info_port))
                            self.send_frame('ERROR', [('message', 'No ID or channel')], '')
                        else:
                            if id not in self.channelsByIds:
                                logger.error("%s:%s Unsubscribe with unknow id (%s)" % (self.info_ip, self.info_port, id))
                                self.send_frame('ERROR', [('message', 'Unknow ID')], '')
                            else:
                                channel = self.channelsByIds[id]

                    if channel not in self.topics:
                        logger.error("%s:%s Unsubscribe on unsubcribled channel (%s)" % (self.info_ip, self.info_port, channel))
                        self.send_frame('ERROR', [('message', 'Not subscribled')], '')
                    else:

                        self.topics.remove(channel)

                        if id and id in self.channelsByIds:
                            del self.channelsByIds[id]
                            del self.idsByChannels[channel]

                        logger.debug("%s:%s Client unsubscribled from %s [ID: %s]" % (self.info_ip, self.info_port, channel, id))

                elif command == 'SEND':

                    if self.station_id is None:
                        logger.warning("%s:%s Tried to SEND without been authenticated !" % (self.info_ip, self.info_port))
                        self.send_frame('ERROR', [('message', 'You cannot do that.')], '')
                    else:

                        # List of allowed channels
                        allowed_channels = radioDns.get_channels(self.station_id)

                        # Check rights
                        destination = get_header_value(headers, 'destination')

                        if destination is None:
                            logger.error("%s:%s SEND without destination !" % (self.info_ip, self.info_port))
                            self.send_frame('ERROR', [('message', 'No destination ?')], '')

                        else:

                            # Sepcial case: all destination:
                            all_destinations = destination[:9] == '/topic/*/'

                            # Find if the channel is allowed (It's a prefix of the destination !)
                            convertedDest = radioDns.convert_fm_topic_to_gcc(destination)
                            channel_ok = False
                            for chan in allowed_channels:
                                chan = radioDns.convert_fm_topic_to_gcc(chan)
                                if convertedDest[:len(chan)] == chan:
                                    channel_ok = True
                                    break

                            if not all_destinations and not channel_ok:
                                logger.warning("%s:%s Tryed to send to a destination not autorized ! (%s vs %s)" % (self.info_ip, self.info_port, destination, allowed_channels))
                                self.send_frame('ERROR', [('message', 'You cannot do that.')], '')
                            else:
                                logger.debug("%s:%s Allowed to send the message to %s" % (self.info_ip, self.info_port, destination))
                                # Prepare headers
                                msg_headers = {}

                                # Copy trigger time
                                trigger_time = get_header_value(headers, 'trigger-time')
                                if trigger_time:
                                    msg_headers['trigger-time'] = trigger_time

                                # Copy link
                                link = get_header_value(headers, 'link')
                                if link:
                                    msg_headers['link'] = link

                                # Message id
                                message_id = get_header_value(headers, 'message-id')
                                if not message_id:
                                    message_id = str(uuid.uuid4())
                                msg_headers['message-id'] = message_id

                                def send_to_dest(destination):
                                    # Destination
                                    msg_headers['topic'] = destination

                                    logger.debug("%s:%s Sending message %s to %s (headers: %s)" % (self.info_ip, self.info_port, body, destination, msg_headers))

                                    self.rabbitcox.send_message(msg_headers, body)

                                if all_destinations:
                                    logger.debug("%s:%s Broadcasting to all channels !!" % (self.info_ip, self.info_port))
                                    for dest in allowed_channels:
                                        send_to_dest(dest + destination[9:])
                                else:
                                    send_to_dest(destination)

                else:
                    logger.warning("%s:%s Unexcepted command %s %s %s" % (self.info_ip, self.info_port, command, headers, body))

        except Exception as e:
            logger.warn("%s:%s Error in run: %s" % (self.info_ip, self.info_port, e))
        finally:
            self.close()
