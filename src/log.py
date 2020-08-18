import os
import ast
import pprint


class QuestionLog:

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
            try:
                file = open(path, "r")
                return ast.literal_eval(file.read())
            except:
                pass
        return None

    def write_dict(self, path, dict):
        file=open(path, 'w')
        pprint.pprint(dict, file)

    def update_q_current(self, q_num):
        self.q_state['current'] = q_num

    def update_q_url(self, q_num, url):
        self.q_state['url'][q_num] = url

    def update_q_state(self, q_num, url):
        self.update_q_current(q_num)
        self.update_q_url(q_num, url)
        self.write_dict(self.q_state_path, self.q_state)
