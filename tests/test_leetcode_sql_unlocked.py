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
import shutil

parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.sys.path.insert(0, parent_dir)
from leetcode_sql_unlocked import LeetcodeUnlocked

def remove(path):
    """ param <path> could either be relative or absolute. """
    print(f'Deleting {path}')
    if os.path.isfile(path) or os.path.islink(path):
        os.remove(path)  # remove the file
    elif os.path.isdir(path):
        shutil.rmtree(path)  # remove dir and all contains
    else:
        raise ValueError("file {} is not a file or dir.".format(path))

def move_to_archive(curr_dir, archive_dir):
    '''
    Moves existing logs/files to archive directory
    '''
    if not os.path.exists(archive_dir):
        os.mkdir(archive_dir)
    for f in os.listdir(curr_dir):
        curr_path = os.path.join(curr_dir, f)
        archive_path = os.path.join(archive_dir, datetime.now().strftime('%Y-%m-%d-%H-%M ')+ f)
        print(f'Moving {f} to {archive_dir}')
        #move files to archive folder
        os.rename(curr_path, archive_path)

class TestLeetcode(unittest.TestCase):

    @classmethod
    def setUpClass(self):
        '''
        Tests leetcode_sql_unlocked.py, starting from scratch with no previous logs and drivers
        WARNING: deletes driver, and moves all logs to a folder called logs_archive
        '''
        os.chdir(parent_dir)
        curr_log_dir = os.path.join(os.getcwd(), 'logs')
        curr_driver_dir = os.path.join(os.getcwd(), 'drivers')
        archive_log_dir = os.path.join(os.getcwd(), 'logs_archive')
        if os.path.exists(curr_log_dir):
            move_to_archive(curr_log_dir, archive_log_dir)
            remove(curr_log_dir)
        if os.path.exists(curr_driver_dir):
            remove(curr_driver_dir)
        self.lc = LeetcodeUnlocked(True)

    @classmethod
    def tearDownClass(self):
        self.lc.exit()

    def get_q_state(self):
        return self.lc.question_log.q_state

    def is_q_match(self, compar_num=None):
        '''
        Checks if question node current number and q log current number are the same
        Optionally, can compare a third expected number, compar_num
        '''
        q_nodes_current = self.lc.question_nodes.get_current_num()
        q_log_current = self.get_q_state()['current']
        if compar_num is None:
            compar_num = q_log_current
        return q_nodes_current == q_log_current == compar_num

    def test_stale_file(self):
        f = self.lc.question_log.q_state_path

        is_stale = self.lc.is_stale_file(f, 0)
        self.assertFalse(is_stale)

        is_stale = self.lc.is_stale_file(f, -1)
        self.assertTrue(is_stale)

    def test_q_nodes(self):
        nodes = self.lc.question_nodes.question_nodes
        k = nodes.keys()
        self.assertTrue(len(k) > 120)
        self.assertTrue(self.is_q_match())

    def test_options(self):
        pass

    def test_invalid_options(self):

        print('\n----------------Running invalid inputs-------')
        print('Should print only invalid inputs\n\n')
        user_input = 'ahcd'
        self.lc.options(user_input)

        user_input = 'zef'
        self.lc.options(user_input)

        user_input = '!!!!!!____'
        self.lc.options(user_input)

        user_input = ''
        self.lc.options(user_input)

        user_input = '  '
        self.lc.options(user_input)
        time.sleep(3)

    def test_help_options(self):
        print('\n----------------Running help inputs-------')
        print('Should print help menu twice\n\n')
        user_input = '_help'
        self.lc.options(user_input)

        user_input = 'he#'
        self.lc.options(user_input)
        time.sleep(3)

    def test_disp_options(self):
        print('\n----------------Running display inputs-------')
        print('Should print different displays\n\n')

        user_input = 'dis$play'
        self.lc.options(user_input)

        user_input = 'dg 5'
        self.lc.options(user_input)

        user_input = 'de16'
        self.lc.options(user_input)

        user_input = 'dmed 30'
        self.lc.options(user_input)

        user_input = 'd hdf40'
        self.lc.options(user_input)

        user_input = 'd h400'
        self.lc.options(user_input)

        user_input = 'd e600'
        self.lc.options(user_input)

    def test_q_option(self):
        self.assertTrue(self.is_q_match(176))

        url_dic = self.get_q_state()['url']
        user_input = '178'
        self.lc.options(user_input)
        self.assertTrue(self.is_q_match(178))
        url1 = url_dic[178]

        #test going to the same problem
        user_input = 'q178'
        self.lc.options(user_input)
        self.assertTrue(self.is_q_match(178))

        user_input = 'que182'
        self.lc.options(user_input)
        self.assertTrue(self.is_q_match(182))

        #test the url hasn't changed after 178->182->178
        user_input = 'qekekrj178'
        self.lc.options(user_input)
        self.assertTrue(self.is_q_match(178))
        url2 = url_dic[178]
        self.assertEqual(url1, url2)

        #should not work
        user_input = '5110'
        self.assertTrue(self.is_q_match(178))

        #175 can't generate fiddles, so a url should not be created
        user_input = '175'
        self.lc.options(user_input)

        #The question node will still go to 175, but quesiton log will not because there is no valid url built
        self.assertEqual(self.lc.question_nodes.get_current_num(), 175)
        self.assertEqual(self.get_q_state()['current'], 178)
        self.assertTrue(175 not in url_dic.keys())

        user_input = '^qs511'
        self.lc.options(user_input)
        self.assertTrue(self.is_q_match(511))

    #def test_n_option(self):
        """
        starting at question 511
        """
        url_dic = self.get_q_state()['url']
        url1 = url_dic[511]

        user_input = 'n'
        self.lc.options(user_input)
        self.assertTrue(self.is_q_match(512))

        user_input = 'nh'
        self.lc.options(user_input)
        self.assertTrue(self.is_q_match(569))

        user_input = 'q262'
        self.lc.options(user_input)
        self.assertTrue(self.is_q_match(262))

        user_input = 'next'
        self.lc.options(user_input)
        self.assertTrue(self.is_q_match(511))
        url2 = url_dic[511]
        self.assertEqual(url1, url2)

        #test with multiple args, shoudl fail
        user_input = 'n  ^  m h'
        self.lc.options(user_input)
        self.assertTrue(self.is_q_match(511))

        #test with invalid arg, should fail
        user_input = 'n1'
        self.lc.options(user_input)
        self.assertTrue(self.is_q_match(511))

        #test with invalid arg, should fail
        user_input = 'nf'
        self.lc.options(user_input)
        self.assertTrue(self.is_q_match(511))

        # test same level using level arg
        user_input = 'n e  +'
        self.lc.options(user_input)
        self.assertTrue(self.is_q_match(512))

        #tests that last question to first question works
        last_question_num = self.lc.question_nodes.tail.number
        user_input = f'q{last_question_num}'
        self.lc.options(user_input)
        self.assertTrue(self.is_q_match(last_question_num))
        #check first question number
        first_question_num = self.lc.question_nodes.head.number
        self.assertEqual(first_question_num, 175)
        user_input = 'n'
        self.lc.options(user_input)
        #The curent question node pointer will still go to 175, but question log will not because url is not valid
        self.assertEqual(self.lc.question_nodes.get_current_num(), 175)

        #this should evaluate to nm (next medium)
        user_input = ' )n!@#$$%^& *m ('
        self.lc.options(user_input)
        self.assertTrue(self.is_q_match(177))


if __name__ == '__main__':
    unittest.main()

