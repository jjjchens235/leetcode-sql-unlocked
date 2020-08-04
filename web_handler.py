from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver import ActionChains
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from datetime import datetime, timedelta
import requests
from bs4 import BeautifulSoup
import re


class WebHandler():
    def __init__(self, driver):
        self.driver = driver
        self.leet_win = None
        self.db_win = None
        self.solution_win = None

    def close_window(self, window):
        if window and len(self.driver.window_handles) > 1:
            self.driver.switch_to.window(window)
            self.driver.close()
            window = None

    def close_curr_windows(self):
        windows =  (self.leet_win, self.db_win, self.solution_win)
        for window in windows:
            self.close_window(window)

    def close_all_windows():
        #see if this works, I'm calling Driver.py method
        self.driver.quit()

    def get_questions_dict(self):
        url = 'https://leetcode.com/problemset/database/?'
        self.driver.get(url)
        WebDriverWait(self.driver, 30).until(EC.element_to_be_clickable((By.XPATH, '//*[@id="question-app"]/div/div[2]/div[2]/div[2]/table/tbody[2]/tr/td/span[1]/select/option[4]'))).click()
        #note that this element can only be found using selenium (not requests, or beautifulsoup)because the table is generated after the fact in javascript
        element = self.driver.find_element_by_class_name('reactable-data')
        text =  [' '.join(line.split()) for line in element.text.split('\n')]
        questions = {}

        for i, line in enumerate(text):
            if (i+1) % 3 == 0:
                q_num = int(text[i-2])
                level = line.split()[1].lower()
                q_name = text[i-2] + ': ' + text[i-1] + ', ' + level
                questions[q_num] = {'level':level, 'name':q_name}
        return questions

    def open_new_win(self, url):
        '''
        open a new tab for specified url
        '''
        url = '\'' + url + '\''
        script = "window.open({url})".format(url=url)
        self.driver.execute_script(script)

    def get_leetcode_url(self, q_num):
        url = 'https://leetcode.jp/problemdetail.php?id={q_num}'.format(q_num=q_num)
        return url

    def open_leetcode_win(self, q_num):
        '''
        select the leetcode jp problem to go to
        '''

        leetcode_url = self.get_leetcode_url(q_num)
        self.open_new_win(leetcode_url)
        self.leet_win = self.driver.window_handles[-1]

    def parse_leetcode_tables(self, q_num):
        self.driver.switch_to_window(self.leet_win)
        r = requests.get(self.get_leetcode_url(q_num))
        soup = BeautifulSoup(r.text,'html.parser')

        tables_pre = soup.find_all('pre')
        for table_pre in list(tables_pre):
            #remove data type tables
            if 'Column Name' in table_pre.text:
                tables_pre.remove(table_pre)

        #get full table data
        table_lines = []
        for table_pre in tables_pre:
            pattern = re.compile('\+--*.*\+|\|.*\|')
            table_lines.append(pattern.findall(table_pre.text))

        tables_text = []
        prev_len = None
        current_table = []
        plus_line_ct= 0
        for table_line in table_lines:
            for line in table_line:
                curr_len = len(line)
                if '+-' in line:
                    plus_line_ct += 1
                #we reached a new table if the length of the lines are different or...
                #if '+------' this pattern is repeating
                if (prev_len and prev_len != curr_len) or (plus_line_ct == 4):
                    if plus_line_ct == 4:
                        plus_line_ct = 0
                    tables_text.append('\n'.join(current_table))
                    current_table = []
                prev_len = curr_len
                current_table.append(line)
        tables_text.append('\n'.join(current_table))
            
        #to get table names
        #1 This works for newer  questions where it goes X table: then the actual SQL table
        pattern = re.compile('.+table')
        table_names = pattern.findall(table_pre.text)
        table_names = [table_name.replace('table','').strip() for table_name in table_names]

        if 'Result' not in table_names and 'result' not in table_names:
            table_names.append('Result')

        #2 This method gets tables using <code> tag
        if len(table_names) != len(tables_text):
            pattern = re.compile(r'[a-zA-Z]+')
            table_names = []
            for name in soup.find_all('code'):
                name = name.find_all(text=True)[0]
                if pattern.match(name):
                    table_names.append(name)
            if 'Result' not in table_names and 'result' not in table_names:
                table_names.append('Result')


        return table_names, tables_text

    def get_prev_db_url(self, q_num):
        #TODO
        # if log shows q_num already has an url, then just open that url
            #actually, you need to check for a more recent url that the user updated to. Might also need to update log accoridingly
        #else return None
        return None
        

    def open_db_win(self, url='https://www.db-fiddle.com/'):
        self.open_new_win(url)
        self.db_win = self.driver.window_handles[-1]



    def db_fiddle_query_input(self, table_name):
        #Code Mirror lines element must be activated, before textbox element can be sent keys
        self.driver.switch_to_window(self.db_win)
        code_mirror = self.driver.find_element_by_xpath( '//*[@id="query"]/div[2]/div[6]/div[1]/div/div/div')
        code_mirror.click()
        textbox = self.driver.find_element_by_xpath('//*[@id="query"]/div[2]/div[1]/textarea')
        query = 'SELECT * FROM {table_name}'.format(table_name=table_name)
        textbox.send_keys(query)

    def db_fiddle_table_input(self, table_name, table_text):
        #text to DDL
        #table_text = '+--------------------+---------+\n| product_name       | unit    |\n+--------------------+---------+\n| Leetcode Solutions | 130     |\n| Leetcode Kit       | 100     |\n+--------------------+---------+'
        self.driver.switch_to_window(self.db_win)
        self.driver.find_element_by_xpath('//*[@id="schema"]/div[3]/button[1]').click()
        table_name_input = self.driver.find_element_by_xpath("//div[@id='textToDDLModal']//*[starts-with(@class,'modal-body')]//*[starts-with(@id,'ember')]/input")
        table_name_input.send_keys(table_name)
        table_input = self.driver.find_element_by_xpath("//div[@id='textToDDLModal']//*[starts-with(@class,'modal-body')]//*[starts-with(@id,'ember')]/textarea")
        table_input.send_keys(table_text)
        append_button = self.driver.find_element_by_xpath("//div[@id='textToDDLModal']//*[starts-with(@class,'modal-body')]/button[2]")
        append_button.click()

    def db_fiddle_save(self):
        self.driver.switch_to_window(self.db_win)
        try:
            self.driver.find_element_by_xpath('//*[@id="saveButton"]').click()
        except:
            self.driver.find_element_by_xpath('//*[@id="runButton"]').click()
        return self.driver.current_url

    def get_question(self, q_num):
        pass
        self.close_curr_windows()
        #should open leetcode window
        self.open_leetcode_win(q_num)
        prev_url = self.get_prev_db_url(q_num)
        if prev_url:
            url = 'TODO'
            self.open_db_win(url)

        else:
            self.open_db_win()
            #parse the tables
            table_names, tables_text = self.parse_leetcode_tables(q_num)
            #dump tables onto db fiddle
            for i, table_text in enumerate(tables_text):
                self.db_fiddle_table_input(table_names[i], table_text)
            self.db_fiddle_query_input(table_names[0])
            save_url = self.db_fiddle_save()


if __name__ == '__main__':
    from driver import Driver
    import os
    q_num = 1517
    driver_path = os.path.join('drivers','chromedriver') 
    wh = WebHandler(Driver.get_driver(driver_path))
    wh.close_curr_windows()
    wh.open_leetcode_win(q_num)

    prev_url = wh.get_prev_db_url(q_num)

    wh.open_db_win()
    #parse the tables

    table_names, tables_text = wh.parse_leetcode_tables(q_num)
    #dump tables onto db fiddle
    for i, table_text in enumerate(tables_text):
        wh.db_fiddle_table_input(table_names[i], table_text)
    wh.db_fiddle_query_input(table_names[0])
    save_url = wh.db_fiddle_save()

