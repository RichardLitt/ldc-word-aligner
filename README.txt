LDC Word Aligner
version 1.20

Stephen Grimes
sgrimes@ldc.upenn.edu
Linguistic Data Consortium
November 2011

Table of Contents
------------------------------------
 1. Description
 2. System Requirements
 3. Package Contents
 4. Getting Started
  4.1 Starting the program
  4.2 Startup Wizard
  4.3 Using the program
 5. Features / Usage
  5.1 Aligment deletion or removing a token from an alignment
  5.2 Adding a token to an alignment
  5.3 Combining two links
  5.4 Automatic file saving
  5.5 Sentence navigation
  5.6 Alignment table
  5.7 Rejecting sentences
  5.8 Undo
  5.9 Colors
 6. Known Issues
 7. Copyright Info
 8. Acknowledgments
------------------------------------

1. Description

The LDC Word Aligner is a Python-based tool used for annotating manual word
alignments (or gold standard alignments). Sentence-segmented parallel texts
are required as input.

2. System Requirements

The tool was developed on a Debian Linux system using Python and PyQt.
Before using the tool, install python2.6 and PyQt4 and ensure that python2.6
is in your path. On a Linux system using apt-get, this can be done as
follows:

 sudo apt-get install python2.6 python-qt4

Test your system setup by typing "python2.6" to start python followed by
"import PyQt4". If this is successful, you have met the required dependencies.

A Windows executable was created using py2exe and is included. It has not been
extensively tested.

3. Package contents

docs/:

 README.txt -- this file
 gpl-3.0.txt -- GNU General Public License

 guidelines/
   Annotator guidelines used by LDC under the GALE project.
   LDC_GALE_Arabic_alignment_guidelines_v6.0.pdf
   LDC_GALE_Chinese_WA_tagging_guidelines_v1.0.pdf
   LDC_GALE_Chinese_alignment_guidelines_v4.0.pdf

 papers/
   Conference proceedings related to LDC Word Aligner.

samples/:

 .wa files
 parallel texts for creating .wa files

scripts/:

 makeWA.pl - create an empty .wa file from two parallel .txt files
 reverseWA.pl - switch source and translation lanaguages in a WA file
 compareWA.py - calculate precision, recall, f-score between two WA files
 WordAlignment.py - module used for a variety of manipulations of WA files

tool/:

 ldc_word_aligner - wrapper script to launching tool

 code/
    This directory contains all .py modules files required and the main
    program, aligner.py. Additionally, tags.txt allows for adding or removing
    possible word tags. See header of tags.txt for details.

 windows/
    LDCWordAligner.v1.20.msi - MS Windows installer

4. Getting Started

 4.1 Starting the program

The user changes to the appropriate directory of the executable, or the user
types the entire path to the exectuable. This is optionally followed by the
filename of the alignment file to open.

If no file is specified, a wizard is used to select an existing alignment
file or create one from a source and tokenized pair of files.

  Sample usage:

  a. Full paths, existing file:
  /path/to/tool/aligner.py -f /path/to/file/filename.wa

  b. Relative paths, create blank parallel file from source and tokenized:
  aligner.py -s chinese.tkn -t english.tkn -f parallel.wa

  c. Opening the file to a specific sentence, say the third:
  /path/to/tool/aligner.py -i 3 -f /path/to/file/filename.wa

  If the user does not use -i to specify a sentence to start at, the tool
  will resume to the first sentence for which annotation has not been
  completed.

 4.2 File Wizard

Using the wizard a new .wa file can be created from two language files with
an equal number of sentences. Each sentence must appear on one line. See
examples in the "samples" directory. The wizard can also be used to open an
existing .wa file.

Note: Do not use the option to add "raw" files; it has not been fully
implemented. The wizard offers the option to include raw source files
(untokenized), which can be used to display an alternate version of the
source and translation texts in the sentence navigation area. This current
version of the tool does not fully support raw text data (it will not be
stored properly).

Avoid using the LDC Arabic Config and LDC Chinese Config options. These are
primarily intedended for LDC-internal annotation.

 4.3 Using the program

The user begins by highlighting words to be aligned together. When all
necessary tokens are selected, a link is created by selecting the "Correct"
or "Incorrect" buttons (or choosing the corresponding keyboard shortcuts,
space and "i").

To assign tokens as "Not Translated - Correct" or "Not Translated -
Incorrect" click the appropriate button or use the corresponding shortcut.
For convenience, multiple not translated tokens from the same language can
be highlighted at once and assigned "Not Translated - Correct" by pressing
the space bar.

