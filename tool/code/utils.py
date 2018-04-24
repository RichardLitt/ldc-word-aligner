#!/ldc/bin/python2.6
# utils.py
"""Utilities module for alignerAR.py. Includes various global helper methods.
Functions:
- createWAFile
- formatBlock
- isInt
"""

# system modules
import sys
import random
import os
import functools
import re
import string
import platform
import shutil
import commands
import subprocess
import PyQt4.Qt
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from unicodedata import *
import getopt

# shared modules
import sen2pa

# Language Constants
AR = "AR"
CH = "CH"
DEFAULT = "default"

# Global Variables
version = "1.20"
data = None

# For independent testing
python_ = '/ldc/bin/python2.6'
if not os.path.exists('/ldc/bin/python2.6'):
    python_ = 'python'


## Program settings / parameters
box_size = 30  # height between consecutive boxes, must be even number

# position of boxes
sbox = 50
stext = 55
stag = 160

tbox = 280
ttext = 285
ttag = 390

# fonts and sizes
if commands.getstatusoutput('uname -s')[1] == 'Linux':
    source_box_font = ("Sans Serif", "Times New Roman")
else:
    source_box_font = ("Arial", "Times New Roman")
source_box_size = (22, 16)
source_box_bold = QFont.Normal

english_box_font = "Times New Roman"
english_box_size = (18, 16)
english_box_bold = QFont.Normal

source_text_font = ("Arial", "Times New Roman")
source_text_size = (20, 16)
source_text_bold = QFont.Bold

english_text_font = "Times New Roman"
english_text_size = 16
english_text_bold = QFont.Normal

link_table_font = "Helvetica"
link_table_size = 12
link_table_bold = QFont.Normal

# Preset tags
AR_tags = [("Unmatched and Glued", "GLU"),
           ("Meta word", "MET"),
           ("Tokenization Error", "TOK"),
           ("Typo", "TYP"),
           ("Markup attached", "MRK"),
           ("<delete existing tag>", "")]
CH_tags = [("Function", "FUN"),
           ("DE-clause", "DEC"),
           ("DE-modifier", "DEM"),
           ("DE-possessive", "DEP"),
           ("Tense/Passive", "TEN"),
           ("Omni-function-preposition", "OMN"),
           ("Possessive", "POS"),
           ("To-infinitive", "TOI"),
           ("Sentence Marker", "SEN"),
           ("Measure-word", "MEA"),
           ("Determiner/demonstrative", "DET"),
           ("Clause marker", "CLA"),
           ("Anaphoric-reference", "ANA"),
           ("Local context marker", "LOC"),
           ("Rhetorical", "RHE"),
           ("NotTranslated: Context obligatory", "COO"),
           ("NotTranslated: Context optional", "CON"),
           ("NotTranslated: Incorrect", "INC"),
           ("Typo", "TYP"),
           ("Markup attached", "MRK"),
           ("Meta word", "MET"),
           ("<delete existing tag>", "")]

# Helper methods
def createWAFile(sourceTok, transTok, waOut, sourceRaw=None, transRaw=None):
    """Performs sen2pa.main() on source, translation files to create new WA file
    @param sourceTok
    @param transTok
    @param waOut The name of the created .wa file
    @param sourceRaw
    @param transRaw
    @return waOut The name of the created .wa file
    """
    argv = ['-c']
    argv += ['-s'] + [sourceTok]
    argv += ['-t'] + [transTok]
    argv += ['-w'] + [waOut]
    if sourceRaw != None:
        argv += ['-r'] + [sourceRaw]
    if transRaw != None:
        argv += ['-q'] + [transRaw]
    sen2pa.main(argv)
    return waOut

def formatBlock(block):
        '''Format the given block of text, trimming leading/trailing
        empty lines and any leading whitespace that is common to all lines.
        The purpose is to let us list a code block as a multiline,
        triple-quoted Python string, taking care of indentation concerns.'''
        # separate block into lines
        lines = str(block).split('\n')
        # remove leading/trailing empty lines
        while lines and not lines[0]:  del lines[0]
        while lines and not lines[-1]: del lines[-1]
        # look at first line to see how much indentation to trim
        ws = re.match(r'\s*',lines[0]).group(0)
        if ws:
                lines = map( lambda x: x.replace(ws,'',1), lines )
        # remove leading/trailing blank lines (after leading ws removal)
        # we do this again in case there were pure-whitespace lines
        while lines and not lines[0]:  del lines[0]
        while lines and not lines[-1]: del lines[-1]
        return '\n'.join(lines)+'\n'

def isInt( str ):
	""" Is the given string an integer?	"""
	ok = 1
	try:
		num = int(str)
	except ValueError:
		ok = 0
	return ok


