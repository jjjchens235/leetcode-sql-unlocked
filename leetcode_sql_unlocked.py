from help_menu import HelpMenu
from questions import QuestionDirectory
from driver import Driver
from web_handler import WebHandler
from log import HistLog
import os
import re
import time
from datetime import datetime
from selenium.common.exceptions import NoSuchWindowException, WebDriverException
import logging

def temp_get_questions():
    import ast
    file = open("/Users/jwong/Cabinet/out/questions_dict.txt", "r")
    contents = file.read()
    return ast.literal_eval(contents)

def test_regex(user_input):
    user_input = '(h)ello.   worlD'
    pattern = re.compile(r'[A-Za-z0-9\s]+')
    sub = re.sub(pattern, '', user_input)
    ' '.join(sub.split()).lower()

def clean_user_input(user_input):
    '''
    removes all whitespace except regular space character, also removes parenthesis
    '''
    #pattern = re.compile(r'[\t\n\r\(\)]+')
    #sub = re.sub(pattern, '', user_input)
    #return ' '.join(sub.split()).lower()
    pattern = re.compile(r'[^A-Za-z0-9\s]+')
    sub = re.sub(pattern, '', user_input)
    return ' '.join(sub.split()).lower()

def is_stale_file(file_path, days_till_stale=13):
    mtime = os.path.getmtime(file_path) 
    return (datetime.now() - datetime.fromtimestamp(mtime)).days > days_till_stale

def print_options(s, n_sleep=1):
    print('\n')
    print(s)
    print('\n')
    time.sleep(n_sleep)

def close_question(q_num, web_handler, hist_log):
    end_url = web_handler.close_question()
    if end_url is not None:
        hist_log.update_q_state(q_num, end_url)

def open_question(q_num, web_handler, hist_log):
    try:
        prev_save_url = hist_log.q_state['url'][q_num]
    except KeyError:
        prev_save_url = None
    start_url = web_handler.open_question(q_num, prev_save_url)
    hist_log.update_q_state(q_num, start_url)

def next_option(user_input, question_dir, hist_log, web_handler):
    if user_input in ['ne', 'nm', 'nh']:
        user_input = ' '.join(user_input)
    user_inputs = user_input.split()
    if user_inputs[0] in ('n', 'next'):
        if len(user_inputs) == 1:
            print_options("You chose next question")
        elif len(user_inputs) == 2:
            #by level
            user_level = user_inputs[1]
            level = None
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

        close_question(question_dir.get_current_num(), web_handler, hist_log)
        question_dir.select_next_question()
        open_question(question_dir.get_current_num(), web_handler, hist_log)
    #command starts with 'n', but not start with 'n' or 'next'
    else:
        print_options("Invalid input!! Do you want to go to next question? Either use 'n' or try by level i.e. 'n e' for next easy, 'n m', 'n h'")

def question_by_number_option(user_input, question_dir, hist_log, web_handler):
    '''
    Checks that the user input is a string that starts with q and ends with a number
    If the input is valid, change question to number inputted
    '''
    pattern = re.compile(r'q[a-z\s]*\d+')
    matches = pattern.findall(user_input)
    if len(matches) > 0:
        pattern = re.compile(r'\d+')
        q_num = int(pattern.findall(matches[0])[0])
        if question_dir.is_q_exist(q_num):
            close_question(question_dir.get_current_num(), web_handler, hist_log)
            question_dir.select_question_by_number(q_num)
            open_question(question_dir.get_current_num(), web_handler, hist_log)
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
    pattern = re.compile(r'\d+')
    nums_to_display = pattern.findall(user_input)
    if len(nums_to_display) > 0:
        num_to_display_arg = int(nums_to_display[0])
    return level_arg, num_to_display_arg
    
def display_questions_option(user_input, question_dir):
    level_arg, num_to_display_arg = parse_display_args(user_input)
    print('\n')
    question_dir.display_questions(level_arg, num_to_display_arg)

def solution_option(web_handler, q_num):
    web_handler.open_solution_win(q_num)

