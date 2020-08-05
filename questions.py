from datetime import datetime
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
import sys
import pprint
from collections import defaultdict
import time
from driver import Driver

def print_file(txt):
    date = datetime.now().strftime('%Y-%m-%d-%M')
    txt = str(txt)
    print(txt, file=open('/Users/jwong/Cabinet/Out/' + date + ' html.txt','w'))

def print_questions(questions):
    date = datetime.now().strftime('%Y-%m-%d-%M')
    file=open('/Users/jwong/Cabinet/Out/' + date + ' html.txt','w')
    pprint.pprint(questions,file)



class Question:
    def __init__(self, number, name, level, next=None, next_same_lvl=None):
        self.number = number
        self.name = name
        self.level = level
        self.next = next
        self.next_same_lvl = next_same_lvl

class QuestionList:
    DEFAULT_NUM_TO_DISPLAY = 15

    def __init__(self, question_elements, curr_log_num):
        
        self.question_nodes = {}
        self.current = self.create_q_nodes(question_elements, curr_log_num) 


    def create_q_nodes(self, question_elements, curr_log_num):
        head = None
        head_easy = None
        head_med = None
        head_hard = None
        prev_q = None
        prev_q_easy = None
        prev_q_med = None
        prev_q_hard = None

        for q_num in questions.keys():
            name = questions[q_num]['name']
            level = questions[q_num]['level']
            q = Question(q_num, name, level)
            self.question_nodes[q_num] = q
            if q_num == curr_log_num:
                curr = q

            if not head:
                head = q

            if prev_q:
                prev_q.next = q
            prev_q = q

            if level == 'easy':
                if prev_q_easy:
                    prev_q_easy.next_same_lvl = q
                else:
                    head_easy = q
                prev_q_easy = q

            elif level == 'medium':
                if prev_q_med:
                    prev_q_med.next_same_lvl = q
                else:
                    head_med = q
                prev_q_med = q

            else:
                if prev_q_hard:
                    prev_q_hard.next_same_lvl = q
                else:
                    head_hard = q
                prev_q_hard = q

        q.next = head
        prev_q_easy.next_same_lvl = head_easy
        prev_q_med.next_same_lvl = head_med
        prev_q_hard.next_same_lvl = head_hard
        return curr


    def print_q_nodes(self):
        curr = self.current
        while curr.number != self.current.number:
            #q_number = curr.number
            print('Current Question: ' + str(curr.number) +', Question Name: ' + curr.name + ', Level: ' + curr.level + ', Next Question: ' + str(curr.next.number) + ' , Next Same Level Question: ' + str(curr.next_same_lvl.number) + '\n')
            curr = curr.next
            
    def get_next_node(self, node, level=None):
        if level is None:
            return node.next
        elif node.level == level:
            return node.next_same_lvl
        else:
            curr = node.next
            while curr.level != level:
                curr = curr.next
            return curr
        
    def select_next_question(self, level=None):
        '''
        Returns the next question based on current. Can also return next question by level
        '''
        self.current = self.get_next_node(self.current, level)

    def select_question_by_number(self, number):
        self.current = self.question_nodes[number]

    def get_next_n_nodes(self, n, level=None):
        nodes = []
        curr = self.current
        head = None
        for i in range(n):
            curr = self.get_next_node(curr, level)
            #repeating questions
            if head is not None and head.number == curr.number:
                break
            nodes.append(curr)
            if i == 0:
                head = curr
        return nodes

    def display_questions(self, level=None , n=None):
        #level_args = {'de':'easy', 'display easy':'easy', 'dm':'medium', 'display medium':'medium', 'dh':'hard', 'display hard':'hard'}

        if n is None:
            n = QuestionList.DEFAULT_NUM_TO_DISPLAY
        q_names = [node.name for node in self.get_next_n_nodes(n, level)]
        print('\nDisplaying next {n}{level} questions:\n'.format(n=n,level= ' '+ level if level is not None else ''))
        pprint.pprint(q_names)
        time.sleep(2)
        return q_names

            

if __name__ == '__main__':
    driver = webdriver.Chrome(executable_path='/Users/jwong/Cabinet/Programming/Python/bing-rewards-master/BingRewards/drivers/chromedriver')
    url = 'https://leetcode.com/problemset/database/?'
    driver.get(url)
    WebDriverWait(driver, 30).until(EC.element_to_be_clickable((By.XPATH, '//*[@id="question-app"]/div/div[2]/div[2]/div[2]/table/tbody[2]/tr/td/span[1]/select/option[4]'))).click()


    #note that this element can only be found using selenium because the table is generated after the fact in javascript
    element = driver.find_element_by_class_name('reactable-data')

    text =  [' '.join(line.split()) for line in element.text.split('\n')]
    questions = {}
    levels = defaultdict(list)

    for i, line in enumerate(text):
        if (i+1) % 3 == 0:
            q_num = int(text[i-2])
            level = line.split()[1].lower()
            levels[level].append(q_num)
            q_name = text[i-2] + ': ' + text[i-1] + ', ' + level
            questions[q_num] = {'level':level, 'name':q_name}


    curr_log_num = 584
    ql = QuestionList(questions, curr_log_num)
    ql.display_questions(level='medium', n=200)
