from help_menu import HelpMenu
from questions import QuestionList
from driver import Driver
from web_handler import WebHandler
from log import HistLog
import os
import re
import time

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

def is_question_changed(curr_number, question):
    #TODO
    '''
    not used for now
    maybe delete it
    '''
    return curr_number != question_number

def output_question_state():
    #TODO
    '''
    not used for now
    maybe delete it
    '''
    pass

def is_stale_file(file_path, days_till_stale=13):
    mtime = os.path.getmtime(path) 
    return (datetime.now() - datetime.fromtimestamp(mtime)).days > days_till_stale:
        

def print_options(s, n_sleep=1):
    print('\n')
    print(s)
    print('\n')
    time.sleep(n_sleep)

def next_option(user_input, question_list):
    if user_input in ['ne', 'nm', 'nh']:
        user_input = ' '.join(user_input)
    user_inputs = user_input.split()
    if user_inputs[0] in ('n', 'next'):
        if len(user_inputs) == 1:
            print_options("You chose next question")
            question_list.select_next_question()
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
            if level:
                print_options("You chose next {level} question".format(level=level))
                question_list.select_next_question(level)
        else:
            print_options("Invalid input!! Too many arguments for next command. Either use 'n' or try by level i.e. 'n e' for next easy, 'n m', 'n h'")
    else:
        print_options("Invalid input!! Do you want to go to next question? Either use 'n' or try by level i.e. 'n e' for next easy, 'n m', 'n h'")

def question_by_number_option(user_input, question_list, web_handler):
    '''
    Checks that the user input is a string that starts with q and ends with a number
    If the input is valid, change question to number inputted
    '''
    pattern = re.compile(r'q[a-z\s]*\d+')
    matches = pattern.findall(user_input)
    if len(matches) > 0:
        pattern = re.compile(r'\d+')
        q_num = int(pattern.findall(matches[0])[0])
        try:
            question_list.select_question_by_number(q_num)
            print('made it here')
            web_handler.get_question(q_num)
        except KeyError:
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
    
def display_questions_option(user_input, question_list):
    level_arg, num_to_display_arg = parse_display_args(user_input)
    print('\n')
    question_list.display_questions(level_arg, num_to_display_arg)

def exit_option():
    print("Exiting program\n")
    return False

def options(user_input, question_list, web_handler):

        valid_start_inputs = ['h', 'n', 'q', 's', 'd', 'e']

        #try:
        start_input = user_input[0]
        if start_input in valid_start_inputs:
            if start_input == 'h':
                if user_input in ('h', 'help'):
                    help_menu.print_help()
            elif start_input == 'n':
                next_option(user_input, question_list)
                            
            elif start_input == 'q':
                if user_input == ('q'):
                    print_options("Invalid input. If you want to select by question number input 'q NUMBER'. Else if you want to quit, press 'e' to exit")
                elif user_input == ('quit'):
                    return exit_option()
                else:
                    question_by_number_option(user_input, question_list, web_handler)
            elif start_input == 's':
                pass
            elif start_input == 'd':
                display_questions_option(user_input, question_list)
            elif start_input == 'e':
                if user_input in ('e', 'exit'):
                    return exit_option()
                else:
                    print_options('Invalid input')
        else:
            print_options('Invalid input!')
        #except:
        #    pass
        return True


DRIVER_DIR = 'drivers'
DRIVER = 'chromedriver'
LOG_DIR = 'logs'
ERROR_LOG = 'error.log'
Q_ELEMENTS_LOG = 'q_elements.log'
Q_STATUS_LOG = 'q_status.log'

#--- what i want to build using driver class
if not os.path.exists(DRIVER_DIR):
    os.mkdir(DRIVER_DIR)

if not os.path.exists(LOG_DIR):
    os.mkdir(LOG_DIR)

driver_path = os.path.join('drivers','chromedriver') 
driver = Driver.get_driver(driver_path)
web_handler = WebHandler(driver)

hist_log = HistLog(os.path.join(LOG_DIR, Q_ELEMENTS_LOG), os.path.join(LOG_DIR, Q_STATUS_LOG))
if is_stale_file(hist_log.q_elements_path):
    question_elements = web_handler.get_question_elements()
else:
    question_elements = hist_log.read(hist_log.q_elements_path)



#------ what i have currently

'''
driver = webdriver.Chrome(executable_path='/Users/jwong/Cabinet/Programming/Python/bing-rewards-master/BingRewards/drivers/chromedriver')
url = 'https://leetcode.com/problemset/database/?'
driver.get(url)
WebDriverWait(driver, 30).until(EC.element_to_be_clickable((By.XPATH, '//*[@id="question-app"]/div/div[2]/div[2]/div[2]/table/tbody[2]/tr/td/span[1]/select/option[4]'))).click()
#note that this element can only be found using selenium because the table is generated after the fact in javascript
element = driver.find_element_by_class_name('reactable-data')
text =  [' '.join(line.split()) for line in element.text.split('\n')]
driver.get('https://yahoo.com')
'''







#questions_dict = web_handler.get_questions_dict()

curr_log_num = 584
ql = QuestionList(driver, question_elements, curr_log_num)
help_menu = HelpMenu()
is_continue = True
while is_continue:
    user_input = clean_user_input(input("\n\n----------------------------------------\nYou are on {name}\n\nWhat would you like to do next?\nType 'n' for next problem, 'h' for more help/options, 'e' to exit\n".format(name=ql.current.name)))
    is_continue = options(user_input, ql, web_handler)
