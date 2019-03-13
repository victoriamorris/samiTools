#  -*- coding: utf8 -*-

"""Functions used within samiTools."""

# Import required modules
from collections import OrderedDict
import datetime
import fileinput
import gc
import getopt
import html
import locale
import os
import re
import string
import sys
import textwrap
import unicodedata

__author__ = 'Victoria Morris'
__license__ = 'MIT License'
__version__ = '1.0.0'
__status__ = '4 - Beta Development'


# ====================
#      Constants
# ====================


SAMI_SUFFICES = ('export_ALL', 'export_DOCRECITEM', 'export_MLRECITEM', 'export_PUBLPROD', 'export_WORK', 'export_WRSECITEM')
PRIMO_FLAGS = ('primo_dels', 'primo_upd')


# ====================
#       Classes
# ====================


class FilePath:
    """Class for working with files"""

    def __init__(self, path=None, function='input'):
        self.path = None
        self.function = function
        self.folder, self.filename, self.ext = '', '', ''
        self.file_object = None
        self.file_writer = None
        if path: self.set_path(path)

    def set_path(self, path):
        self.path = path
        expected_ext = ['.txt', '.prn', '.xml'] if self.function == 'input' else ['.lex', '.xml']
        if not path or path == '':
            exit_prompt('Error: Could not parse path to {} file'.format(self.function))
        try:
            self.filename, self.ext = os.path.splitext(os.path.basename(path))
            self.folder = os.path.dirname(path)
        except:
            exit_prompt('Error: Could not parse path to {} file'.format(self.function))
        if self.ext not in expected_ext:
            exit_prompt('Error: The specified file should have the extension {}'.format(' or '.join(expected_ext)))
        if 'output' not in self.function and not os.path.isfile(os.path.join(self.folder, self.filename + self.ext)):
            exit_prompt('Error: The specified {} file cannot be found'.format(self.function))


# ====================
#  General Functions
# ====================


def print_opt(o, v, indent=5):
    """Function to print information about options/arguments for a function"""
    print('{}{:<10}  {:<40}'.format(' ' * indent, o, textwrap.fill(v, width=60 - indent, subsequent_indent=' ' * (indent + 12))))


def date_time(message='All processing complete'):
    """Function to print a message, followed by the current date and time"""
    if message: print('\n\n' + str(message))
    print('----------------------------------------')
    print(str(datetime.datetime.now()))


def date_time_exit():
    """Function to exit the program after displaying the current date and time"""
    date_time()
    sys.exit()


def exit_prompt(message=None):
    """Function to exit the program after prompting the use to press Enter"""
    if message: print(str(message))
    input('\nPress [Enter] to exit...')
    sys.exit()


# ====================
#    Functions for
#   cleaning strings
# ====================


def clean_text(s):
    """Function to remove control characters and escape invalid HTML characters <>&"""
    if s is None or not s: return None
    return html.escape(re.sub(r'[\u0000-\u001F\u007F-\u009F]', '', html.unescape(s)))