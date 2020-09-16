'''
The main module that instantiates and controls the behavior and interaction of all objects, most notably objects from WebHandler, QuestionNodes, and QuestionLog.
'''
import os
import re
import time
from datetime import datetime
from threading import Event

from .config import cfg
from .help_menu import HelpMenu
from .questions import QuestionNodes
from .driver import Driver
from .web_handler import WebHandler
from .log import QuestionLog
from .exc_thread import ExcThread

class Leetcode():

    def __init__(self, driver_path, q_elements_path, q_state_path, q_public_urls_path, headless=False):
        self.cfg = cfg
        self.driver_path = driver_path
        self.web_handler = WebHandler(self.driver_path, headless)
        self.question_log = QuestionLog(q_elements_path, q_state_path, q_public_urls_path)

        def is_stale_elements(elements_path, days_till_stale=13):
            mtime = os.path.getmtime(elements_path)
            return (datetime.now() - datetime.fromtimestamp(mtime)).days > days_till_stale

        if not os.path.exists(q_elements_path) or is_stale_elements(q_elements_path):
            #if path exists, it must be a stale question list
            if os.path.exists(q_elements_path):
                print('\nQuestion list have not been updated recently. Will update from LeetCode in case there are any new problems')
            q_elements = self.web_handler.get_question_elements()
            self.question_log.write_dict(q_elements_path, q_elements)
        #don't re-download elements, read from q_elements log directly
        else:
            q_elements = self.question_log.q_elements
        self.question_nodes = QuestionNodes(q_elements, self.question_log.q_state['current'])

        if self.cfg['is_preload']:
            self.__turn_on_preloading()

    def get_current_q(self):
        '''
        Get the current question node object
        '''
        return self.question_nodes.get_current()

    def get_current_q_num(self):
        '''
        Get the current question nodes number
        '''
        return self.question_nodes.get_current_num()

    def preload_finish(self):
        '''
        Turn on stop event so that main preload method will stop creating
        new db-fiddles.
        Join() waits for the preload method to finish its current
        db-fiddle, before opening a new question in main thread.
        Even if the thread is already finished, call join() for exec info.
        '''
        #tell preload thread to end
        if self.preloader.thread is not None:
            if self.preloader.thread.is_alive():
               self.preloader.stop_event.set()
               print('\nWrapping up current question being pre-loaded')
            #wait for preload thread to finish its current question
            self.preloader.thread.join()
            self.preloader.stop_event.clear()

    def preload_delay(self, question_index):
        '''
        Based on number of questions to preload, delay processing the next pre-loaded question so as not to send too much traffic at one time to external website
        '''
        if question_index <= 5:
            return
        elif question_index <= 15:
            delay = 10
        elif question_index <= 40:
            delay = 30
        else:
            delay = 45
        self.preloader.stop_event.wait(delay)

    def preload_open_question(self, q_num):
        if self.check_is_forkable(q_num):
            public_url = self.question_log.q_public_urls[q_num]
            start_url = self.preloader.web_handler.open_fork(q_num, public_url)
        else:
            start_url = self.preloader.web_handler.open_question(q_num, self.cfg['db_engine'], self.cfg['is_check_new_save_versions'])
        #check that the question still doesn't exist in the log before writing just the url to it
        if start_url is not None and not self.question_log.is_q_exist(q_num):
            self.question_log.update_q_url(q_num, start_url)
            self.question_log.write_dict(self.question_log.q_state_path, self.question_log.q_state)

    def preload_close_question(self):
        self.preloader.web_handler.close_question(is_save_before_closing=False)

    def preload_question(self, q_num):
        self.preload_open_question(q_num)
        self.preload_close_question()

    def preload(self, n_next, n_next_same_lvl):
        '''
        Headless web handler in the background to create db-fiddles for pre-loading.
        This will try to guarantee the next n questions are pre-loaded.
        However, if the question's db-fiddle already exists, no need to pre-load.
        If user selects another question before all n questions can be pre-loaded, thread will be terminated after the current question being preloaded is finished
        '''
        q_curr = self.get_current_q()
        next_q_nums = [q.number for q in self.question_nodes.get_next_n_nodes(n_next)]
        next_same_lvl_q_nums = [q.number for q in self.question_nodes.get_next_n_nodes(n_next_same_lvl, q_curr.level)]
        question_nums = sorted(set(next_q_nums + next_same_lvl_q_nums))
        question_nums = [q_num for q_num in question_nums if not self.question_log.is_q_exist(q_num) and q_num != 175]
        #print(f'in preload, node(s) to be processed are {question_nums}')

        for i, q_num in enumerate(question_nums):
            # if main thread is still running
            #and question has never been created
            if self.preloader.stop_event.is_set():
                return
            self.preload_question(q_num)
            self.preload_delay(i)
        if len(question_nums) > 5:
            print('FYI, current batch of questions have finished preloading')

    def close_current_question(self):
        q_num = self.get_current_q_num()
        try:
            start_url = self.question_log.q_state['url'][q_num]
        #no valid url was created in open_new_questions()
        except:
            start_url = None
        end_url = self.web_handler.close_question(self.cfg['is_save_before_closing'])
        if end_url not in (None, 'https://www.db-fiddle.com/'):
            self.question_log.update_q_state(q_num, end_url)

    def check_is_forkable(self, q_num):
        '''
        Check that
        1) the question has not been saved to the personal state log yet.
        2) The question has a public url to fork
        3) The user wants to fork an exiting public url
        '''
        cond1 = not self.question_log.is_q_exist(q_num)
        cond2 = self.question_log.is_q_public_exist(q_num)
        cond3 = self.cfg['is_fork_public_url']
        if cond1 and cond2 and cond3:
            return True
        return False

    def open_new_question(self, q_num=None):
        if q_num is None:
            q_num = self.get_current_q_num()
        #print(f'inside open_new_question, q_num is {q_num}')
        try:
            prev_save_url = self.question_log.q_state['url'][q_num]
        except KeyError:
            prev_save_url = None

        if self.check_is_forkable(q_num):
            public_url = self.question_log.q_public_urls[q_num]
            start_url = self.web_handler.open_fork(q_num, public_url)
        else:
            start_url = self.web_handler.open_question(q_num, self.cfg['db_engine'], self.cfg['is_check_new_save_versions'], prev_save_url)

        if start_url is not None:
            self.question_log.update_q_state(q_num, start_url)
        else:
            print('\n\nCAUTION: For question {}, not able to parse tables from leetcode.jp'.format(q_num))

        if self.__is_preload_questions:
            #start preloading now that user selected question is loaded
            self.preloader.thread = ExcThread(target=self.preload, args=(self.cfg['n_to_preload'], self.cfg['n_same_level_to_preload']))
            self.preloader.thread.start()

    def start_new_question(self, q_level=None, q_num=None):
        if self.__is_preload_questions:
            self.preload_finish()

        self.close_current_question()
        #updates question current to the question the user chose
        if q_num is not None:
            self.question_nodes.select_question_by_number(q_num)
        else:
            self.question_nodes.select_next_question(q_level)
        self.open_new_question()

    @staticmethod
    def print_options(expr, sleep_time=1):
        print('\n'+ expr+ '\n')
        time.sleep(sleep_time)

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

    def help_option(self):
        h = HelpMenu(self.question_nodes.DEFAULT_NUM_TO_DISPLAY)
        h.print_help()

    def solution_option(self):
        self.web_handler.open_solution_win(self.get_current_q())

    def __turn_off_preloading(self):
        self.preload_finish()
        self.__is_preload_questions = False

    def turn_off_preloading(self):
        self.print_options('Turning OFF question loading for the duration of this program.')
        if self.__is_preload_questions:
            self.__turn_off_preloading()

    class Preloader:
        def __init__(self, thread, web_handler):
            self.thread = thread
            self.web_handler = web_handler
            self.stop_event = Event()

    def __turn_on_preloading(self):
        self.__is_preload_questions = True
        if not hasattr(self, 'preloader'):
            self.preloader = self.Preloader(thread=None, web_handler=WebHandler(self.driver_path, headless=True))

    def turn_on_preloading(self):
        #possibilities, load has never been turned on
        # load was previously off but was turned on at one point
        #load was previously on
        self.print_options('Turning ON question loading for the duration of this program.')
        if not self.__is_preload_questions:
            self.__turn_on_preloading()

    def preload_option(self, user_input):
        if 'on' in user_input:
            self.turn_on_preloading()
        elif 'off' in user_input:
            self.turn_off_preloading()
        return True

    def __exit(self, msg="Exiting program"):
        self.web_handler.close_all()
        if self.__is_preload_questions:
            self.preload_finish()
        if hasattr(self, 'preload_thread'):
            self.preloader.web_handler.close_all()
        print(msg + '\n')
        return False

    def exit_option(self, msg="Exiting program"):
        '''
        If the user inputs 'e' into console, we can save the state of the question to the log before closing everything
        '''
        try:
            self.close_current_question()
        except:
            pass
        return self.__exit(msg)

    def get_user_input(self):
        user_input = input("\n\n----------------------------------------\nYou are on {name}\n\nWhat would you like to do next?\nType 'n' for next problem, 'h' for more help/options, 'e' to exit\n".format(name=self.get_current_q().name))
        return user_input

    @staticmethod
    def clean_user_input(user_input):
        '''
        cleans invalid characters from user input
        '''
        pattern = re.compile(r'[^A-Za-z0-9\s]+')
        sub = re.sub(pattern, '', user_input)
        return ' '.join(sub.split()).lower()

    def options(self, user_input):
        '''
        handles user input
        '''
        user_input = self.clean_user_input(user_input)
        #if input is numbers only, this will be treated as question # arg
        is_num_only = re.match(r'[1-9]\d{2,3}$', user_input) is not None
        valid_start_inputs = ['h', 'n', 'q', 's', 'd', 'l', 'e']
        try:
            start_input = user_input[0]
        #empty user input
        except:
            self.print_options('Invalid input')
            return True

        if start_input in valid_start_inputs or is_num_only:
            if start_input == 'h':
                self.help_option()

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
            elif start_input == 'l':
                if 'on' in user_input or 'off' in user_input:
                    return self.preload_option(user_input)
                else:
                    self.print_options('Invalid input')
            elif start_input == 'e':
                if user_input in ('e', 'exit'):
                    return self.exit_option()
                else:
                    self.print_options('Invalid input')
        #does not start with valid char
        else:
            self.print_options('Invalid input!')
        return True
