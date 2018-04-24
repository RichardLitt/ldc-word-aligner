#!/ldc/bin/python2.6
# dialogs.py

"""Module for dialogs used with aligner tool.
Dialogs:
- NewProjectWizard
- StartupDialog
- DumbDialog
- DumbDialogWithCancel
- WarningDialog
- PopupDialog
- ChangeFont
"""

from utils import *


class NewProjectWizard(QWizard):
    """A custom wizard for starting new projects in the word alignment
    tool. Each page is created by calling the corresponding createPage
    methods within the class.
    Attributes:
    - IntroPage
    - TokenInputPage
    - WaOutPage
    - RawInputPage
    """
    def __init__(self, parent=None):
        """Calls the create page methods and assembles the wizard
        in the required order
        """
        super(NewProjectWizard, self).__init__(parent)
        self.addPage(self.createIntroPage())
        self.addPage(self.createTokenInputPage())
        self.addPage(self.createWaOutPage())
        self.addPage(self.createRawInputPage())

        self.setWindowTitle("Create New Project Wizard")

    def getFilenames(self):
        """Returns a list of filenames in the following order:
        sourceTok, transTok, waOut, sourceRaw, transRaw
        @return list of string filenames
        """
        return [str(self.sourceTok_edit.text()),
                     str(self.transTok_edit.text()),
                     str(self.waOut_edit.text()),
                     str(self.sourceRaw_edit.text()),
                     str(self.transRaw_edit.text())]
        # Account for possible whitspace in filenames
        # return [x.replace(' ', '\ ') for x in filenames]

    def createIntroPage(self):
        """Creates an introductory wizard page"""
        page = QWizardPage(self)
        page.setTitle("Introduction")

        label = QLabel("This wizard will help you start a new project. "
                       "Please use full pathnames.")
        label.setWordWrap(True)

        layout = QVBoxLayout(self)
        layout.addWidget(label)
        page.setLayout(layout)

        return page

    def _validatePage(self, edit_lines):
        """Subroutine for checking whether the information entered
        in a wizard page is valid. Checks that the filepaths entered
        by the user exist.
        @param edit_lines List of QLineEdit objects with texts to check
        """
        for edit_line in edit_lines:
            if not os.path.isfile(str(edit_line.text())) and \
                   str(edit_line.text()) != '':
                QMessageBox.warning(None, "File Load Error",
                                    str(edit_line.text()) +
                                    " is not a valid file.")
                return False
        return True
    
    def _textFileDialog(self, line_edit_field):
        """Custom button action to start dialog. Need a new dialog for each consecutive
        push of the button hence the function.
        @param line_edit_field The QLineEdit object holding the filename.
        """
        dialog = QFileDialog()
        dialog.setFileMode(QFileDialog.ExistingFile)
        dialog.setFilter("Text Files (*.txt *.tkn *.raw);; All Files (*.*)")
        self.connect(dialog, SIGNAL("fileSelected(QString)"), line_edit_field.setText)
        dialog.exec_()
        
    def createTokenInputPage(self):
        """Creates a Token Input Page for user to enter source and translated
        token files. Contains one entry field for each file with a browse button
        that triggers QFileDialog. Moves forward through the wizard only if the
        files exist.
        """
        page = QWizardPage(self)
        page.setTitle("Input File Selection")
        page.setSubTitle("Please select corresponding source and translation files")

        sourceTok_label = QLabel("Source token input file: ")
        sourceTok_edit = QLineEdit()
        sourceTok_edit.setMinimumWidth(300)  # Sets example for the rest
        sourceTok_button = QPushButton("Browse..")
        
        transTok_label = QLabel("Translation token input file: ")
        transTok_edit = QLineEdit()
        transTok_button = QPushButton("Browse..")
        
        self.sourceTok_edit = sourceTok_edit
        self.transTok_edit = transTok_edit

        def _isComplete():
            return str(sourceTok_edit.text()) != '' \
                   and str(transTok_edit.text()) != ''
        
        # Override isComplete so that it checks for text in edit fields
        page.isComplete = _isComplete
        # Connect page to lineEdit to check for changes in isComplete
        page.connect(sourceTok_edit, SIGNAL("textChanged(QString)"),
                     page, SIGNAL("completeChanged()"))
        page.connect(transTok_edit, SIGNAL("textChanged(QString)"),
                     page, SIGNAL("completeChanged()"))
        # Override validatePage with local function
        page.validatePage = functools.partial(self._validatePage,
                                              [sourceTok_edit, transTok_edit])

        ## File Dialog Connections
        # 'Browse..' -> open file dialog
        page.connect(sourceTok_button, SIGNAL("clicked()"),
                     functools.partial(self._textFileDialog, sourceTok_edit))
        page.connect(transTok_button, SIGNAL("clicked()"),
                     functools.partial(self._textFileDialog, transTok_edit))

        ## Layout
        default_layout = QGridLayout()

        default_layout.addWidget(sourceTok_label, 0, 0)
        default_layout.addWidget(sourceTok_edit, 1, 0, 1, 1)
        default_layout.addWidget(sourceTok_button, 1, 2)

        default_layout.addWidget(transTok_label, 2, 0)
        default_layout.addWidget(transTok_edit, 3, 0, 1, 1)
        default_layout.addWidget(transTok_button, 3, 2)

        page.setLayout(default_layout)
        return page

    def createWaOutPage(self):
        """Creates wizard page with single filename input for waOut filepath.
        The waOut filepath is created by the program, not loaded. Therefore, the
        user must enter a filename manually unless they wish to overwrite the file
        they choose in the file dialog. The file dialog can be used to navigate
        to the required directory in order to minimize the typing of the file path.
        """
        page = QWizardPage(self)
        page.setTitle("Output File Selection")
        page.setSubTitle("Please create a filename to use as output.")
        note = QLabel("Note: You may navigate to a selected directory using the browse "
                      "button,\nbut you must create a file name within the find "
                      "file dialog of type .wa")
        
        waOut_label = QLabel("Word Alignment output file: ")
        waOut_edit = QLineEdit()
        waOut_button = QPushButton("Browse..")

        self.waOut_edit = waOut_edit

        def _isComplete():
            return str(waOut_edit.text())[-3:] == '.wa'
        
        # Override isComplete so that it checks for text in edit fields
        page.isComplete = _isComplete
        page.connect(waOut_edit, SIGNAL("textChanged(QString)"),
                     page, SIGNAL("completeChanged()"))
        # Custom button action to start dialog. Need a new dialog for each consecutive
        # push of the button hence the function
        def _WAFileDialog(line_edit_field):
            dialog = QFileDialog()
            dialog.setFileMode(QFileDialog.AnyFile)
            dialog.setFilter("WA Files (*.wa)")
            page.connect(dialog, SIGNAL("fileSelected(QString)"), line_edit_field.setText)
            dialog.exec_()
        
        self.connect(waOut_button, SIGNAL("clicked()"),
                     functools.partial(_WAFileDialog, waOut_edit))
        
        default_layout = QGridLayout(self)
        default_layout.addWidget(waOut_label, 0, 0)
        default_layout.addWidget(waOut_edit, 1, 0, 1, 1)
        default_layout.addWidget(waOut_button, 1, 2)
        default_layout.addWidget(note, 3, 0, 1, 0)
        default_layout.setRowMinimumHeight(2, 40)
        page.setLayout(default_layout)
        return page

    def createRawInputPage(self):
        page = QWizardPage(self)
        page.setTitle("Raw Input Selection")
        page.setSubTitle("Optional: Select raw language files to include original "
                      "sentences in word alignment tool.")
        # Row 4: source raw
        sourceRaw_label = QLabel("Source raw input file: ")
        sourceRaw_edit = QLineEdit()
        sourceRaw_edit.setMinimumWidth(300) # Again
        sourceRaw_button = QPushButton("Browse..")
        # Row 5: translation raw
        transRaw_label = QLabel("Translated raw input file: ")
        transRaw_edit = QLineEdit()
        transRaw_button = QPushButton("Browse..")
        
        self.sourceRaw_edit = sourceRaw_edit
        self.transRaw_edit = transRaw_edit

        page.validatePage = functools.partial(self._validatePage,
                                              [sourceRaw_edit, transRaw_edit])

        self.connect(sourceRaw_button, SIGNAL("clicked()"),
                     functools.partial(self._textFileDialog, sourceRaw_edit))
        self.connect(transRaw_button, SIGNAL("clicked()"),
                     functools.partial(self._textFileDialog, transRaw_edit))

        default_layout = QGridLayout(self)
        default_layout.addWidget(sourceRaw_label, 0, 0)
        default_layout.addWidget(sourceRaw_edit, 1, 0, 1, 1)
        default_layout.addWidget(sourceRaw_button, 1, 2)

        default_layout.addWidget(transRaw_label, 2, 0)
        default_layout.addWidget(transRaw_edit, 3, 0, 1, 1)
        default_layout.addWidget(transRaw_button, 3, 2)
        page.setLayout(default_layout)
        return page


