Through the command line, the user can easily access all ~125 LeetCode SQL/Database questions, even locked ones, and automatically generate the tables in db-fiddle.com, a SQL database playground environment.


![GIF demo](img/demo2.gif)

## Features
* Auto-generate tables from each SQL LeetCode problem into db-fiddle so all your queries can be tested
* Past db-fiddles are saved, so progress is never lost and the user can continue right where they left off
* Solutions tab easily opened
* Convenient LeetCode question navigation, by level or by number

## Getting Started
1. Requires Google Chrome which can be downloaded from https://www.google.com/chrome/browser/desktop/index.html.
2. Python 3.6+. If you don't already have Python 3 installed, visit https://www.python.org/downloads/.
3. The only dependency is selenium. Either install using `pip install selenium` or use the requirements.txt file included in the repo: `pip install -r leetcode_sql_unlocked/requirements.txt`.
4. Run `leetcode_sql_unlocked/setup.py` to create a config file with default settings.
5. And you're all set. To start the program run `leetcode_sql_unlocked/leetcode_sql_unlocked.py` and follow the onscreen prompt.

## Command Line Options
`(h)elp`: Show this help menu.

`(n)ext [LEVEL]`: Select next problem. Optionally, go next by level [(e)asy, (m)edium, (h)ard], default ignores levels. Ex: 'n' or 'next easy' or 'n e'

`(q)uestion NUMBER`: Select problem by question number. Ex: 'question 183' or 'q 183'

`(s)olution`: Open solution of current problem in new chrome tab

`(d)isplay [LEVEL] [# TO DISPLAY]`: Displays list of problems. Optionally, can display by level [(e)asy, (m)edium, (h)ard]. Furthermore, can optionally choose how many problems to display, default is 15. Ex: 'd' is to display next 15 problems of all levels, 'd e 30' is to display the next 30 easy problems.

`(e)xit`: Exit Program

## Config
The following db-fiddle settings can be optionally configured inside *leetcode_sql_unlocked/src/config.py*:

`DB_ENGINE`: User has the following databases to choose from: MYSQL_8, POSTGRES_12, and SQLITE_3_3. Default is `MYSQL_8`.

`SAVE_BEFORE_CLOSING`: If `True`, before going to the next question or exiting, will save the current fiddle automatically. Note that the fiddle is always saved when first created- this setting is for all proceeding saves. Default is `False`, meaning the user must manually click save if they want the changes they made to persist beyond the current session.

`CHECK_NEW_SAVE_VERSIONS`: If `True`, will check for any newer versions of the db-fiddle. Default is `False`. This setting should only be switched to True if user is planning to make changes to their db-fiddles outside of this program.

## Known Issues
* Some problems don't have actual table data, for example problem #175, so no db-fiddle can be created.
* DB-fiddle issue
 * Columns with only blank values are parsed as INTEGER in db-fiddle's text to DDL parser. However, this ends up throwing an error when the tables are actually queried on. This issue occurs for problem #586, a simple fix is switching from INTEGER to VARCHAR(1) in the table schema.
 * Columns with %Y-%m, i.e. '2017-05' are parsed as DATETIME when they should be parsed as VARCHAR inside db-fiddle's text to DDL. A simple fix is switching from DATETIME to VARCHAR(7) in the table schema. This issue occurs for #615.

## DB Fiddle url quick access
For convenience, [this file](db_fiddle_public_urls.md) contains db-fiddle links for each LeetCode SQL problem. This might be useful if you want to to test your queries on just a few problems, you don't have Python, etc.
