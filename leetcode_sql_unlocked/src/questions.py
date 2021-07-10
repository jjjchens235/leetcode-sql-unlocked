import pprint
import time

class QuestionNode:
    '''
    Each question node has a number, name, and level attribute and a pointer to the next node, as well as pointer to the next node of the same level
    '''
    def __init__(self, number, name, level, next=None, next_same_lvl=None):
        self.number = number
        self.name = name
        self.level = level
        self.next = next
        self.next_same_lvl = next_same_lvl

class QuestionNodes:
    '''
    The questions are represented as a linked list type structure. The current node is saved in a log file, so the next question can be easily accessed. However, the user also has an option of selecting by question number, meaning there's potential of jumping many nodes across, so each question node can also be accessed by its number key.
    '''
    DEFAULT_NUM_TO_DISPLAY = 15

    def __init__(self, question_elements, curr_log_num):
        self.__question_nodes = {}
        self.head = None
        self.tail = None
        self.__current = self.create_q_nodes(question_elements, curr_log_num)

    def create_q_nodes(self, question_elements, curr_log_num):
        head_easy = None
        head_med = None
        head_hard = None
        prev_q = None
        prev_q_easy = None
        prev_q_med = None
        prev_q_hard = None

        for q_num in sorted(question_elements.keys()):
            name = question_elements[q_num]['name']
            level = question_elements[q_num]['level']
            q = QuestionNode(q_num, name, level)
            self.__question_nodes[q_num] = q
            if q_num == curr_log_num:
                curr = q

            if not self.head:
                self.head = q

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

        self.tail = q
        q.next = self.head
        prev_q_easy.next_same_lvl = head_easy
        prev_q_med.next_same_lvl = head_med
        prev_q_hard.next_same_lvl = head_hard

        #if for some reason, the current question in the log is an invalid question #, reset question to #176
        if not self.is_q_exist(curr_log_num):
            curr = self.head.next
        return curr

    def print_q_nodes(self):
        curr = self.__current
        while curr.number != self.__current.number:
            print('Current Question: ' + str(curr.number) +', Question Name: ' + curr.name + ', Level: ' + curr.level + ', Next Question: ' + str(curr.next.number) + ' , Next Same Level Question: ' + str(curr.next_same_lvl.number) + '\n')
            curr = curr.next

    def get_current(self):
        return self.__current

    def get_current_num(self):
        return self.__current.number

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
        self.__current = self.get_next_node(self.__current, level)

    def is_q_exist(self, number):
       try:
           self.__question_nodes[number]
       except KeyError:
            return False
       return True

    def select_question_by_number(self, number):
        self.__current = self.__question_nodes[number]

    def get_next_n_nodes(self, n, level=None):
        nodes = []
        curr = self.__current
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
        if n is None:
            n = self.DEFAULT_NUM_TO_DISPLAY
        q_names = [node.name for node in self.get_next_n_nodes(n, level)]
        print('\nDisplaying next {n}{level} questions:\n'.format(n=n, level= ' '+ level if level is not None else ''))
        pprint.pprint(q_names)
        time.sleep(2)
        return q_names
