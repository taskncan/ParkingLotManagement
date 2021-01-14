# definitions.py
'''
Contains project wide(global) variables
'''
from pathlib import Path
import sys


def init():
    '''
    Creates project wide global variables to be reached within other files
    '''
    # DIR_SRC points to folder of source codes which is *PROJECT_DIRECTORY*/src
    global DIR_SRC
    DIR_SRC = Path(__file__).parent
    sys.path.append(str(DIR_SRC.resolve()))
