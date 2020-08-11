from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException, NoSuchElementException, NoSuchWindowException
from datetime import datetime, timedelta
import re
import time

        #WebDriverWait(self.driver, self.__WEB_DRIVER_WAIT_SHORT).until(EC.element_to_be_clickable((By.XPATH, 'df')))
        #WebDriverWait(self.driver, self.__WEB_DRIVER_WAIT_SHORT).until(EC.element_to_be_clickable((By.CLASS_NAME, 'df')))

class WebHandler():
    __WEB_DRIVER_WAIT_LONG      = 15
    __WEB_DRIVER_WAIT_SHORT     = 5
    
    def __init__(self, driver):
        self.driver = driver
        self.leet_win = None
        self.db_win = None
        self.solution_win = None

    def get_question_elements(self):
        url = 'https://leetcode.com/problemset/database/?'
        win = self.open_new_win(url)
        WebDriverWait(self.driver, self.__WEB_DRIVER_WAIT_LONG).until(EC.element_to_be_clickable((By.XPATH, '//*[@id="question-app"]/div/div[2]/div[2]/div[2]/table/tbody[2]/tr/td/span[1]/select/option[4]'))).click()
        #note that this element can only be found using selenium (not requests, or beautifulsoup)because the table is generated after the fact in js
        element = self.driver.find_element_by_class_name('reactable-data')
        text =  [' '.join(line.split()) for line in element.text.split('\n')]
        question_elements = {}

        for i, line in enumerate(text):
            if (i+1) % 3 == 0:
                q_num = int(text[i-2])
                level = line.split()[1].lower()
                q_name = text[i-2] + ': ' + text[i-1] + ', ' + level
                question_elements[q_num] = {'level':level, 'name':q_name}
        self.close_window(win)
        return question_elements

    def close_window(self, window):
        try:
            if len(self.driver.window_handles) > 1:
                self.driver.switch_to.window(window)
                self.driver.close()
        except:
            pass

    def close_question_windows(self):
        windows =  (self.leet_win, self.db_win, self.solution_win)
        for window in windows:
            if window is not None:
                self.close_window(window)
        self.leet_win = self.db_win = self.solution_win = None

    def close_all(self):
        try:
            self.driver.quit()
        #driver already quit
        except:
            pass

    def get_last_window(self):
        return self.driver.window_handles[-1]

    def reset_curr_window(self):
        try:
            self.driver.switch_to_window(self.get_last_window()) 
        except:
            pass

    def open_new_win(self, url):
        '''
        Open a new tab for specified url
        Note that driver.current_window_handle attribute is not updated when executing this
        '''
        # need to always reset to an active window before opening new window b/c if opening from an inactive window, a non such window exception is triggered
        self.reset_curr_window()
        url = '\'' + url + '\''
        script = "window.open({url})".format(url=url)
        self.driver.execute_script(script)
        self.reset_curr_window()
        return self.get_last_window()

    def get_newest_fiddle_url(self, url):
        '''
        Gets the newest version of the fiddle url
        Each fiddle url ends with a version #, and increments up each time its saved
        If the fiddle url redirects to db-fiddle.com that means that url is not valid
        Note: I tried using requests module to check if url is valid, but even when the url is redirected, the request.is_redirect flag is still False
        '''
        url_index = int(url[-1])
        base_url = url[:-1]
        window_handles = []

        while url != 'https://www.db-fiddle.com/':
            window_handles.append(self.open_new_win(base_url + str(url_index)))
            time.sleep(3)
            url = self.driver.current_url
            url_index += 1

        # window_handles[-1] is always an invalid link that redirects to 'db-fiddle.com'
        self.db_win = window_handles[-2]

        for window in window_handles:
            if window != self.db_win:
                self.close_window(window)
        return base_url + str(url_index - 2)

    def open_solution_win(self, q_num):
        q_num = '\'' + str(q_num).zfill(4) + '\''
        try:
            url = 'https://github.com/kamyu104/LeetCode-Solutions#sql'
            self.solution_win = self.open_new_win(url)
            self.driver.find_element_by_xpath("//*[contains(text(),{q_num})]/following-sibling::td/following-sibling::td".format(q_num=q_num)).click()

            element = self.driver.find_element_by_css_selector('div[itemprop="text"]')
            self.driver.execute_script("arguments[0].scrollIntoView();", element)
        except:
            print('Solution not found')


    def get_leetcode_url(self, q_num):
        return 'https://leetcode.jp/problemdetail.php?id={q_num}'.format(q_num=q_num)

    def open_leetcode_win(self, q_num):
        '''
        select the leetcode jp problem to go to
        '''
        self.leet_win = self.open_new_win(self.get_leetcode_url(q_num))

        

    def test_parse_leetcode_tables_selenium():
        # this works out the box in qtconsole only for now     
        from selenium import webdriver
        import re

        driver = webdriver.Chrome(executable_path='/Users/jwong/Cabinet/Programming/Python/bing-rewards-master/BingRewards/drivers/chromedriver')

        num = 618
        url = 'https://leetcode.jp/problemdetail.php?id={num}'.format(num=num)
        driver.get(url)
        elements_pre = driver.find_elements_by_css_selector("pre")
        tables_pre = [element.text for element in elements_pre]
        for table_pre in list(tables_pre):
            #remove data type tables
            if 'Column Name' in table_pre:
                tables_pre.remove(table_pre)

        table_lines = []
        for table_pre in tables_pre:
            pattern = re.compile('\+--*.*\+|\|.*\|')
            table_lines.append(pattern.findall(table_pre))

        #seperate full table data into individual tables
        tables_text, current_table = [], []
        #seperate table type 1, common table style
        if '+' in table_lines[0][0]:
            #seperate table 1
            plus_ct = 0
            line_i = 0
            is_single_col = False
            for table_line in table_lines:
                for line in table_line:
                    if line.count('+') == 2:
                        is_single_col = True
                    if '+-' in line:
                        plus_ct += 1

                    if is_single_col:
                        line = add_col_table1(line_i, line, plus_ct == 3)
                    current_table.append(line)
                    line_i += 1
                    if plus_ct == 3:
                        tables_text.append('\n'.join(current_table))
                        current_table = []
                        plus_ct = 0
                        is_single_col = False
                        line_i = 0

        #seperate table type 2, rare style
        else:
            for table_line in table_lines:
                is_single_col = False
                if table_line[0].count('|') == 2:
                    is_single_col = True
                for i, line in enumerate(table_line):
                    if is_single_col:
                        line = add_col_table2(i, line)
                    current_table.append(line)
                tables_text.append('\n'.join(current_table))
                current_table = []



    class TableParser:

        def parse_table_pre(self, driver):
            elements_pre = driver.find_elements_by_css_selector("pre")
            tables_pre = [element.text for element in elements_pre]

            for table_pre in list(tables_pre):
                #remove data type tables
                if 'Column Name' in table_pre:
                    tables_pre.remove(table_pre)
            return tables_pre

        def parse_table_lines(self, tables_pre):
            '''
            tables_pre will contain some extra non-table lines
            This will remove any line that is not part of a table.
            The returned list will still need to be cleaned because the tables aren't seperated out
            '''
            table_lines = []
            for table_pre in tables_pre:
                pattern = re.compile('\+--*.*\+|\|.*\|')
                table_lines.append(pattern.findall(table_pre))
            return table_lines

        def is_table1(self, table_lines):
            return '+' in table_lines[0][0]

        def add_filler_col1(self, index, line, is_final=False):
            '''
            DB-fiddle does not support text to DDL for tables with 1 column. This adds a filler column for type 1 tables
            '''
            if index == 0:
                concat = '---------+'
            elif index == 1:
                concat = ' ignore  |'
            elif index == 2:
                concat = '---------+'
            elif is_final:
                concat = '---------+'
            else:
                concat = '  _      |'
            return line + concat

        def add_filler_col2(self, index, line):
            '''
            DB-fiddle does not support text to DDL for tables with 1 column. This adds a filler column for type 2 tables
            '''
            if index == 0:
                concat = ' ignore|'
            elif index == 1:
                concat = '-------|'
            else:
                concat = '   _   |'
            return line + concat
        
        def replace_invalid_char_header(self, line):
            '''
            for each non-valid char match, returns a space 
            The inner function adds a space for every match, rather than just one space for all matches
            '''
            pattern = re.compile(r'[^_A-Za-z\s\|\+\-]+')
            def repl(m):
                return ' ' * len(m.group())
            sub = re.sub(pattern, repl, line)
            return sub

        def seperate_tables1(self, table_lines):
            '''
            Seperate each table of table type 1 (they contain '+' in the text) into its own item in tables_text list
            '''
            tables_text, current_table = [], []
            plus_ct = line_i = 0
            is_single_col = False
            for table_line in table_lines:
                for line in table_line:
                    #if header line
                    if line_i == 1:
                        line = self.replace_invalid_char_header(line)
                    if line.count('+') == 2:
                        is_single_col = True
                    if '+-' in line:
                        plus_ct += 1

                    if is_single_col:
                        line = self.add_filler_col1(line_i, line, plus_ct == 3)
                    current_table.append(line)
                    line_i += 1
                    if plus_ct == 3:
                        tables_text.append('\n'.join(current_table))
                        current_table = []
                        is_single_col = False
                        plus_ct = line_i = 0
            return tables_text

        def seperate_tables2(self, table_lines):
            '''
            Seperate each table of table type 2 (they contain '|' in the first line) into its own item in tables_text list
            '''
            tables_text, current_table = [], []
            for table_line in table_lines:
                is_single_col = False
                if table_line[0].count('|') == 2:
                    is_single_col = True
                for line_i, line in enumerate(table_line):
                    if line_i == 0:
                        line = self.replace_invalid_char_header(line)
                    if is_single_col:
                        line = self.add_filler_col2(line_i, line)
                    current_table.append(line)
                tables_text.append('\n'.join(current_table))
                current_table = []
            return tables_text

        def add_result_tbl_name(self, names):
            if 'Result' not in names and 'result' not in names:
                names.append('Result')
            return names

        def get_names_final(self, names1, names2, target_len):
            diff1 = abs(target_len - len(names1))
            diff2 = abs(target_len - len(names2))
            min_diff = min(diff1, diff2)
            if min_diff == diff1:
                names_final = names1
            else:   
                names_final = names2

            if min_diff == 0:
                return names_final
            elif len(names_final) > target_len:
                print('CAUTION: Too many names parsed compared to # of tables')
                while len(names_final) != target_len:
                    names_final.pop()
            else:
                i = 0
                print('CAUTION: Too few names parsed compared to # of tables')
                while len(names_final) != target_len:
                    names_final.append('Unknown{i}'.format(i=i))
                    i+=1
            return names_final

        def parse_table_names(self, driver, tables_pre, target_len):
            #1 This method gets tables using regex looking for keyword 'table'
            pattern = re.compile('.+table')
            names1 = pattern.findall(''.join(tables_pre))
            names1 = [table_name.replace('table','').strip() for table_name in names1]
            names1 = self.add_result_tbl_name(names1)
            if len(names1) == target_len:
                return names1

            #2 This method gets tables using <code> tag
            elements = driver.find_elements_by_css_selector("code")
            element_names = set([element.text for element in elements])
            pattern = re.compile(r'[a-zA-Z]+')
            invalid_names = ['null']
            names2 = []
            for name in element_names:
                #name = element_name.text.find_all(text=True)[0]
                if pattern.match(name) and name not in invalid_names:
                    names2.append(name)
            names2 = self.add_result_tbl_name(names2)
            if len(names2) == target_len:
                return names2

            return self.get_names_final(names1, names2, target_len)

        def parse_leetcode_tables(self, driver, leet_win):
            driver.switch_to_window(leet_win)
            tables_pre = self.parse_table_pre(driver)
            table_lines = self.parse_table_lines(tables_pre)

            #seperate tables based on type
            if self.is_table1(table_lines):
                tables_text = self.seperate_tables1(table_lines)
            else:
                tables_text = self.seperate_tables2(table_lines)
                
            table_names = self.parse_table_names(driver, tables_pre, len(tables_text))
            return table_names, tables_text

    def open_db_win(self, url='https://www.db-fiddle.com/'):
        self.db_win = self.open_new_win(url)

    def db_fiddle_select_engine(self):
        OPTION_MYSQL8 = 0
        OPTION_POSTGRES12 = 5
        #actual
        self.driver.switch_to_window(self.db_win)
        self.driver.find_element_by_class_name('ember-power-select-status-icon').click()
        self.driver.find_elements_by_class_name('ember-power-select-option')[OPTION_MYSQL8].click()

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
        pre_url = self.driver.current_url
        try:
            self.driver.find_element_by_xpath('//*[@id="saveButton"]').click()
        except:
            self.driver.find_element_by_xpath('//*[@id="runButton"]').click()
        WebDriverWait(self.driver, self.__WEB_DRIVER_WAIT_LONG).until_not(EC.url_to_be(pre_url))
        return self.driver.current_url

    def close_question(self, to_resave_before_close=False):
        if len(self.driver.window_handles) == 0:
            raise NoSuchWindowException
        end_url = None
        try:
            self.driver.switch_to_window(self.db_win)
            if to_resave_before_close:
                end_url = self.db_fiddle_save()
            else:
                end_url = self.driver.current_url
        except:
            pass
        self.close_question_windows()
        return end_url

    def open_question(self, q_num, prev_url=None):
        #should open leetcode window
        self.open_leetcode_win(q_num)
        if prev_url is not None:
            start_url = self.get_newest_fiddle_url(prev_url)

            #start_url = prev_url
            #self.open_db_win(start_url)

        #no db-fiddle has been created, create one
        else:
            self.open_db_win()
            self.db_fiddle_select_engine()
            #parse the tables
            table_names, tables_text = self.TableParser().parse_leetcode_tables(self.driver, self.leet_win)
            #table_names, tables_text = self.parse_leetcode_tables(q_num)
            #dump tables onto db fiddle
            for i, table_text in enumerate(tables_text):
                self.db_fiddle_table_input(table_names[i], table_text)
            self.db_fiddle_query_input(table_names[0])
            start_url = self.db_fiddle_save()
        self.driver.switch_to_window(self.leet_win)
        return start_url


if __name__ == '__main__':
    from selenium import webdriver
    import os
    #q_num = 1517
    driver_path = os.path.join('drivers','chromedriver') 
    from driver import Driver
    wh = WebHandler(Driver.get_driver(driver_path))

    q_num = 613
    wh.open_leetcode_win(q_num)

    wh.open_db_win()
    #parse the tables
    table_names, tables_text = wh.TableParser().parse_leetcode_tables(wh.driver, wh.leet_win)

    for i, table_text in enumerate(tables_text):
        wh.db_fiddle_table_input(table_names[i], table_text)




    #tables_pre = wh.parse_leetcode_tables(q_num)

    #url = 'https://www.db-fiddle.com/f/oGBBsMS81pMbm3eYDWTm7S/0'
    #newest = wh.get_newest_fiddle_url(url)
    #wh.open_question(q_num)
    

    ''' get_question testing
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
    '''    
