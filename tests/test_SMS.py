import os
import sys
import logging
import unittest


_this_dir = os.path.dirname(os.path.abspath(__file__))
to_add = os.path.abspath(_this_dir + '/..')  # for 'qa_py'
if to_add not in sys.path:
    sys.path.insert(0, to_add)

if 1:
    from application import application
    from SMS.SMS_Misc import sendSMS
    from SMS.TransactionSMS import walletSMS
    from Misc import logger

logg = logging.getLogger(__name__)
logg = logger.setLogger(logg)


class SMSTestCases(unittest.TestCase):
    def setUp(self):
        logg.info('=> Setting up test client')
        self.app = application.test_client()

    def tearDown(self):
        pass

    def test_Transactional_SMS(self):
        response = self.app.get('/api/v1.0/sendtraSMS', query_string = dict(mobile = '8178265894', message = 'Hi'))
        status = str(response.data)
        self.assertTrue('found' not in status)

    def test_send_SMS(self):
        response = sendSMS('8178265894', 'Hi')
        self.assertTrue('found' not in response)

    def test_wallet_SMS(self):
        response = walletSMS('557', 10, 10)
        self.assertTrue('found' not in response)





