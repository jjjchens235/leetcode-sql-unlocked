
## Overview
Through the command line, the user can easily access all ~100 leetcode SQL questions, even the locked ones, and automatically generate the tables in db-fiddle.com

## Features
* Auto-generate tables from each leetcode problem into db-fiddle so all your code/queries can be tested
* Past db-fiddles are saved, so progress is never lost and the user can continue right where they left off
* Solutions tab easily opened
* Convenient leetcode question navigation, by level or by number

## Getting Started
1. Requires Google Chrome which can be downloaded from https://www.google.com/chrome/browser/desktop/index.html
2. Python 3.6+. If you don't already have Python 3 installed, visit https://www.python.org/downloads/
3. Now install the dependencies using requirements.txt file included in the repo: `pip install -r leetcode_sql_unlocked/requirements.txt`
4. And you're all set. To start the program run `leetcode_sql_unlocked/leetcode_sql_unlocked.py` and follow the onscreen prompt

## Command Line Options
`
  (h)elp                            Show this help menu
  (n)ext [LEVEL]                    Select next problem. Optionally, go next
                                    by level [(e)asy, (m)edium, (h)ard],
                                    default ignores levels. I.e. 'n' or 'n e'
                                    or 'next easy'
  (q)uestion NUMBER                 Select problem by question number i.e. 'q
                                    183' or 'question 183'
  (s)olution                        Open solution of current problem in
                                    webpage
  (d)isplay [LEVEL] [# TO DISPLAY]  Displays list of problems. Optionally, can
                                    display by level [(e)asy, (m)edium,
                                    (h)ard]. Optionally, can also choose how
                                    many problems to display, default is 15.
                                    Ex: 'd' is to display next 15 problems of
                                    all levels, 'd e 30' is to display the
                                    next 30 easy problems.
  (e)xit                            Exit program
`

## Optional Config
The following db-fiddle settings can be optionally configured inside *leetcode_sql_unlocked/config_db_fiddle.py*:

`DB_OPTION`: User has the following databases to choose from, MYSQL_8, POSTGRES_12, and SQLITE_3_3. Default is MYSQL_8.

`SAVE_BEFORE_CLOSING`: If `True`, before going to the next question or exiting, will save the current fiddle automatically. Default is `False`, meaning the user must click save in the db-fiddle for changes to be saved.

`CHECK_NEW_SAVE_VERSIONS`: If `True`, will check for any newer versions of the db-fiddle. Default is `False`. This setting should only be switched to True if user is planning to make changes to db-fiddles outside of this program.
`

## Known Issues
* Columns with only blank values are parsed as Integer in db-fiddle's text to DDL parser, however, this ends up throwing an error when the tables are actually queried on. This issue occurs for problem #586, a simple fix is switching from Integer to Varchar(1)
* Some problems don't have actual table data, for example problem #175, so no db-fiddle can be created
