'''
The main module that instantiates and controls the behavior and interaction of all objects, most notably objects from WebHandler, QuestionNodes, and QuestionLog.
'''
import os
from shutil import copyfile
import logging
import traceback
from datetime import datetime

from selenium.common.exceptions import NoSuchWindowException, NoSuchElementException, WebDriverException

from src.leetcode import Leetcode

DRIVER_DIR = 'drivers'
DRIVER = 'chromedriver'

LOG_DIR = 'logs'
ERROR_LOG = 'error.log'
Q_ELEMENTS_LOG = 'q_elements.log'
Q_STATE_LOG = 'q_state.log'
Q_PUBLIC_URLS_LOG = 'q_public_urls.log'

def setup_dirs():
    try:
        os.chdir(os.path.dirname(os.path.realpath(__file__)))
        if not os.path.exists(DRIVER_DIR):
            os.mkdir(DRIVER_DIR)
        if not os.path.exists(LOG_DIR):
            os.mkdir(LOG_DIR)
    #running from shell, no __file__ var
    except NameError:
        print('CAUTION: __file__ variable could not be determined so directory check could not be completed')

def copy_public_urls(target):
    src = os.path.join(os.path.dirname(os.getcwd()), 'db_fiddle_public_urls.md')
    if not os.path.exists(src):
        with open(src, 'w') as f:
            f.write('{}')
    copyfile(src, target)

def get_leetcode(headless=False):
    setup_dirs()
    driver_path = os.path.join(DRIVER_DIR, DRIVER)
    q_elements_path = os.path.join(LOG_DIR, Q_ELEMENTS_LOG)
    q_state_path = os.path.join(LOG_DIR, Q_STATE_LOG)
    q_public_urls_path = os.path.join(LOG_DIR, Q_PUBLIC_URLS_LOG)
    if not os.path.exists(q_public_urls_path):
        copy_public_urls(q_public_urls_path)
    lc = Leetcode(driver_path, q_elements_path, q_state_path, q_public_urls_path, headless=headless)
    return lc

def main():
    lc = get_leetcode()
    logging.basicConfig(level=logging.ERROR, format='%(message)s', filename=os.path.join(LOG_DIR, ERROR_LOG))
    is_continue, tb = True, None
    try:
        lc.start_new_question(q_num=lc.get_current_q_num())
        while is_continue:
            is_continue = lc.options(lc.get_user_input())

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
            lc.exit_option(msg)

if __name__ == '__main__':
    main()