def exit(web_handler, msg):
    web_handler.close_all()
    print(msg + '\n')
    return False

def exit_option(q_num, web_handler, hist_log, msg="Exiting program"):
    '''
    If the user inputs 'e' into console, we can save the state of the question to the log before closing everything
    '''
    close_question(q_num, web_handler, hist_log)
    return exit(web_handler, msg)

def options(user_input, question_dir, hist_log, web_handler):

        valid_start_inputs = ['h', 'n', 'q', 's', 'd', 'e']
        try:
            start_input = user_input[0]
        except:
            print('Invalid input')
            return True
        if start_input in valid_start_inputs:
            if start_input == 'h':
                if user_input in ('h', 'help'):
                    help_menu.print_help()
            elif start_input == 'n':
                next_option(user_input, question_dir, hist_log, web_handler)
                            
            elif start_input == 'q':
                if user_input == ('q'):
                    print_options("Invalid input. If you want to select by question number input 'q NUMBER'. Else if you want to quit, press 'e' to exit")
                elif user_input == ('quit'):
                    return exit_option(question_dir.get_current_num(), web_handler, hist_log)
                else:
                    question_by_number_option(user_input, question_dir, hist_log, web_handler)
            elif start_input == 's':
                solution_option(web_handler, question_dir.get_current_number())
            elif start_input == 'd':
                display_questions_option(user_input, question_dir)
            elif start_input == 'e':
                if user_input in ('e', 'exit'):
                    #close_question(question_dir.get_current_num(), web_handler, hist_log)
                    #web_handler.close_all()
                    return exit_option(question_dir.get_current_num(), web_handler, hist_log)
                else:
                    print_options('Invalid input')
        else:
            print_options('Invalid input!')
        return True


DRIVER_DIR = 'drivers'
DRIVER = 'chromedriver'
LOG_DIR = 'logs'
ERROR_LOG = 'error.log'
Q_ELEMENTS_LOG = 'q_elements.log'
Q_STATE_LOG = 'q_state.log'

if not os.path.exists(DRIVER_DIR):
    os.mkdir(DRIVER_DIR)

if not os.path.exists(LOG_DIR):
    os.mkdir(LOG_DIR)

logging.basicConfig(level=logging.ERROR, format='%(asctime)s:%(message)s', filename=os.path.join(LOG_DIR, ERROR_LOG))

driver_path = os.path.join('drivers','chromedriver') 
web_handler = WebHandler(Driver.get_driver(driver_path))
hist_log = HistLog(os.path.join(LOG_DIR, Q_ELEMENTS_LOG), os.path.join(LOG_DIR, Q_STATE_LOG))

if not os.path.exists(hist_log.q_elements_path) or is_stale_file(hist_log.q_elements_path):
    q_elements = web_handler.get_question_elements()
    hist_log.write_dict(q_elements, hist_log.q_elements_path)
else:
    q_elements = hist_log.q_elements

q_dir = QuestionDirectory(q_elements, hist_log.q_state['current'])
help_menu = HelpMenu(q_dir.DEFAULT_NUM_TO_DISPLAY)
open_question(q_dir.get_current_num(), web_handler, hist_log)

is_continue = True
while is_continue:
    user_input = clean_user_input(input("\n\n----------------------------------------\nYou are on {name}\n\nWhat would you like to do next?\nType 'n' for next problem, 'h' for more help/options, 'e' to exit\n".format(name=q_dir.get_current().name)))
    try:
        is_continue = options(user_input, q_dir, hist_log, web_handler)
    except (IndexError, NoSuchWindowException, WebDriverException) as e:
        #print(e)
        msg =  'Browser was closed by user, exiting now'
        logging.exception(msg)
        is_continue = exit(web_handler,msg)
    except NoSuchElementException:
        msg = 'Web element not found, exiting now'
        logging.exception(msg)
        is_continue = exit(web_handler, msg)
    except:
        msg =  'Unexpected error, check log, exiting now'
        logging.exception(msg)
        is_continue = exit(web_handler, msg)

