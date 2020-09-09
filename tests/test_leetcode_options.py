'''
Unit tests for leetcode_sql_unlocked.py program.
Assumes setup.py has already been run.
Simulates the rest of the program from scratch.
CAUTION: This program will archives logs and delete driver and log folders
Every user option is tested and the state of the log is compared with the state of the QuestionNodes object.
'''
from datetime import datetime
import unittest
import time
import os

parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.sys.path.insert(0, parent_dir)
from leetcode_sql_unlocked import LeetcodeUnlocked

class TestLeetcodeOptions(unittest.TestCase):

    @classmethod
    def setUpClass(self):
        '''
        Tests leetcode_sql_unlocked.py, starting from scratch with no previous logs and drivers
        WARNING: deletes driver, and moves all logs to a folder called logs_archive
        '''
        os.chdir(parent_dir)
        self.lc = LeetcodeUnlocked(headless=True)

    @classmethod
    def options(self, user_input):
        self.lc.options(user_input)

    @classmethod
    def tearDownClass(self):
        self.lc.exit()

    def test_invalid_options(self):

        print('\n----------------Running invalid inputs-------')
        print('Should print only invalid inputs\n\n')
        user_input = 'ahcd'
        self.options(user_input)

        user_input = 'zef'
        self.options(user_input)

        user_input = '!!!!!!____'
        self.options(user_input)

        user_input = ''
        self.options(user_input)

        user_input = '  '
        self.options(user_input)
        time.sleep(3)

    def test_help_options(self):
        print('\n----------------Running help inputs-------')
        print('Should print help menu twice\n\n')
        user_input = '_help'
        self.options(user_input)

        user_input = 'he#'
        self.options(user_input)
        time.sleep(3)

    def test_disp_options(self):
        print('\n----------------Running display inputs-------')
        print('Should print different displays\n\n')

        user_input = 'dis$play'
        self.options(user_input)

        user_input = 'dg 5'
        self.options(user_input)

        user_input = 'de16'
        self.options(user_input)

        user_input = 'dmed 30'
        self.options(user_input)

        user_input = 'd hdf40'
        self.options(user_input)

        user_input = 'd h400'
        self.options(user_input)

        user_input = 'd e600'
        self.options(user_input)

    def test_load_options(self):
        print('\n----------------Running pre-load option inputs-------')
        user_inputs = ['load on', 'load off', 'lon', 'loff', 'ldkfdkf']
        for user_input in user_inputs:
            self.options(user_input)

    def test_preloading_delay(self):
        print('\n-------------Checking preload delays lasting correct duration----')
        self.options('load on')

        a = datetime.now()
        self.lc.preload_delay(10)
        b = datetime.now()
        self.assertTrue((b-a).total_seconds() >= 15)

        a = datetime.now()
        self.lc.preload_delay(5)
        b = datetime.now()
        self.assertTrue((b-a).total_seconds() <= 3)

        self.options('load off')
        self.assertTrue(self.lc.stop_event._flag)
        a = datetime.now()
        self.lc.preload_delay(100)
        b = datetime.now()
        self.assertTrue((b-a).total_seconds() <= 3)
        self.options('load on')

if __name__ == '__main__':
    unittest.main()

