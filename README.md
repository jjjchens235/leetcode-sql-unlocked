Through the command line, the user can easily access all ~125 LeetCode SQL/Database questions, even locked ones!! and automatically generate the tables in db-fiddle.com, a SQL database playground environment.


![GIF demo](img/demo2.gif)

## Features
* Auto-generate tables from each SQL/Database LeetCode problem into db-fiddle so all your queries can be tested
* Past db-fiddles are saved, so progress is never lost and the user can continue right where they left off
* Convenient LeetCode question navigation, by level or by number
* Solutions tab easily opened

## Getting Started
1. Requires Google Chrome which can be downloaded from https://www.google.com/chrome/browser/desktop/index.html.
2. Python 3.6+. If you don't already have Python 3 installed, visit https://www.python.org/downloads/.
3. The only dependency is selenium. Either install using `pip install selenium` or use the requirements.txt file included in the repo: `pip install -r requirements.txt`.
4. Run `setup.py` to create a config file with default settings.
5. And you're all set. To start the program run `leetcode_sql_unlocked/leetcode_sql_unlocked.py` and follow the onscreen prompt.

## Command Line Options
`(h)elp`: Show this help menu.

`(n)ext [LEVEL]`: Select next problem. Optionally, go next by level [(e)asy, (m)edium, (h)ard], default ignores levels. Ex: 'n' to go to next problem, 'ne' to go to next easy problem.

`(q)uestion NUMBER`: Select problem by question number. Ex: 'q 183' or simply '183' to go to question 183.

`(s)olution`: Open solution of current problem in new chrome tab. If solution is not found, will do a google search in a new window

`(d)isplay [LEVEL] [# TO DISPLAY]`: Displays list of problems. Optionally, can display by level [(e)asy, (m)edium, (h)ard]. Furthermore, can optionally choose how many problems to display, default is 15. Ex: 'd' is to display next 15 problems of all levels, 'd e 30' is to display the next 30 easy problems.

`(l)oad ON/OFF`: Pre-load additional questions in the background for faster future question access. Ex: 'l on' is to turn load on, and 'l off' is to turn load off"

`(e)xit`: Exit Program

## Config
These settings can be configured within *leetcode_sql_unlocked/src/config.py*:
1. db-fiddle settings
	* `db_engine`: User has the following databases to choose from: MYSQL_8, POSTGRES_12, and SQLITE_3_3. Default is `MYSQL_8`.
	* `save_before_closing`: If `True`, before going to the next question or exiting, will save the current fiddle automatically. Default is `False`, meaning the user must manually click save if they want the changes they made to persist beyond the current session.
		* Note that the fiddle is always saved when first created- this setting is for all proceeding saves.
	* `check_new_save_versions`: If `True`, will check for any newer versions of an existing db-fiddle. Default is `False`. This setting should only be switched to True if user is planning to make changes to their db-fiddles outside of this program.
	
2. forking
	* `is_fork_public_url`: If `True`, will try to create a new db-fiddle by forking the public db fiddle url that is provided in db_fiddle_public_urls.md. If `False`, will create a brand new fiddle from scratch. The default is True.
		* Most likely, this should be kept as True as forking an existing fiddle is faster than creating a new one. The exception might be if the user wants to create a db-fiddle with a different config than the one provided in the public url, such as using Postgres rather than MySQL.
		
3. preloading
	* `is_preload`: If `True`, preloading will be turned on and if `False` it will be turned off. True by default. 
		* This can be toggled within the program itself by using 'l on' and 'l off'.
	* `n_to_preload`: For each question selected, the number of succeeding questions to preload in the background. The default is `1`. 
	* `n_same_level_to_preload`: For each question selected, the number of succeeding questions of the SAME LEVEL to preload in the background. The default is `1`.

##### Additional notes on pre-loading
Preloading refers to creating additional db-fiddles in a background/headless web driver. The questions that will be preloaded are those that are next in line numerically from the question the user is currently on.

Preloading should be useful for most users as it allows for minimized load times, especially for db-fiddles that need to be created from scratch (not forked). It should be turned off though if the user is planning on navigating questions in a non-sequential manner or if there are computer performance issues.

## Known Issues
* Some problems don't have actual table data. For example problem #175 only includes table schemas, so no tables can be parsed, the table schemas need to be loaded manually into db-fiddle.com.
* DB-fiddle.com issues
	* Columns with only blank values are parsed as INTEGER in db-fiddle's text to DDL parser. However, this ends up throwing an error when the tables are actually queried on. This issue occurs for problem #586, a simple fix is switching from INTEGER to VARCHAR(1) in the table schema.
	* Columns with %Y-%m, i.e. '2017-05' are parsed as DATETIME when they should be parsed as VARCHAR inside db-fiddle's text to DDL. A simple fix is switching from DATETIME to VARCHAR(7) in the table schema. This issue occurs for #615.

## DB Fiddle url quick access
For convenience, [this file](db_fiddle_public_urls.md) contains db-fiddle links for each LeetCode SQL problem. This might be useful if you want to to test your queries on just a few problems, you don't have Python, etc.

## Future Ideas
* Create public db-fiddles for Postgres and sqlite as well.
* Create db-fiddle solution links for each question instead of using github solutions which doesn't contain every solution and loads slower.
