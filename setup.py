import os
import sys

version = sys.version_info[:3]
if version < (3, 6, 0):
  sys.exit( 'Requires Python >= 3.6.0; '
            'your version of Python is ' + sys.version )

CONFIG_FILE_PATH = 'src/config.py'
CONFIG_FILE_TEMPLATE = """
'''
The following db-fiddle settings can be optionally configured inside leetcode_sql_unlocked/src/config.py:

DB_ENGINE: User has the following databases to choose from: MYSQL_8, POSTGRES_12, and SQLITE_3_3. Default is MYSQL_8.

SAVE_BEFORE_CLOSING: If True, before going to the next question or exiting, will save the current fiddle automatically. Note that the fiddle is always saved when first created- this setting is for all proceeding saves. Default is False, meaning the user must manually click save if they want the changes they made to persist beyond the current session.

CHECK_NEW_SAVE_VERSIONS: If True, will check for any newer versions of the db-fiddle. Default is False. This setting should only be switched to True if user is planning to make changes to their db-fiddles outside of this program.
'''

__DB_OPTIONS = {'MYSQL_8': 0,
'POSTGRES_12': 5,
'SQLITE_3_3': 11}

DB_ENGINE = __DB_OPTIONS['MYSQL_8']
SAVE_BEFORE_CLOSING = False
CHECK_NEW_SAVE_VERSIONS = False

#pre-loading settings
is_pre_load_questions = True
N_TO_PRELOAD = 1
N_SAME_LEVEL_TO_PRELOAD = 1
"""

os.chdir(os.path.dirname(os.path.realpath(__file__)))
if os.path.exists(CONFIG_FILE_PATH):
    status = 'updated'
else:
    status = 'created'


with open(CONFIG_FILE_PATH, "w") as config_file:
    config_file.write(CONFIG_FILE_TEMPLATE)
    print("Config {} successfully in path {}".format(status, os.path.join(os.getcwd(), CONFIG_FILE_PATH)))
