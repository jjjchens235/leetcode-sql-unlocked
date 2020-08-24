import os
import re
import time
import logging
import traceback
from datetime import datetime
from selenium.common.exceptions import NoSuchWindowException, NoSuchElementException, WebDriverException
from src.help_menu import HelpMenu
from src.questions import QuestionDirectory
from src.driver import Driver
from src.web_handler import WebHandler
from src.log import QuestionLog

def clean_user_input(user_input):
    '''
    cleans invalid characters from user input
    '''
    pattern = re.compile(r'[^\w\s]+')
    sub = re.sub(pattern, '', user_input)
    return ' '.join(sub.split()).lower()

def is_stale_file(file_path, days_till_stale=13):
    '''
    Used to determine whether or not questions list need to be updated from leetcode.com in case there are new questions. Default is to update every two weeks
    '''
    mtime = os.path.getmtime(file_path)
    return (datetime.now() - datetime.fromtimestamp(mtime)).days > days_till_stale

def print_options(s, n_sleep=1):
    print('\n'+ s+ '\n')
    time.sleep(n_sleep)

def close_question(q_num, web_handler, q_log):
    try:
        start_url = q_log.q_state['url'][q_num]
    #no valid url was created in open_questions()
    except:
        start_url = None
    end_url = web_handler.close_question()
    if start_url is not None and end_url not in [None, 'https://www.db-fiddle.com/']:
        q_log.update_q_state(q_num, end_url)

def open_question(q_num, web_handler, q_log):
    try:
        prev_save_url = q_log.q_state['url'][q_num]
    except KeyError:
        prev_save_url = None
    start_url = web_handler.open_question(q_num, prev_save_url)
    if start_url is not None:
        q_log.update_q_state(q_num, start_url)
    else:
        print('\n\nCAUTION: For question {}, not able to parse tables from leetcode.jp'.format(q_num))

def next_option(user_input, question_dir, q_log, web_handler):
    '''
    if user selects next
    '''
    if user_input in ['ne', 'nm', 'nh']:
        user_input = ' '.join(user_input)
    user_inputs = user_input.split()
    if user_inputs[0] in ('n', 'next'):
        level = None
        #ignore level
        if len(user_inputs) == 1:
            print_options("You chose next question")
        #by level
        elif len(user_inputs) == 2:
            user_level = user_inputs[1]
            if user_level in ('e', 'easy'):
                level = 'easy'
            elif user_level in ('m', 'medium'):
                level = 'medium'
            elif user_level in ('h', 'hard'):
                level = 'hard'
            else:
                print_options("Invalid next command!! Do you want to go to next question? Either use 'n' or try by level i.e. 'n e' for next easy, 'n m', 'n h'")
                return
            print_options("You chose next {level} question".format(level=level))
        else:
            print_options("Invalid input!! Too many arguments for next command. Either use 'n' or try by level i.e. 'n e' for next easy, 'n m', 'n h'")
            return

        close_question(question_dir.get_current_num(), web_handler, q_log)
        question_dir.select_next_question(level)
        open_question(question_dir.get_current_num(), web_handler, q_log)

    #command starts with 'n', but not start with 'n' or 'next'
    else:
        print_options("Invalid input!! Do you want to go to next question? Either use 'n' or try by level i.e. 'n e' for next easy, 'n m', 'n h'")

def question_by_number_option(user_input, question_dir, q_log, web_handler):
    '''
    Checks that the user input is a string that starts with q and ends with a number
    If the input is valid, change question to number inputted
    '''
    matches = re.match(r'[a-z\s]*(\d+)', user_input)
    if matches:
        q_num = int(matches.group(1))
        if question_dir.is_q_exist(q_num):
            close_question(question_dir.get_current_num(), web_handler, q_log)
            question_dir.select_question_by_number(q_num)
            open_question(question_dir.get_current_num(), web_handler, q_log)
        else:
            print_options("Question number inputted is not on question list. Please enter valid question number, press 'd' to see list of questions",1.5)
    else:
        print_options("Invalid input. If you want to select by question number input 'q NUMBER'. Else if you want to quit, press 'e' to exit")

def parse_display_args(user_input):
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

def display_questions_option(user_input, question_dir):
    '''
    Main display method
    '''
    level_arg, num_to_display_arg = parse_display_args(user_input)
    print()
    question_dir.display_questions(level_arg, num_to_display_arg)

