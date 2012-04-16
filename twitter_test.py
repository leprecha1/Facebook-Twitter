import os
import twitter
import unittest
import tempfile

class twitterTestCase(unittest.TestCase):

    def setUp(self):
        self.db_fd, twitter.app.config['DATABASE'] = tempfile.mkstemp()
        twitter.app.config['TESTING'] = True
        self.app = twitter.app.test_client()
        twitter.init_db()

    def tearDown(self):
        os.close(self.db_fd)
        os.unlink(twitter.app.config['DATABASE'])

if __name__ == '__main__':
    unittest.main()
