import requests
from bs4 import BeautifulSoup
import re





#def get_sql_tables():

url = 'https://leetcode.jp/problemdetail.php?id=584'
r = requests.get(url)
soup = BeautifulSoup(r.text,'html.parser')
'''
to get the tables data ( but it's still messy so you need to clean it)
'''
tables_pre = soup.find_all('pre')
for table_pre in list(tables_pre):
    #remove any tables that show the data types
    if 'Column Name' in table_pre.text:
        tables_pre.remove(table_pre)


'''
attempt to get full table data
'''
table_lines = []
for table_pre in tables_pre:
    #pattern = re.compile('\+-.*-\+')
    pattern = re.compile('\+--*.*\+|\|.*\|')
    table_lines.append(pattern.findall(table_pre.text))


tables_sep = []
prev_len = None
current_table = []
plus_line_ct= 0
for table_line in table_lines:
    for line in table_line:
        curr_len = len(line)
        if '+-' in line:
            plus_line_ct += 1
        #we reached a new table if the length of the lines are different or...
        #+------ this pattern is repeating
        if (prev_len and prev_len != curr_len) or (plus_line_ct == 4):
            if plus_line_ct == 4:
                plus_line_ct = 0
            tables_sep.append('\n'.join(current_table))
            current_table = []
        prev_len = curr_len
        current_table.append(line)
tables_sep.append('\n'.join(current_table))


    
'''
to get table names
'''
#1 This works for newer  questions where it goes X table: then the actual SQL table
pattern = re.compile('.+table')
table_names = pattern.findall(table_pre.text)
table_names = [table_name.replace('table','').strip() for table_name in table_names]

if 'Result' not in table_names and 'result' not in table_names:
    table_names.append('Result')

if len(table_names) != len(tables_sep):
    name = 'hello'
    pattern = re.compile(r'[a-zA-Z]+')

    #2 This method gets tables using <code> tag
    table_names = []
    for name in soup.find_all('code'):
        name = name.find_all(text=True)[0]
        if pattern.match(name):
            print(name)
            table_names.append(name)
    if 'Result' not in table_names and 'result' not in table_names:
        table_names.append('Result')


