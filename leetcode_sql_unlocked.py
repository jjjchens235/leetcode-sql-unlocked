'''
The main module that instantiates and controls the behavior and interaction of all objects, most notably objects from WebHandler, QuestionNodes, and QuestionLog.
'''
import os
import re
import time
import logging
import traceback
from datetime import datetime
from threading import Event

from selenium.common.exceptions import NoSuchWindowException, NoSuchElementException, WebDriverException

from src.help_menu import HelpMenu
from src.questions import QuestionNodes
from src.driver import Driver
from src.web_handler import WebHandler
from src.log import QuestionLog
from src.config import IS_PRE_LOAD_QUESTIONS, N_TO_PRELOAD, N_SAME_LEVEL_TO_PRELOAD
from src.exc_thread import ExcThread

class LeetcodeUnlocked():
    DRIVER_DIR = 'drivers'
    DRIVER = 'chromedriver'

    LOG_DIR = 'logs'
    ERROR_LOG = 'error.log'
    Q_ELEMENTS_LOG = 'q_elements.log'
    Q_STATE_LOG = 'q_state.log'

    def __init__(self, headless=False):
        self.create_dirs()
        self.start_error_logger()
        self.web_handler = self.get_web_handler(headless)
        self.question_log = self.get_question_logger()
        self.question_nodes = self.get_question_nodes()
        self.help_menu = self.get_help_menu()

        if IS_PRE_LOAD_QUESTIONS:
            self.stop_event = Event()
            self.threads = {'bg_child':None,'main_child':None}
            self.bg_web_handler = self.get_web_handler(headless=True)

    def create_dirs(self):
        try:
            os.chdir(os.path.dirname(os.path.realpath(__file__)))
            if not os.path.exists(self.DRIVER_DIR):
                os.mkdir(self.DRIVER_DIR)
            if not os.path.exists(self.LOG_DIR):
                os.mkdir(self.LOG_DIR)
        #running from shell, no __file__ var
        except NameError:
            print('CAUTION: __file__ variable could not be determined so directory check could not be completed')

    def start_error_logger(self):
        logging.basicConfig(level=logging.ERROR, format='%(message)s', filename=os.path.join(self.LOG_DIR, self.ERROR_LOG))

    def get_question_logger(self):
        question_log = QuestionLog(os.path.join(self.LOG_DIR, self.Q_ELEMENTS_LOG), os.path.join(self.LOG_DIR, self.Q_STATE_LOG))
        return question_log

    def get_web_handler(self, headless):
        driver_path = os.path.join(self.DRIVER_DIR, self.DRIVER)
        return WebHandler(Driver.get_driver(driver_path, headless))

    def get_question_nodes(self):
        '''
        Returns a QuestionNodes object, a data structure created for optimal question access.
        The QuestionNodes obj is created from question elements scraped from leetcode.
        These elements are not scraped each time the program is run.
        Rather, they are scraped if the elements don't exist, or
        when the elements need to be updated after a certain time period
        '''
        #dl questions list from leetcode if elements dont exist or stale
        if not os.path.exists(self.question_log.q_elements_path) or self.is_stale_file(self.question_log.q_elements_path):
            #if path exists, it must be a stale question list
            if os.path.exists(self.question_log.q_elements_path):
                print('\nQuestion list have not been updated recently. Will update from LeetCode in case there are any new problems')
            q_elements = self.web_handler.get_question_elements()
            self.question_log.write_dict(self.question_log.q_elements_path, q_elements)
        #don't re-download elements, read from q_elements log directly
        else:
            q_elements = self.question_log.q_elements
        return QuestionNodes(q_elements, self.question_log.q_state['current'])

    def get_help_menu(self):
        return HelpMenu(self.question_nodes.DEFAULT_NUM_TO_DISPLAY)

    @staticmethod
    def clean_user_input(user_input):
        '''
        cleans invalid characters from user input
        '''
        pattern = re.compile(r'[^A-Za-z0-9\s]+')
        sub = re.sub(pattern, '', user_input)
        return ' '.join(sub.split()).lower()

    @staticmethod
    def is_stale_file(file_path, days_till_stale=13):
        '''
        Used to determine whether or not questions list need to be updated from leetcode.com in case there are new questions. Default is to update every two weeks
        '''
        mtime = os.path.getmtime(file_path)
        return (datetime.now() - datetime.fromtimestamp(mtime)).days > days_till_stale

    @staticmethod
    def print_options(expr, sleep_time=1):
        print('\n'+ expr+ '\n')
        time.sleep(sleep_time)

    def join_bg_thread(self):
        if self.threads['bg_child'] is not None and self.threads['bg_child'].is_alive():
            print('\nWrapping up current question being pre-loaded')
            self.threads['bg_child'].join()

    def setup_preload(self):
        if self.threads['bg_child'] is not None:
            #tell preload thread to end
            self.stop_event.set()
            #wait for bg thread to wrap up the question it's currently on
            self.join_bg_thread()
        #preload thread can start over again when it is called since it the last thread has ended
        self.stop_event.clear()

    def open_preload(self, q_num):
        print('inside open_preload() about to open a question in webhandler')
        start_url = self.bg_web_handler.open_question(q_num)
        #check that the question still doesn't exist in the log before writing just the url to it
        if start_url is not None and not self.question_log.is_q_exist(q_num):
            self.question_log.update_q_url(q_num, start_url)
            self.question_log.write_dict(self.question_log.q_state_path, self.question_log.q_state)

    def close_preload(self):
        self.bg_web_handler.close_question()

    def preload(self, n_next=1, n_next_same_lvl=0):
        '''
        Headless web handler in the background to create db-fiddles for pre-loading.
        This will try to guarantee the next n questions are pre-loaded.
        However, if the question's db-fiddle already exists, no need to pre-load.
        Thread will be terminated if user goes to the next question before all n questions can be pre-loaded
        '''

        q_curr = self.question_nodes.get_current()
        next_q_nums = [q.number for q in self.question_nodes.get_next_n_nodes(n_next)]
        next_same_lvl_q_nums = [q.number for q in self.question_nodes.get_next_n_nodes(n_next_same_lvl, q_curr.level)]
        question_nums = list(set(next_q_nums + next_same_lvl_q_nums))
        #print(f'in preload, node(s) to be processed are {question_nums}')

        for q_num in question_nums:
            # if main thread is still running
            #and question has never been created
            if self.stop_event.is_set():
                return
            if not self.question_log.is_q_exist(q_num):
                self.open_preload(q_num)
                self.close_preload()

    def close_current_question(self):
        q_num = self.question_nodes.get_current_num()
        try:
            start_url = self.question_log.q_state['url'][q_num]
        #no valid url was created in open_new_questions()
        except:
            start_url = None
        end_url = self.web_handler.close_question()
        if end_url not in (None, 'https://www.db-fiddle.com/'):
            self.question_log.update_q_state(q_num, end_url)

    def open_new_question(self, q_num=None):
        if q_num is None:
            q_num = self.question_nodes.get_current_num()
        #print(f'inside open_new_question, q_num is {q_num}')
        try:
            prev_save_url = self.question_log.q_state['url'][q_num]
        except KeyError:
            prev_save_url = None
        start_url = self.web_handler.open_question(q_num, prev_save_url)
        if start_url is not None:
            self.question_log.update_q_state(q_num, start_url)
        else:
            print('\n\nCAUTION: For question {}, not able to parse tables from leetcode.jp'.format(q_num))

    def start_new_question(self, q_level=None, q_num=None):
        if IS_PRE_LOAD_QUESTIONS:
            self.setup_preload()

        self.close_current_question()
        #updates question current to the question the user chose
        if q_num is not None:
            self.question_nodes.select_question_by_number(q_num)
        else:
            self.question_nodes.select_next_question(q_level)

        print(f'inside start_new_question(), current num is {self.question_nodes.get_current_num()}')
        if IS_PRE_LOAD_QUESTIONS:
            self.threads['main_child'] = ExcThread(target=self.open_new_question)
            self.threads['bg_child'] = ExcThread(target=self.preload)
            self.threads['main_child'].start()
            self.threads['main_child'].join()
            self.threads['bg_child'].start()
        else:
            self.open_new_question()

    def next_option(self, user_input):
        '''
        if user selects next
        '''
        if user_input in ['ne', 'nm', 'nh']:
            user_input = ' '.join(user_input)
        user_inputs = user_input.split()
        if user_inputs[0] in ('n', 'next'):
            q_level = None
            #ignore q_level
            if len(user_inputs) == 1:
                self.print_options("You chose next question")
            #by q_level
            elif len(user_inputs) == 2:
                user_level = user_inputs[1]
                if user_level in ('e', 'easy'):
                    q_level = 'easy'
                elif user_level in ('m', 'medium'):
                    q_level = 'medium'
                elif user_level in ('h', 'hard'):
                    q_level = 'hard'
                else:
                    self.print_options("Invalid next command!! Do you want to go to next question? Either use 'n' or try by level i.e. 'n e' for next easy, 'n m', 'n h'")
                    return
                self.print_options("You chose next {q_level} question".format(q_level=q_level))
            else:
                self.print_options("Invalid input!! Too many arguments for next command. Either use 'n' or try by level i.e. 'n e' for next easy, 'n m', 'n h'")
                return

            self.start_new_question(q_level=q_level)

        #command starts with 'n', but not start with 'n' or 'next'
        else:
            self.print_options("Invalid input!! Do you want to go to next question? Either use 'n' or try by level i.e. 'n e' for next easy, 'n m', 'n h'")

    def question_by_number_option(self, user_input):
        '''
        Checks that the user input is a string that starts with q and ends with a number
        If the input is valid, change question to number inputted
        '''
        matches = re.match(r'[a-z\s]*(\d+)', user_input)
        if matches:
            q_num = int(matches.group(1))
            if self.question_nodes.is_q_exist(q_num):
                self.print_options('You chose question {q_num}'.format(q_num=q_num))
                self.start_new_question(q_num=q_num)
            else:
                self.print_options("Question number inputted is not on question list. Please enter valid question number, press 'd' to see list of questions",1.5)
        else:
            self.print_options("Invalid input. If you want to select by question number input 'q NUMBER'. Else if you want to quit, press 'e' to exit")

    def parse_display_args(self, user_input):
        '''
        Unsophisticated way of parsing out what display options the user wants. If the input starts with 'd', immediately assume its display. If the letters 'e','m','h' are included that means a level is being specified. Use regex to check if user specified n questions to display
        '''
        level_arg = None
        if 'm' in user_input:
            level_arg = 'medium'
        elif 'h' in user_input:
            level_arg = 'hard'
        elif 'e' in user_input:
            level_arg = 'easy'

        num_to_display_arg = None
        try:
            num_to_display_arg = int(re.search(r'\d+', user_input).group(0))
        except AttributeError:
            pass
        return level_arg, num_to_display_arg

    def display_questions_option(self, user_input):
        '''
        Main display method
        '''
        level_arg, num_to_display_arg = self.parse_display_args(user_input)
        print()
        self.question_nodes.display_questions(level_arg, num_to_display_arg)

    def solution_option(self):
        self.web_handler.open_solution_win(self.question_nodes.get_current())

    def exit(self, msg="Exiting program"):
        self.web_handler.close_all()
        if IS_PRE_LOAD_QUESTIONS:
            self.join_bg_thread()
            self.bg_web_handler.close_all()
        print(msg + '\n')
        return False

    def exit_option(self, msg="Exiting program"):
        '''
        If the user inputs 'e' into console, we can save the state of the question to the log before closing everything
        '''
        self.close_current_question()
        return self.exit(msg)

    def get_user_input(self):
        user_input = input("\n\n----------------------------------------\nYou are on {name}\n\nWhat would you like to do next?\nType 'n' for next problem, 'h' for more help/options, 'e' to exit\n".format(name=self.question_nodes.get_current().name))
        return user_input

    def load_option():
        pass

    def options(self, user_input):
        '''
        handles user input
        '''
        user_input = self.clean_user_input(user_input)
        #if input is numbers only, this will be treated as question # arg
        is_num_only = re.match(r'[1-9]\d{2,3}$', user_input) is not None
        valid_start_inputs = ['h', 'n', 'q', 's', 'd', 'e']
        try:
            start_input = user_input[0]
        #empty user input
        except:
            self.print_options('Invalid input')
            return True

        if start_input in valid_start_inputs or is_num_only:
            if start_input == 'h':
                self.help_menu.print_help()

            elif start_input == 'n':
                self.next_option(user_input)

            elif start_input == 'q' or is_num_only:
                if user_input == ('q'):
                    self.print_options("Invalid input. If you want to select by question number input 'q NUMBER'. Else if you want to quit, press 'e' to exit")
                elif user_input == ('quit'):
                    return self.exit_option()
                else:
                    self.question_by_number_option(user_input)
            elif start_input == 's':
                self.solution_option()
            elif start_input == 'd':
                self.display_questions_option(user_input)
            elif start_input == 'e':
                if user_input in ('e', 'exit'):
                    return self.exit_option()
                else:
                    self.print_options('Invalid input')
        #does not start with valid char
        else:
            self.print_options('Invalid input!')
        return True

    def main(self):
        try:
            #self.open_new_question()
            print(f'question node current num in main is: {self.question_nodes.get_current_num()}')
            self.start_new_question(q_num=self.question_nodes.get_current_num())
            is_continue = True
            tb = None
            while is_continue:
                is_continue = self.options(self.get_user_input())

        except (NoSuchWindowException, WebDriverException):
            tb = traceback.format_exc()
            msg =  'Lost connection with browser, exiting now'
        except NoSuchElementException:
            tb = traceback.format_exc()
            msg = 'Web element not found, exiting now'
        except:
            tb = traceback.format_exc()
            msg =  'Uncaught exc, check logs/error.log, exiting now'
        finally:
            if tb:
                now = datetime.now().strftime("\n%Y-%m-%d %H:%M:%S ")
                logging.exception(now + msg + '\n' + tb)
                is_continue = self.exit(msg)

if __name__ == '__main__':
    lc = LeetcodeUnlocked()
    lc.main()
