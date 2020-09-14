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
sister_dir = os.path.join(parent_dir, 'leetcode_sql_unlocked/')
os.sys.path.insert(0, sister_dir)
import leetcode_sql_unlocked

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
        #os.chdir(sister_dir)
        curr_log_dir = os.path.join(sister_dir, 'logs')
        curr_driver_dir = os.path.join(sister_dir, 'drivers')
        archive_log_dir = os.path.join(sister_dir, 'logs_archive')
        if os.path.exists(curr_log_dir):
            move_to_archive(curr_log_dir, archive_log_dir)
            remove(curr_log_dir)
        if os.path.exists(curr_driver_dir):
            remove(curr_driver_dir)
        self.lc = leetcode_sql_unlocked.get_leetcode(headless=False)
        self.lc.options('loff')

    @classmethod
    def tearDownClass(self):
        self.lc.exit_option()

    def options_with_join(self, user_input):
        self.lc.options(user_input)
        self.lc.preloader.thread.join()

    def options(self, user_input):
        self.lc.options(user_input)

    def get_q_state(self):
        return self.lc.question_log.q_state

    def is_current_question_match(self, compar_num=None):
        '''
        Checks if question node current number and q log current number are the same
        Optionally, can compare a third expected number, compar_num
        '''
        q_nodes_current = self.lc.question_nodes.get_current_num()
        q_log_current = self.get_q_state()['current']
        if compar_num is None:
            compar_num = q_log_current
        return q_nodes_current == q_log_current == compar_num

    def in_url_keys(self, match_nums):
        url_nums = self.get_q_state()['url'].keys()
        return all(i in url_nums for i in match_nums)

    '''
    def test_stale_file(self):
        print('\n\n Testing stale files!')
        f = self.lc.question_log.q_state_path

        is_stale = self.lc.is_stale_elements(f, 0)
        self.assertFalse(is_stale)

        is_stale = self.lc.is_stale_elements(f, -1)
        self.assertTrue(is_stale)
    '''

    def test_q_nodes(self):
        #nodes = self.lc.question_nodes.question_nodes
        nodes = self.lc.question_nodes._QuestionNodes__question_nodes
        k = nodes.keys()
        self.assertTrue(len(k) > 120)
        self.assertTrue(self.is_current_question_match())

    def test_q_option(self):
        self.assertTrue(self.is_current_question_match(176))

        url_dic = self.get_q_state()['url']
        user_input = '178'
        self.options(user_input)
        self.assertTrue(self.is_current_question_match(178))
        url1 = url_dic[178]
        time.sleep(30)

        #test going to the same problem
        user_input = 'q178'
        self.options(user_input)
        self.assertTrue(self.is_current_question_match(178))

        user_input = 'que182'
        self.options(user_input)
        self.assertTrue(self.is_current_question_match(182))

        #test the url hasn't changed after 178->182->178
        user_input = 'qekekrj178'
        self.options(user_input)
        self.assertTrue(self.is_current_question_match(178))
        url2 = url_dic[178]
        self.assertEqual(url1, url2)

        #should not work
        user_input = '5110'
        self.assertTrue(self.is_current_question_match(178))

        #175 can't generate fiddles, so a url should not be created
        user_input = '175'
        self.options(user_input)

        #The question node will still go to 175, but quesiton log will not because there is no valid url built
        self.assertEqual(self.lc.question_nodes.get_current_num(), 175)
        self.assertEqual(self.get_q_state()['current'], 178)
        self.assertTrue(175 not in url_dic.keys())

        user_input = '^qs511'
        self.options(user_input)
        self.assertTrue(self.is_current_question_match(511))

    #def test_n_option(self):
        """
        starting at question 511
        """
        url_dic = self.get_q_state()['url']
        url1 = url_dic[511]

        user_input = 'n'
        self.options(user_input)
        self.assertTrue(self.is_current_question_match(512))

        user_input = 'nh'
        self.options(user_input)
        self.assertTrue(self.is_current_question_match(569))

        user_input = 'q262'
        self.options(user_input)
        self.assertTrue(self.is_current_question_match(262))

        user_input = 'next'
        self.options(user_input)
        self.assertTrue(self.is_current_question_match(511))
        url2 = url_dic[511]
        self.assertEqual(url1, url2)

        #test with multiple args, shoudl fail
        user_input = 'n  ^  m h'
        self.options(user_input)
        self.assertTrue(self.is_current_question_match(511))

        #test with invalid arg, should fail
        user_input = 'n1'
        self.options(user_input)
        self.assertTrue(self.is_current_question_match(511))

        #test with invalid arg, should fail
        user_input = 'nf'
        self.options(user_input)
        self.assertTrue(self.is_current_question_match(511))

        # test same level using level arg
        user_input = 'n e  +'
        self.options(user_input)
        self.assertTrue(self.is_current_question_match(512))

        #tests that last question to first question works
        last_question_num = self.lc.question_nodes.tail.number
        user_input = f'q{last_question_num}'
        self.options(user_input)
        self.assertTrue(self.is_current_question_match(last_question_num))
        #check first question number
        first_question_num = self.lc.question_nodes.head.number
        self.assertEqual(first_question_num, 175)
        user_input = 'n'
        self.options(user_input)
        #The curent question node pointer will still go to 175, but question log will not because url is not valid
        self.assertEqual(self.lc.question_nodes.get_current_num(), 175)

        #this should evaluate to nm (next medium)
        user_input = ' )n!@#$$%^& *m ('
        self.options(user_input)
        self.assertTrue(self.is_current_question_match(177))

        #------- Preloading  testing ---------
        self.options('load on')

        #check that both preload questions were loaded, and that current still points to 512
        user_input = '512'
        self.options_with_join(user_input)
        q_num = int(user_input)
        self.assertTrue(self.in_url_keys([q_num, 534, 577]))
        self.assertTrue(self.is_current_question_match(q_num))

        #while preload originally includes both 578 and 584, when turning load off, only the current preloaded question (578) should be finished
        user_input = '577'
        self.options(user_input)
        q_num = int(user_input)
        self.assertTrue(self.is_current_question_match(q_num))
        self.options('load off')
        self.assertTrue(self.in_url_keys([q_num, 578]))
        self.assertFalse(self.in_url_keys([584]))

        #Check that after turning load off, that after user goes to 578, nothing is loaded in the background
        url_keys = self.get_q_state()['url'].keys()
        len1 = len(url_keys)
        user_input = '578'
        self.options(user_input)
        q_num = int(user_input)
        self.assertTrue(self.is_current_question_match(q_num))
        len2 = len(url_keys)
        self.assertTrue(len1 == len2)

        #Check that after going to 579, url dictionary only increaed by one, similiar to the check above
        user_input = '579'
        self.options(user_input)
        q_num = int(user_input)
        self.assertTrue(self.is_current_question_match(q_num))
        len3 = len(url_keys)
        self.assertTrue(len1 == len3-1)

        #turn load back on, go to 586, testing if preload is only 1 problem since it happens to be both the next problem, and the next level problem
        self.options('load on')
        user_input = '586'
        self.options_with_join(user_input)
        q_num = int(user_input)
        self.assertTrue(self.is_current_question_match(q_num))
        self.assertTrue(self.in_url_keys([q_num, 595]))
        #dictionary size should increase by 2, for the new current problem, and the one preloaded problem
        self.assertTrue(len(url_keys) == len3+2)

        #turn load off to setup a bigger preload
        self.options('load off')
        user_input = '601'
        self.options_with_join(user_input)

        #preload 3 next, and 3 next same level problems
        self.options('load on')
        self.lc.preload(3, 3)
        #the preloaded problems should match these 6 hardcoded ones
        self.assertTrue(self.in_url_keys([602, 603, 607, 615, 618, 1097]))
        q_num = int(user_input)
        self.assertTrue(self.is_current_question_match(q_num))

        #make sure regular loading, and preloading are working fine after running preload on its own
        user_input = '1097'
        self.options_with_join(user_input)
        self.assertTrue(self.in_url_keys([1097, 1098, 1127]))
        q_num = int(user_input)
        self.assertTrue(self.is_current_question_match(q_num))

if __name__ == '__main__':
    unittest.main()

