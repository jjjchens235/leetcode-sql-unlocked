import os
import sys

version = sys.version_info[:3]
if version < (3, 6, 0):
  sys.exit( 'Requires Python >= 3.6.0; '
            'your version of Python is ' + sys.version )

CONFIG_FILE_PATH = 'leetcode_sql_unlocked/src/config.py'
CONFIG_FILE_TEMPLATE = """
'''
The following db-fiddle settings can be optionally configured inside leetcode_sql_unlocked/src/config.py:

DB_ENGINE: User has the following databases to choose from: MYSQL_8, POSTGRES_12, and SQLITE_3_3. Default is MYSQL_8.

SAVE_BEFORE_CLOSING: If True, before going to the next question or exiting, will save the current fiddle automatically. Note that the fiddle is always saved when first created- this setting is for all proceeding saves. Default is True, meaning the fiddle will be saved.

CHECK_NEW_SAVE_VERSIONS: If True, will check for any newer versions of the db-fiddle. Default is False. This setting should only be switched to True if user is planning to make changes to their db-fiddles outside of this program.
'''

mysql = 'MYSQL_8.0'
postgres = 'POSTGRES_12'
sqlite = 'SQLITE_3_3'
__DB_OPTIONS = {mysql: 0,
postgres: 5,
sqlite: 11}

cfg = dict(
    db_engine = __DB_OPTIONS[mysql],
    is_save_before_closing = True,
    is_check_new_save_versions = False,
    is_fork_public_url = True,
    is_preload = True,
    n_to_preload = 1,
    n_same_level_to_preload = 1
)
"""

os.chdir(os.path.dirname(os.path.realpath(__file__)))
if os.path.exists(CONFIG_FILE_PATH):
    status = 'updated'
else:
    status = 'created'


with open(CONFIG_FILE_PATH, "w") as config_file:
    config_file.write(CONFIG_FILE_TEMPLATE)
    print("Config {} successfully in path:\n{}".format(status, os.path.join(os.getcwd(), CONFIG_FILE_PATH)))
