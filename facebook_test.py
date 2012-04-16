import os
import facebook
import unittest
import tempfile

class facebookTestCase(unittest.TestCase):

    def setUp(self):
        self.db_fd, facebook.app.config['DATABASE'] = tempfile.mkstemp()
        facebook.app.config['TESTING'] = True
        self.app = facebook.app.test_client()
        facebook.init_db()

    def tearDown(self):
        os.close(self.db_fd)
        os.unlink(facebook.app.config['DATABASE'])

if __name__ == '__main__':
    unittest.main()