class StartupDialog(QDialog):
    """A wrapper class for the File/New and File/Open dialogs. This dialog
    is loaded on startup of the program when no file(s) has been selected.
    The user can then open a new project by selecting a .WA file from the
    open file dialog, or start a new project by clicking 'new project' and
    starting the newProjectWizard. In both cases, the program will load the
    resulting .WA file.
    Attributes:
    - filename: The .wa filename to load after user has made their selection.
    """
    def __init__(self, language_mode, parent=None):
        """Creates a new startup dialog with text prompt and buttons
        New Project, Open Project, and Quit."""
        super(StartupDialog, self).__init__(parent)
        self.setWindowTitle("Create or Open Project")
        self.parent = parent
        self.filename = None
        self.language_mode = language_mode
        
        prompt = QLabel("Please select a project to open or "
        "create a new one.")

        newButton = QPushButton("&New Project")
        openButton = QPushButton("&Open Project")
        cancelButton = QPushButton("&Quit")

        self.ARButton = QRadioButton("&LDC Arabic Config")
        self.CHButton = QRadioButton("&LDC Chinese Config")
        self.defaultButton = QRadioButton("&Default Config")
        self.defaultButton.setChecked(True)
            
        self.connect(newButton, SIGNAL("clicked()"), self.newProject)
        self.connect(openButton, SIGNAL("clicked()"), self.openProject)
        self.connect(cancelButton, SIGNAL("clicked()"), self.close)

        buttonLayout = QHBoxLayout()
        buttonLayout.addWidget(newButton)
        buttonLayout.addWidget(openButton)
        buttonLayout.addWidget(cancelButton)
        radioLayout = QHBoxLayout()
        radioLayout.addWidget(self.defaultButton)
        radioLayout.addWidget(self.ARButton)
        radioLayout.addWidget(self.CHButton)
        mainLayout = QVBoxLayout()
        mainLayout.addWidget(prompt)
        if not self.language_mode:
            mainLayout.addLayout(radioLayout)
        mainLayout.addLayout(buttonLayout)
        self.setLayout(mainLayout)

    def newProject(self):
        """Creates a new project wizard and runs it. Once it is done,
        collects the relevant filename information, runs it through
        sen2pa with createWAFile() and gives the .wa filename back to
        the main frame to load.
        """
        wizard = NewProjectWizard()
        if wizard.exec_():
            files = wizard.getFilenames()
            try:
                createWAFile(files[0], files[1],
                             files[2],
                             None if files[3] == '' else files[3],
                             None if files[4] == '' else files[4])
            except IOError, e:
                print e
                QMessageBox.warning(None, "File Error",
                                    "There was a problem creating the new project. "
                                    "Please check that all files exist and are valid "
                                    "token/raw files.")
                wizard.close()
                return
            except AssertionError, e:
                print e
                QMessageBox.warning(None, "File Error", str(e))
                wizard.close()
                return
            else:
                self.filename = files[2]
                self.accept()
        
    def openProject(self):
        """Starts the open file dialog and stores the name of the selected
        file. If the user clicks 'Cancel', it simply closes."""
        open_dialog = QFileDialog()
        open_dialog.setFileMode(QFileDialog.ExistingFile)
        filters = ["WA Files (*.wa)", "All Files (*.*)"]
        open_dialog.setFilters(QStringList(filters))
        if open_dialog.exec_():
            filenames = open_dialog.selectedFiles()
            self.filename = str(filenames[0])
            self.accept()
        else:
            pass
            # Here should return to parent selector
            #raise Usage("File not selected")

    def _getLanguage(self):
        if self.ARButton.isChecked():
            self.language_mode = AR
        elif self.CHButton.isChecked():
            self.language_mode = CH
        else:
            self.language_mode = DEFAULT
            
    def getInfo(self):
        self._getLanguage()
        return (self.filename, self.language_mode)


