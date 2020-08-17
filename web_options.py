
__DB_OPTIONS = 
{'MYSQL_8': 0,
'POSTGRES_12': 5,
'SQLITE_3_3': 11}

#default is mySQL8
DB_ENGINE = __DB_OPTIONS['MYSQL_8']

# Default is true. If true, before going to the next question or exiting, will save the current fiddle automatically
SAVE_BEFORE_CLOSING = True

#Default is false, if true, will check for any newer versions of the saved db fiddle url. This could be useful if user is planning to make changes to db-fiddles outside of the program
CHECK_NEW_SAVE_VERSIONS = False
