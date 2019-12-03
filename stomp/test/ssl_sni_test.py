import unittest
import uuid

import stomp
from stomp.listener import TestListener
from stomp.test.testutils import *


class TestSNIMQSend(unittest.TestCase):
    """
    To test SNI:

    - Run a STOMP server in 127.0.0.1:62613

    - Add a couple fully qualified hostnames to your /etc/hosts
        # SNI test hosts
        127.0.0.1 my.example.com
        127.0.0.1 my.example.org

    - Run `make haproxy` which will generate keys and run the haproxy load balancer

    Connections with SNI to "my.example.com" will be routed to the STOMP server on port 62613.
    Connections without SNI won't be routed.

    """

    def setUp(self):
        self.receipt_id = str(uuid.uuid4())

    def testconnect(self):
        conn = stomp.Connection11(get_sni_ssl_host())
        conn.set_ssl(get_sni_ssl_host())
        listener = TestListener(self.receipt_id)
        conn.set_listener('', listener)
        conn.connect(get_default_user(), get_default_password(), wait=True)
        conn.subscribe(destination='/queue/test', id=1, ack='auto')

        print('.....sending message with receipt %s' % self.receipt_id)
        conn.send(body='this is a test', destination='/queue/test', receipt=self.receipt_id)

        print('>>>>wait on receipt')
        listener.wait_for_message()
        print('>>>>>receipt received')
        conn.disconnect(receipt=None)

        self.assertTrue(listener.connections == 1, 'should have received 1 connection acknowledgement')
        self.assertTrue(listener.messages >= 1, 'should have received 1 message')
        self.assertTrue(listener.errors == 0, 'should not have received any errors')