class DumbDialog(QDialog):
   def __init__(self, text, parent=None):
        super(DumbDialog, self).__init__(parent)   
	self.setWindowTitle("Trouble")
	
	okButton = QPushButton("&Yes")
	cancelButton = QPushButton("No")
	self.connect(okButton, SIGNAL("clicked()"), self, SLOT("accept()"))
	self.connect(cancelButton, SIGNAL("clicked()"), self, SLOT("reject()"))

	buttonLayout = QHBoxLayout()
	buttonLayout.addWidget(okButton)
	buttonLayout.addWidget(cancelButton)

	mainLayout = QVBoxLayout()
	mainLayout.addWidget(text)
	mainLayout.addLayout(buttonLayout)
	self.setLayout(mainLayout)


class SaveOnQuitDialog(QDialog):
   def __init__(self, text, data, parent=None):
        super(SaveOnQuitDialog, self).__init__(parent)   
	self.setWindowTitle("Trouble")
        self.parent = parent
        self.data = data
	
	yesButton = QPushButton("&Yes")
	noButton = QPushButton("&No")
        cancelButton = QPushButton("&Cancel")

	self.connect(yesButton, SIGNAL("clicked()"), self.save)
        self.connect(noButton, SIGNAL("clicked()"), self.noSave)
	self.connect(cancelButton, SIGNAL("clicked()"), self, SLOT("reject()"))
        self.connect(yesButton, SIGNAL("clicked()"), self, SLOT("accept()"))
        self.connect(noButton, SIGNAL("clicked()"), self, SLOT("accept()"))

	buttonLayout = QHBoxLayout()
	buttonLayout.addWidget(yesButton)
        buttonLayout.addWidget(noButton)
	buttonLayout.addWidget(cancelButton)

	mainLayout = QVBoxLayout()
	mainLayout.addWidget(text)
	mainLayout.addLayout(buttonLayout)
	self.setLayout(mainLayout)

   def save(self):
       print "Saving",
       self.data.comment[self.parent.sent] = self.parent.commentField.text()   
       self.data.save()

   def noSave(self):
       print "Not saving",


