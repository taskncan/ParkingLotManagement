from pathlib import Path

# ########################
# DIRECTORIES
# ########################
''' Define new directory variables according to following rules:
    1) Use CAPITAL LETTERS
    2) Start with phrase 'DIR'
    3) Use '_' as delimiter
'''
# DIR_SRC points to the folder source code is being held
DIR_SRC = Path(__file__).parent.resolve()
DIR_ROOT = DIR_SRC.parent  # Points to Root directory of the project

# ########################
# SINGLE FILES
# ########################
''' Define new file variables according to following rules:
    1) Use CAPITAL LETTERS
    2) Start with phrase 'FILE'
    3) Use '_' as delimiter
'''
FILE_REQS = DIR_SRC / "requirements.txt"  # Points to requirements.txt
FILE_FLASK = DIR_SRC / "parkingmanagement.py"
FILE_DATABASE = DIR_SRC / 'parkinglot.db'

# ########################
# SETTINGS
# ########################
DEMO = True
VERBOSE = True
DEBUG = True
CLEAN_DB = True
SILENT_INSTALL = False


# ########################
# CLASS (for Flask)
# ########################
class Config(object):
    SECRET_KEY = 'fission-liturgy9-ru+f_ous-comely-burp'
    """docstring for Config"""
    def __init__(self, arg):
        super(Config, self).__init__()
        self.arg = arg
