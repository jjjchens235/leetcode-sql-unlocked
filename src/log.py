import os
import ast
import pprint


class QuestionLog:
    '''
    The question log keeps track of two things. Firstly, q_elements, which is all the question data parsed from leetcode. The question elements are saved in a log so that the question info doesn't have to be downloaded each session since questions aren't being added that often.
    Secondly, q_state, which is the state of each of the questions, specifically which question the user is currently on, and a list of all questions that user has a db-fiddle of, including the URL of the db-fiddle.
    '''

    def __init__(self, q_elements_path, q_state_path):
        self.q_elements_path = q_elements_path
        self.q_state_path = q_state_path

        self.q_elements = self.__read_dict(q_elements_path)
        self.q_state = self.__read_dict(q_state_path)

        if self.q_state is None:
            #If question state does not exist yet, start at question 176
            self.q_state = {'current':176,'url':{}}

    def __read_dict(self, path):
        if os.path.exists(path):
            with open(path, "r") as f:
                return ast.literal_eval(f.read())
        return None

    def write_dict(self, path, dict):
        with open(path, 'w') as f:
            pprint.pprint(dict, f)

    def update_q_current(self, q_num):
        self.q_state['current'] = q_num

    def update_q_url(self, q_num, url):
        self.q_state['url'][q_num] = url

    def update_q_state(self, q_num, url):
        self.update_q_current(q_num)
        self.update_q_url(q_num, url)
        self.write_dict(self.q_state_path, self.q_state)

    def is_q_exist(self, q_num):
        return q_num in self.q_state['url'].keys()