class WarningDialog(QDialog):
    def __init__(self, text, parent=None):
        super(WarningDialog, self).__init__(parent)	    
	self.setWindowTitle("Warning")
	okButton = QPushButton("&OK")
	layout = QGridLayout()
	layout.addWidget(text,0,0)
	layout.addWidget(okButton,1,0)
	self.setLayout(layout)
	self.connect(okButton, SIGNAL("clicked()"), self, SLOT("accept()"))


class PopupDialog(QDialog):         # copy/paste window
    def __init__(self, text, language_mode, parent=None):
        super(PopupDialog, self).__init__(parent)
	layout = QGridLayout()
        textEdit = QTextEdit()
        ######### Language Specific ##########
        if language_mode in (DEFAULT, AR):
            font = QFont(source_text_font[0],16,source_text_bold)
        else:
            font = QFont(source_text_font[1], 16, source_text_bold)
        ######### Language Specific ##########
        textEdit.setFont(font)
        textEdit.setText(text)
        textEdit.setReadOnly(True)
	layout.addWidget(textEdit,0,0)
       	okButton = QPushButton("&OK")
	layout.addWidget(okButton,1,0)
	self.setLayout(layout)
	self.connect(okButton, SIGNAL("clicked()"), self, SLOT("accept()"))


class ChangeFont(QDialog):
   def __init__(self, parent=None):
        super(QDialog, self).__init__(parent)   
        self.parent = parent

        inst1 = QLabel("Be sure to enter a valid font name.")
        inst2 = QLabel("Valid values for weight are between 1 and 99.")