Tags are selected by right clicking in the box containing a token and
choosing from the context menu. Default tags are Meta Word (MET),
Tokenization Error (TOK), and Typo (TYP), but these can be altered in the
tags.txt configuration file according to the needs of a project.

 4.4 Saving and exiting

The user may save the file at any time by selecting File->Save from the
menu.  The program automatically saves when advancing to the next sentence.

The program does not have Exit option in Menu. Instead, to quit, select the
X at the top corner of your screen (or on some systems Alt+F4. You will be
given the option to save; if you do not save, all annotated sentences but
the last are likely to have been saved.

5. Program features

 5.1 Alignment deletion or removing a token from an alignment

Alignments may be deleted by first selecting the link to delete from the
lower right link table, then clicking the Delete button in the bottom right
corner of the screen. Links selected by clicking them in the annotation
area on the left of the screen can be deleted by clicking the Delete button
or by pressing the Del key on the keyboard. Additionally, individual words
may be removed from a larger link by double clicking on the box of the
word.  If the word is the last remaining word from one language in a link,
the entire link is removed. Deleting "Not Translated" links works the same
way.

 5.2 Adding a token to an alignment

Tokens can be added to existing links by selecting the existing link (either
click on a word that is part of the link or select the link in the table).
Once the existing link is selected, select the word to be added and press
space bar (or "i" for an incorrect link).

 5.3 Combining two links

Multiple alignments can be combined by selecting them while holding down
CTRL on the keyboard and then clicking the appropriate link type button (or
pressing space bar or i) as usal. Once two or more existing links are
selected with the CTRL key, it is possible to add previously unlinked words
as described above in 5.2.

 5.4 Automatic file saving

The user may save the file at any time by selecting File->Save from the
menu.  The program automatically saves when advancing to the next sentence.

 5.5 Sentence navigation (upper right of display)

The Next and Previous buttons may be used for sentence navigation.
Alternatively, the user may change to any sentence by double clicking on
that sentence in the source or translation boxes on the upper right side.
The Refresh button reloads the current sentence and can be used to revert
annotations to the saved version.

 5.6 Alignment table (lower right of display)

The alignment table displays all alignments for the current sentence. It can
be used to quickly review in table format the links for the sentence. The
table is sorted by a given column heading by clicking on that heading.
Selecting a link brings it to focus in the annotation area to the left.
Links can be deleted from this table by clicking the Delete button at the
bottom right corner of the screen.

 5.7 Rejecting sentences

Annotators may explicity reject sentences. This is handled in the edit menu.
This makes clear that the sentence is invalid for annotation for some reason
such as incorrect translation, offensive material, or plain gibberish. The
.wa file for rejected sentences contains status="rejected" instead of
status="".

 5.8 Undo

The Undo button removes the last link in the link table.  This is usually
the last link added, although the order of links in the link table may
change if the sentence is reloaded.

 5.9 Colors

 Annotation area (left side):

 Yellow      Unannotated tokens
 Lavender    Selected tokens
 Green       Composite links
 Light blue  Not translated
 Red         Incorrect, Not Translated Incorrect

 Sentence navigation area (upper right):

 White      Blank sentence (no alignments)
 Red        Partially-annotated sentence
 Green      Completely alignmed sentence

6. Known issues

In order to tag a word, the user may have difficulty if right-clicking on
the word itself. Instead click in an area of the box where there are no
words or tags.

Currently one word is not permitted to be a member of multiple separate
links. Also, if a word is a member of an alignment, it must be linked to all
words in the oppoistive language participating in the alignment. These
behaivors are by design.

The file format for alignments has grown organically but would be useful to
be modified eventually. The current format is designed to be human-readable.

7. Acknowledgments

Thanks to John Mayer, Mishal Awadah, Pranshu Sharma, and Katherine Peterson
for their help in developing, enhancing, and testing features of the tool.

8. Copyright Info

LDC Word Aligner version 1.20 developed by the Linguistic Data Consortium.
Portions (c) 2011 Trustees of the University of Pennsylvania

Portions (c) 2001, 2002, 2003, 2004, 2005, 2006 Python Software
Foundation, All Rights Reserved.

Parts of this program are written in Python, and this package
contains Python runtime.

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License version 3
along with this program. If not, see <http://www.gnu.org/copyleft/gpl.htm>.

----------------------
README Created October 27, 2011 Stephen Grimes
README Modified November 10, 2011 Stephen Grimes
Code copied and uploaded April 24, 2018 Richard Littauer
