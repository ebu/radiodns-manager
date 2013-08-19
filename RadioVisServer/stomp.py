
import uuid
import logging

from gevent.coros import RLock

from gevent import spawn, queue

from radiodns import RadioDns

# API
radioDns = RadioDns()

class StompServer():
    """A basic stomp server"""

    def __init__(self, socket, LAST_MESSAGES, rabbitcox):
        (ip, port) = socket.getpeername()

        self.logger = logging.getLogger('radiovisserver.stompserver.' + ip + '.' + str(port))

        self.socket = socket
        # Buffer for icoming data
        self.incomingData = ''
        # Topic the client subscribled to
        self.topics = []
        
        # Queue of messages
        self.queue = queue.Queue()
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

        # Station id, if authenticated
        self.station_id = None


    def get_frame(self):
        """Get one stomp frame"""
        
        while not "\x00" in self.incomingData:
            data = self.socket.recv(1024)
            if not data:
               self.logger.warning("Socket seem closed")
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

        self.logger.debug("Got one frame: %s %s %s" % (command, headers, body))

        # Return everything
        return (command, headers, body)

    def send_frame(self, command, headers, body):
        """Send a frame to the client"""

        # Lock the send, so we don't send a command inside a command
        self.logger.debug("Wait for lock to send frame: %s %s %s" % (command, headers, body))
        with self.lock:

            self.socket.send(command + '\n')
            for (header, value) in headers:
                self.socket.send(header + ':' + value + '\n')

            self.socket.send('\n')

            self.socket.send(body)

            self.socket.send('\x00')
        self.logger.debug("Frame send !")

    def new_message(self, topic, message, headers):
        """Handle a new message"""

        # Put it inscide the queue
        self.queue.put((topic, message, headers))

    def consume_queue(self):
        """A thread who read topics from the queue of message and send them to the client, if requested"""
        
        try:
            while True:
                self.logger.debug("Waiting for message in queue")
                topic, message, bonusHeaders = self.queue.get()
                self.logger.debug("Got a message on topic %s: %s (headers: %s)" % (topic, message, bonusHeaders))

                # Is the user subscribled ?
                if topic in self.topics:
                    topicMatching = topic
                else:  # Is the user subscribled because of a special case ?
                    topicMatching = radioDns.check_special_matchs(topic, self.topics)
                
                if topicMatching is not None:
                    self.logger.debug("Sending the message to the client !")
                    headers = [('destination', topicMatching)]

                    for header in bonusHeaders:
                        headers.append(header)

                    # If subscribled with an ID, add the subscription header
                    if topicMatching in self.idsByChannels:
                        headers.append(('subscription', self.idsByChannels[topicMatching]))

                    self.send_frame("MESSAGE", headers , message)

        except Exception as e:
            self.logger.error("Error in consume_queue: %s" % (e, ))
        finally:
            self.socket.close()

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
            self.logger.debug("Waiting for CONNECT")
            (command, headers, body) = self.get_frame()

            if command != 'CONNECT':
                self.logger.error("Unexcepted command, %s instead of CONNECT" % (command, ))
                self.send_frame('ERROR', [('message', 'Excepted CONNECT')], '')
                return

            # Check username and password, if any
            user = get_header_value(headers, 'login')
            password = get_header_value(headers, 'passcode')

            if user is None:
                user = ''
            if password is None:
                password = ''

            if user != '' or password != '':
                if radioDns.check_auth(user, password, self.socket.getpeername()[0]):
                    self.station_id = user.split('.')[0]
                    self.logger.info("Logged as station #%s" % (self.station_id, ))    
                else:
                    self.logger.warning("Wrong password, closing connexion...")
                    self.send_frame('ERROR', [('message', 'Wrong credentials')], '')
                    return

            else:
                self.logger.info("Anonymous user")
                
            # Create a session id
            self.session_id = str(uuid.uuid4())

            self.logger.debug("Session ID is %s" % (self.session_id, ))

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

            self.logger.info("Stomp client connected !")

            # Spawn queue consumer
            spawn(self.consume_queue)

            # Now we just wait for a command
            while True:
                self.logger.debug("Waiting for a command")
                (command, headers, body) = self.get_frame()

                self.logger.debug("Processing command %s" % (command,))

                # If the client want us to ack the server, ackit
                receipt = get_header_value(headers, 'receipt')
                if receipt:
                    self.logger.debug("Sending RECEIPT as requested (R-id: %s)" % (receipt,))
                    self.send_frame('RECEIPT', [('receipt-id', receipt)], '')


                # Parse the command
                if command == 'DISCONNECT':
                    # Close and finish
                    self.logger.info("Client send a DISCONNECT")
                    self.socket.close()
                    return

                elif command == 'SUBSCRIBE':
                    # New subscription
                    channel = get_header_value(headers, 'destination')

                    if channel is None:

                        self.logger.warning("SUBSCRIBE without a destination")
                        self.send_frame('ERROR', [('message', 'I need a destination')], '')
                    else:
                        channel = channel.strip()

                        id = get_header_value(headers, 'id')

                        if id:
                            self.channelsByIds[id] = channel
                            self.idsByChannels[channel] = id

                        self.topics.append(channel)
                        self.logger.debug("Client is now subscribled to %s [ID: %s]" % (channel,id))

                        # Send the last message from the topic. A message may be send twice, but that should be ok
                        if  get_header_value(headers, 'x-ebu-nofastreply') != 'yes':
                            if channel in self.LAST_MESSAGES:
                                body, headers = self.LAST_MESSAGES[channel]
                                self.logger.debug("Quick sending the previous message %s (headers: %s)" % (body, headers))
                                self.new_message(channel, body, headers)

                elif command == 'UNSUBSCRIBE':
                    # Remove subscription
                    channel = get_header_value(headers, 'destination')
                    id = get_header_value(headers, 'id')

                    if channel is None:
                        if id is None:
                            self.logger.error("Unsubscribe without channel and id !")
                            self.send_frame('ERROR', [('message', 'No ID or channel')], '')
                        else:
                            if id not in self.channelsByIds:
                                self.logger.error("Unsubscribe with unknow id (%s)" % (id, ))
                                self.send_frame('ERROR', [('message', 'Unknow ID')], '')
                            else:
                                channel = self.channelsByIds[id]

                    if channel not in self.topics:
                        self.logger.error("Unsubscribe on unsubcribled channel (%s)" % (channel, ))
                        self.send_frame('ERROR', [('message', 'Not subscribled')], '')
                    else:

                        self.topics.remove(channel)

                        if id and id in self.channelsByIds:
                            del self.channelsByIds[id]
                            del self.idsByChannels[channel] 

                        self.logger.debug("Client unsubscribled from %s [ID: %s]" % (channel,id))

                elif command == 'SEND':

                    if self.station_id is None:
                        self.logger.warning("Tried to SEND without been authenticated !")
                        self.send_frame('ERROR', [('message', 'You cannot do that.')], '')
                    else:

                        # List of allowed channels
                        allowed_channels = radioDns.get_channels(self.station_id)

                        # Check rights
                        destination = get_header_value(headers, 'destination')

                        if destination is None:
                            self.logger.error("SEND without destination !")
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
                                self.logger.warning("Tryed to send to a destination not autorized ! (%s vs %s)" % (destination, allowed_channels))
                                self.send_frame('ERROR', [('message', 'You cannot do that.')], '')
                            else:
                                self.logger.debug("Allowed to send the message to %s" % (destination, ))
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

                                    self.logger.debug("Sending message %s to %s (headers: %s)" % (body, destination, msg_headers))

                                    self.rabbitcox.send_message(msg_headers, body)

                                if all_destinations:
                                    self.logger.debug("Broadcasting to all channels !!")
                                    for dest in allowed_channels:
                                        send_to_dest(dest + destination[9:])
                                else:   
                                    send_to_dest(destination)

                else:
                    self.logger.warning("Unexcepted command %s %s %s" % (command, headers, body))

                

        except Exception as e:
            self.logger.error("Error in run: %s" % (e, ))
        finally:
            self.socket.close()