#                          Bold weight is 75 and normal is 50.''')

        l1 = QLabel("Source Box Font")
        l2 = QLabel("Source Box Font Size")
        l3 = QLabel("Source Box Font Weight")
        
        l4 = QLabel("English Box Font")
        l5 = QLabel("English Box Font Size")
        l6 = QLabel("English Box Font Weight")

        l7 = QLabel("Source Text Font")
        l8 = QLabel("Source Text Font Size")
        l9 = QLabel("Source Text Font Weight")

        l10 = QLabel("English Text Font")
        l11 = QLabel("English Text Font Size")
        l12 = QLabel("English Text Font Weight")

        self.v1 = QLineEdit()
        self.v1.setText(source_box_font)
        self.v1.setFixedWidth(200)
        self.v2 = QLineEdit()
        self.v2.setText(str(source_box_size))
        self.v2.setFixedWidth(200)
        self.v3 = QLineEdit()
        self.v3.setText(str(source_box_bold))
        self.v3.setFixedWidth(200)
        self.v4 = QLineEdit()
        self.v4.setText(english_box_font)
        self.v4.setFixedWidth(200)
        self.v5 = QLineEdit()
        self.v5.setText(str(english_box_size))
        self.v5.setFixedWidth(200)
        self.v6 = QLineEdit()
        self.v6.setText(str(english_box_bold))
        self.v6.setFixedWidth(200)
        self.v7 = QLineEdit()        
        self.v7.setText(source_text_font)
        self.v7.setFixedWidth(200)
        self.v8 = QLineEdit()        
        self.v8.setText(str(source_text_size))
        self.v8.setFixedWidth(200)
        self.v9 = QLineEdit()
        self.v9.setText(str(source_text_bold))
        self.v9.setFixedWidth(200)
        self.v10 = QLineEdit()
        self.v10.setText(english_text_font)
        self.v10.setFixedWidth(200)
        self.v11 = QLineEdit()
        self.v11.setText(str(english_text_size))
        self.v11.setFixedWidth(200)
        self.v12 = QLineEdit()
        self.v12.setText(str(english_text_bold))
        self.v12.setFixedWidth(200)

        layout = QGridLayout()
        layout.addWidget(l1, 0, 0)
        layout.addWidget(l2, 1, 0)
        layout.addWidget(l3, 2, 0)
        layout.addWidget(l4, 3, 0)
        layout.addWidget(l5, 4, 0)
        layout.addWidget(l6, 5, 0)
#        layout.addWidget(l7, 6, 0)
#        layout.addWidget(l8, 7, 0)
#        layout.addWidget(l9, 8, 0)
#        layout.addWidget(l10, 9, 0)
#        layout.addWidget(l11, 10, 0)
#        layout.addWidget(l12, 11, 0)
        layout.addWidget(self.v1, 0, 1)
        layout.addWidget(self.v2, 1, 1)
        layout.addWidget(self.v3, 2, 1)
        layout.addWidget(self.v4, 3, 1)
        layout.addWidget(self.v5, 4, 1)
        layout.addWidget(self.v6, 5, 1)
#        layout.addWidget(self.v7, 6, 1)
#        layout.addWidget(self.v8, 7, 1)
#        layout.addWidget(self.v9, 8, 1)
#        layout.addWidget(self.v10, 9, 1)
#        layout.addWidget(self.v11, 10, 1)
#        layout.addWidget(self.v12, 11, 1)
        
        okButton = QPushButton("Save Values")
        okButton.setFixedWidth(100)
        self.connect(okButton, SIGNAL("clicked()"), self.ok)

        mainLayout = QVBoxLayout()
        mainLayout.addLayout(layout)
        mainLayout.addWidget(okButton)
        mainLayout.setStretchFactor(layout,20)
        mainLayout.setStretchFactor(okButton,1)

        self.setLayout(mainLayout)
       
   def ok(self):
       # save values
       source_box_font = self.v1.text()
       source_box_size = int(self.v2.text())
       source_box_bold = int(self.v3.text())
       english_box_font = self.v4.text()
       english_box_size = int(self.v5.text())
       english_box_bold = int(self.v6.text())
#       source_text_font = self.v7.text()
#       source_text_size = int(self.v8.text())
#       source_text_bold = int(self.v9.text())
#       english_text_font = self.v10.text()
#       english_text_size = int(self.v11.text())
#       english_text_bold = int(self.v12.text())
