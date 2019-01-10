import os
import sys
import unittest
import logging
import xmlrunner


_this_dir = os.path.dirname(os.path.abspath(__file__))
to_add = os.path.abspath(_this_dir + '/..')  # for 'qa_py'
if to_add not in sys.path:
    sys.path.insert(0, to_add)

if 1:
    from Misc import logger
    from application import application

logg = logging.getLogger(__name__)
logg = logger.setLogger(logg)


class AppTestCases(unittest.TestCase):

    def setUp(self):
        logg.info('=> Setting up test client')
        self.app = application.test_client()

    def tearDown(self):
        pass

    def test_application_working(self):
        response = self.app.get('/')
        self.assertEqual(response.status_code, 200)

    def test_login_correct_credential(self):
        response = self.app.get('/api/v1.0/verifyemployee', query_string = dict(username = 'sushil', password = 'sushil'))
        logg.info(response.data)
        self.assertEqual(response.status_code, 200)

    def test_login_incorrect_credential(self):
        pass

    def test_verify_mobile(self):
        pass

    def test_verify_false_mobile(self):
        pass

    def test_category(self):
        response = self.app.get('/api/v1.0/category')
        pass

    def test_items(self):
        response = self.app.get('/api/v1.0/item')

if __name__ == '__main__':
    unittest.main(testRunner=xmlrunner.XMLTestRunner(output="./python_unittests_xml"))