def solution_option(web_handler, q_num):
    web_handler.open_solution_win(q_num)

def exit(web_handler, msg):
    web_handler.close_all()
    print(msg + '\n')
    return False

def exit_option(q_num, web_handler, q_log, msg="Exiting program"):
    '''
    If the user inputs 'e' into console, we can save the state of the question to the log before closing everything
    '''
    close_question(q_num, web_handler, q_log)
    return exit(web_handler, msg)

def options(user_input, question_dir, q_log, web_handler):
    '''
    handles user input
    '''

    #if input is numbers only, this will be treated as question # arg
    is_num_only = re.match(r'[1-9]\d{2,3}$', user_input) is not None
    valid_start_inputs = ['h', 'n', 'q', 's', 'd', 'e']
    try:
        start_input = user_input[0]
    except:
        print_options('Invalid input')
        return True

    if start_input in valid_start_inputs or is_num_only:
        if start_input == 'h':
            help_menu.print_help()

        elif start_input == 'n':
            next_option(user_input, question_dir, q_log, web_handler)

        elif start_input == 'q' or is_num_only:
            if user_input == ('q'):
                print_options("Invalid input. If you want to select by question number input 'q NUMBER'. Else if you want to quit, press 'e' to exit")
            elif user_input == ('quit'):
                return exit_option(question_dir.get_current_num(), web_handler, q_log)
            else:
                question_by_number_option(user_input, question_dir, q_log, web_handler)
        elif start_input == 's':
            solution_option(web_handler, question_dir.get_current())
        elif start_input == 'd':
            display_questions_option(user_input, question_dir)
        elif start_input == 'e':
            if user_input in ('e', 'exit'):
                return exit_option(question_dir.get_current_num(), web_handler, q_log)
            else:
                print_options('Invalid input')
    #does not start with valid char
    else:
        print_options('Invalid input!')
    return True


DRIVER_DIR = 'drivers'
DRIVER = 'chromedriver'

LOG_DIR = 'logs'
ERROR_LOG = 'error.log'
Q_ELEMENTS_LOG = 'q_elements.log'
Q_STATE_LOG = 'q_state.log'

os.chdir(os.path.dirname(os.path.realpath(__file__)))
if not os.path.exists(DRIVER_DIR):
    os.mkdir(DRIVER_DIR)

if not os.path.exists(LOG_DIR):
    os.mkdir(LOG_DIR)

logging.basicConfig(level=logging.ERROR, format='%(message)s', filename=os.path.join(LOG_DIR, ERROR_LOG))

driver_path = os.path.join('drivers','chromedriver')
web_handler = WebHandler(Driver.get_driver(driver_path))
q_log = QuestionLog(os.path.join(LOG_DIR, Q_ELEMENTS_LOG), os.path.join(LOG_DIR, Q_STATE_LOG))

if  not os.path.exists(q_log.q_elements_path) or is_stale_file(q_log.q_elements_path):
    q_elements = web_handler.get_question_elements()
    q_log.write_dict(q_log.q_elements_path, q_elements)
else:
    q_elements = q_log.q_elements

q_dir = QuestionDirectory(q_elements, q_log.q_state['current'])
help_menu = HelpMenu(q_dir.DEFAULT_NUM_TO_DISPLAY)
open_question(q_dir.get_current_num(), web_handler, q_log)

is_continue = True
tb = None
while is_continue:
    user_input = clean_user_input(input("\n\n----------------------------------------\nYou are on {name}\n\nWhat would you like to do next?\nType 'n' for next problem, 'h' for more help/options, 'e' to exit\n".format(name=q_dir.get_current().name)))
    try:
        is_continue = options(user_input, q_dir, q_log, web_handler)
    except (NoSuchWindowException, WebDriverException):
        tb = traceback.format_exc()
        msg =  'Browser was already closed by user, exiting now'
    except NoSuchElementException:
        tb = traceback.format_exc()
        msg = 'Web element not found, exiting now'
    except:
        tb = traceback.format_exc()
        msg =  'Uncaught exc, check log, exiting now'
    finally:
        if tb:
            now = datetime.now().strftime("\n%Y-%m-%d %H:%M:%S ")
            logging.exception(now + msg + '\n' + tb)
            is_continue = exit(web_handler, msg)


