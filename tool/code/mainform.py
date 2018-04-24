#!/ldc/bin/python2.6
# mainform.py
"""Holds the MainForm class which is the main window for the Word Alignment tool."""

# local modules
from utils import *
import datamodule
from ui_components import *
from dialogs import *
from QC import *


class MainForm(QMainWindow):
    """The main program window"""
    def __init__(self, paFilename, indexStart, highlightAlignment,
                 language_mode, parent=None):
        super(MainForm, self).__init__(parent)

        self.data = datamodule.DataStructure(paFilename, language_mode)
        self.language_mode = language_mode
        
        getStem = re.compile("([^\/]+)$")
        ssss = getStem.search(paFilename).group(1)
        self.setWindowTitle("LDC Word Aligner " + version + " File: "+ssss)
        self.view = QGraphicsView(self)
        self.scene = QGraphicsScene(self)
        self.view.setScene(self.scene)
        #	self.view.setFocusPolicy(Qt.NoFocus)

        # emish:
	# open program to first sentence to be worked on...
        if indexStart: # -i option
            self.sent = indexStart - 1          ## sentence number
        else: # normal, indexStart is 0
            self.sent = indexStart
            # Goto next unannotated sentence
            while (self.sent < len(self.data.status) \
                   and self.isCompletelyLinked(self.sent)):    
                self.sent += 1
        if (self.sent >= len(self.data.status)):
            self.sent = 0
	sent = self.sent
        print 'Opening tool at sentence ', sent+1

	self.lines = {}

	# Sentence navigation area of layout -- top right
	self.sourceText = TableClass2(self, "s", self.language_mode)
	self.targetText = TableClass2(self, "t", self.language_mode)
 	self.paintSentences()         # print upper right sentence tables

	# Link Table Layout
        self.bottomTable = TableClass(self)
	self.bottomTable.setColumnCount(6)
	self.bottomTable.setAlternatingRowColors(True)
	self.bottomTable.setSelectionBehavior(QTableWidget.SelectRows)
	self.bottomTable.setSelectionMode(QTableWidget.SingleSelection)
	self.bottomTable.setHorizontalHeaderLabels(("Source Token(s)","#",
                                 "Target Token(s)","#","Sent","Link Type"))
	self.bottomTable.resizeColumnsToContents()
        ######## Language Specific ########
        if self.language_mode in (DEFAULT, AR):
            # AR Layout
            self.navArea = NavArea(self.language_mode, self)
            self.linkButtons = LinkButtons(self.language_mode, self)
            
            self.rightSplitter = QSplitter(Qt.Vertical)
            self.rightSplitter.addWidget(self.sourceText)
            self.rightSplitter.addWidget(self.targetText)
            self.rightSplitter.addWidget(self.linkButtons)
            # self.rightSplitter.addWidget(self.buttonArea)
            self.rightSplitter.addWidget(self.bottomTable)
            self.rightSplitter.addWidget(self.navArea)
            self.rightSplitter.setStretchFactor(0,2)
            self.rightSplitter.setStretchFactor(1,2)
            self.rightSplitter.setStretchFactor(2,1)
            self.rightSplitter.setStretchFactor(3,1)
            self.rightSplitter.setStretchFactor(4,2)
            self.rightSplitter.setStretchFactor(5,1)
            self.leftSplitter = QSplitter(Qt.Vertical)
            self.leftSplitter.addWidget(self.view)
            
            self.mainSplitter = QSplitter(Qt.Horizontal)
            self.mainSplitter.addWidget(self.leftSplitter)
            self.mainSplitter.addWidget(self.rightSplitter)
            self.mainSplitter.setStretchFactor(0,3)
            self.mainSplitter.setStretchFactor(1,4)
        else:
            # CH Layout
            self.navArea = NavArea(self.language_mode, self)
            self.buttonArea = ButtonArea(self)
            self.linkButtons = LinkButtons(self.language_mode, self)

            self.rightSplitter = QSplitter(Qt.Vertical)
            self.rightSplitter.addWidget(self.navArea)
            self.rightSplitter.addWidget(self.sourceText)
            self.rightSplitter.addWidget(self.targetText)
            self.rightSplitter.addWidget(self.buttonArea)
            self.rightSplitter.addWidget(self.bottomTable)
            self.rightSplitter.setStretchFactor(0,1)
            self.rightSplitter.setStretchFactor(1,3)
            self.rightSplitter.setStretchFactor(2,3)
            self.rightSplitter.setStretchFactor(3,1)
            self.rightSplitter.setStretchFactor(4,4)

            self.leftSplitter = QSplitter(Qt.Vertical)
            self.leftSplitter.addWidget(self.view)
            self.leftSplitter.addWidget(self.linkButtons)

            self.mainSplitter = QSplitter(Qt.Horizontal)
            self.mainSplitter.addWidget(self.leftSplitter)
            self.mainSplitter.addWidget(self.rightSplitter)
            self.mainSplitter.setStretchFactor(0,3)
            self.mainSplitter.setStretchFactor(1,5)
        ######## Language Specific ########

        # Menu
        menuBar = self.menuBar()
        file = self.menuBar().addMenu("&File")
        edit = self.menuBar().addMenu("&Edit")
        actions = self.menuBar().addMenu("&Actions")
        help = self.menuBar().addMenu("&Help")

        saveAction = QAction("Save", self)
        saveAction.setShortcut(QKeySequence.Save)
        saveAction.setToolTip("Save the current alignment file")
        self.connect(saveAction, SIGNAL("triggered()"), self.data.save)
        file.addAction(saveAction)

        quitAction = QAction("Exit", self)
        self.connect(quitAction, SIGNAL("triggered()"), self, SLOT("close()"))
        file.addAction(quitAction)
        
        editRejectAction = QAction("(Un)Reject Sentence", self)
        self.connect(editRejectAction, SIGNAL("triggered()"), self.rejectSentence)
        edit.addAction(editRejectAction)

        editQualityControl = QAction("Quality Control", self)
        self.connect(editQualityControl, SIGNAL("triggered()"), self.doQC)
        edit.addAction(editQualityControl)

        # Actions menu
        refreshAction = QAction("Refresh", self)
        self.connect(refreshAction, SIGNAL("triggered()"), self.refresh)
        actions.addAction(refreshAction)

        undoAction = QAction("Undo", self)
        self.connect(undoAction, SIGNAL("triggered()"), self.undo)
        actions.addAction(undoAction)

        clearAction = QAction("Clear", self)
        self.connect(clearAction, SIGNAL("triggered()"), self.clear)
        actions.addAction(clearAction)

        # Help menu
        helpAction = QAction("Help", self)
        self.connect(helpAction, SIGNAL("triggered()"), self.help)
        help.addAction(helpAction)

        aboutAction = QAction("About", self)
        self.connect(aboutAction, SIGNAL("triggered()"), self.about)
        help.addAction(aboutAction)


        # Status Bar
        self.sizeLabel = QLabel()
        self.sizeLabel.setFrameStyle(QFrame.StyledPanel|QFrame.Sunken)
        self.status = self.statusBar()
        self.status.setSizeGripEnabled(False)
        self.status.addPermanentWidget(self.sizeLabel)
        self.status.showMessage("Ready", 5000)

	self.setCentralWidget(self.mainSplitter)
	self.updateAll()  # draw boxes, text, and links for given sentence

        # emish: Highlight Alignment must proceed after updateAll()
        if highlightAlignment:
            try:
                self.highlight(highlightAlignment[1], highlightAlignment[0])
                self.selectAppropriateBoxes()
                self.doCenterOn()
            except AttributeError:
                print "Word ", highlightAlignment, " is not an alignment"



    def paintSentences(self):# upper right side of screen for navigation
                             # currently only called upon program startup
                             # hence coloring unchanged unless program restarted

        leftBrace = re.compile("{")
        subs = u"\u0625"

	self.sourceText.setRowCount(len(self.data.source))
	self.targetText.setRowCount(len(self.data.target))
	self.sourceText.setColumnCount(1)
	self.targetText.setColumnCount(1)
	self.sourceText.setSelectionBehavior(QTableWidget.SelectRows)
	self.targetText.setSelectionBehavior(QTableWidget.SelectRows)
	self.sourceText.setSelectionMode(QTableWidget.SingleSelection)
	self.targetText.setSelectionMode(QTableWidget.SingleSelection)

	for i in range(0,len(self.data.source)):
            
            # source 
            r = unicode(QString.fromUtf8(self.data.source_sent[i]))
            line = QString(leftBrace.sub(subs, r))
            item = QTableWidgetItem(line)
            ######## Language Specific ########
            if self.language_mode in (DEFAULT, AR):
                font = QFont(source_text_font[0],source_text_size[0],source_text_bold)
            else:
                font = QFont(source_text_font[1],source_text_size[1],source_text_bold)
            ######## Language Specific ########
            item.setFont(font)
            isFullyLinked = self.isCompletelyLinked(i)
            if isFullyLinked:
                isSomewhatLinked = False
	       	item.setBackgroundColor(QColor("#99CC99").light())
            else:
                isSomewhatLinked = self.isPartiallyLinked(i)
                if isSomewhatLinked:
                    item.setBackgroundColor(QColor("#CD143C").light().light())
            item.setFlags(item.flags() ^ Qt.ItemIsSelectable)
            item.setFlags(item.flags() ^ Qt.ItemIsEditable)
            item.setFlags(item.flags() ^ Qt.ItemIsEnabled)
            self.sourceText.setItem(0,i,item)

            #target
            line = QString.fromUtf8(self.data.target_sent[i])
            item = QTableWidgetItem(line)
            font = QFont(english_text_font, english_text_size, \
                                                   english_text_bold)
            item.setFont(font)
            if isFullyLinked:
                item.setBackgroundColor(QColor("#99CC99").light())
            elif isSomewhatLinked:
		item.setBackgroundColor(QColor("#CD143C").light().light())
            item.setFlags(item.flags() ^ Qt.ItemIsEditable)
            item.setFlags(item.flags() ^ Qt.ItemIsSelectable)
            item.setFlags(item.flags() ^ Qt.ItemIsEnabled)
            self.targetText.setItem(0,i,item)

        self.sourceText.setColumnWidth(0,7*self.sourceText.size().width())
        self.targetText.setColumnWidth(0,7*self.sourceText.size().width())
        self.sourceText.resizeRowsToContents()
        self.targetText.resizeRowsToContents()
        self.sourceText.setHorizontalHeaderLabels(("",""))
        self.targetText.setHorizontalHeaderLabels(("",""))



    def closeEvent(self,event):
	text = QLabel(formatBlock('''
               Do you wish to save?
               '''))
	verifyContinue = SaveOnQuitDialog(text, self.data, self)

        # save program settings (may not be functional)
        settings = QSettings()
        settings.setValue("MainWindow/Size", QVariant(self.size()))
        settings.setValue("MainWindow/Position", QVariant(self.pos()))
        settings.setValue("MainWindow/State", QVariant(self.saveState()))

	if verifyContinue.exec_():
            print "Exiting."
        else:
            print "Exit cancelled."
            event.ignore()

    def mousePressEvent(self,event):
        if event.button() == Qt.LeftButton:
            self.clearSelections()

    def deleteLink(self):        # deletes the link of current table row
        # rewrite this as:
        #  
        # delete lines
        # delete link from align, links self.data structures
        # recolor boxes
        # do not delete tags
        # remove link from table

        # get indices for source and target tokens
 	rowNum = self.bottomTable.currentRow()
	sourceTokens = self.bottomTable.item(rowNum, 1).text()
	sourceList = str(sourceTokens).rstrip(" ").split(" ") 
	targetTokens = self.bottomTable.item(rowNum, 3).text()
        targetList = str(targetTokens).rstrip(" ").split(" ")
        for i in range(0, len(sourceList)):
            sourceList[i] = int(sourceList[i])
        for j in range(0, len(targetList)):
            targetList[j] = int(targetList[j])

        # delete link from align, links self.data structures
        del self.data.links[self.sent,tuple(sourceList),tuple(targetList)]

        for i in sourceList:
            if i != 0:
                tag = self.data.sourceTags[self.sent,i]
                if tag == "COO" or tag == "CON" or tag == "INC":
                    self.sourceBoxList[i].changeTag("")
                self.changeBoxColor(i, "s")
            for j in targetList:
                #if i == 0:
                #    self.targetBoxList[j].changeTag("")
                #elif j == 0:
                #    self.sourceBoxList[i].changeTag("")
                del self.data.align[self.sent,i,j]
                self.removeLinkLines(i,j)
        
        for j in targetList:
            if j != 0:
                tag = self.data.targetTags[self.sent,j]
                if tag == "COO" or tag == "CON" or tag == "INC":
                    self.targetBoxList[j].changeTag("")
                self.changeBoxColor(j, "t")

        # remove row of table
	self.bottomTable.removeRow(self.bottomTable.currentRow())
	self.bottomTable.clearSelection()

   	self.clearSelections()
        self.status.showMessage("Link deleted/updated...", 5000)

    def changeFont(self):
        dialog = ChangeFont(self)
        dialog.resize(form.sizeHint())
        dialog.show()
        dialog.exec_()        


    def removeLinkLines(self, i, j):
        # remove line from scene
        if (i != 0 and j != 0):
            line = self.lines[i,j]
            self.scene.removeItem(line)            
            del self.lines[i,j]


    def changeBoxColor(self, i, type):
        # update box color -- this logic method was originally for when 
        # words are allowed to have multiple links

        # set box to not linked and update

        if type == "s" and i != 0:
            self.sourceBoxList[i].isLinked = False
            self.sourceBoxList[i].update()
        elif type == "t" and i != 0:
            self.targetBoxList[i].isLinked = False
            self.targetBoxList[i].update()

    def correct(self):
        ######## Language Specific ########
        if self.language_mode in (DEFAULT, AR):
            link_type = "COR"
            if not self.atLeastOneSourceAndTarget():
                self.notTranslatedArabic(link_type)
            else:
                self.createLink(link_type)               
        else:
            # collect info about selected boxes to pass to determineLinkType
            preventLink = False
            numChinese=0
            s_tags=[]
            t_tags=[]
            for i in range(1,len(self.sourceBoxList)):
               if self.sourceBoxList[i].selected:
                   numChinese += 1
                   tag = self.data.sourceTags[self.sent,i]
                   if tag != '': 
                       s_tags.append(tag)
                   if tag == "CON" or tag == "INC" or tag == "COO":
                       preventLink = True
            for i in range(1,len(self.targetBoxList)):
               if self.targetBoxList[i].selected:
                   tag = self.data.targetTags[self.sent,i]
                   if tag != '':
                       t_tags.append(self.data.targetTags[self.sent,i])
                   if tag == "CON" or tag == "INC" or tag == "COO":
                       preventLink = True
            if preventLink:
                text = QLabel(formatBlock('''
                Error: You may not link words to another word that has
                already been marked as Not Translated (COO, CON, INC).
                First delete the tag for this word or give it another
                kind of tag.  Thanks!
                '''))
                warnUser = WarningDialog(text,self)
                warnUser.exec_()
            else:
                link_type = self.determineLinkTypeCH(s_tags,t_tags,numChinese)
                self.createLink(link_type)
        ######## Language Specific ########

    def determineLinkTypeCH(self, s_tags, t_tags, num):
        # s_tags, t_tags are lists
        # gather list of tags
        # check how many Chinese words linked

        tags = s_tags + t_tags
        numChinese = num  # number of linked chinese words, not number of tagged

        # eliminate duplicate tags
        d = {}
        for x in tags:
            if x != "":
                d[x] = x
        tags = d.values()
        
        link_type = "SEM"  # default

        if "LOC" in tags:
            link_type = "COI"
        elif "INC" in tags:
            link_type = "INC"
        elif len(tags) == 0:
            link_type = "SEM"
        elif "DEP" in tags:
            link_type = "PDE"
        elif "DEC" in tags:
            link_type = "CDE"
        elif "DEM" in tags:
            if numChinese == 1:
                link_type = "MDE"
            elif len(tags) == 1:
                link_type = "GIS"
            elif "FUN" in tags:
                link_type = "GIF"
            else:
                link_type = "GIS"
        elif "FUN" in tags and len(tags) == 1:
            link_type = "FUN"
        elif not "FUN" in tags and not "LOC" in tags and len(tags) >= 1:
            link_type = "GIS"
        elif "FUN" in tags and len(tags) >= 2:
            link_type = "GIF"
  
        return link_type

    def incorrect(self):
	self.createLink("INC")

    def notTranslatedChinese(self, index, side):          # correct
        # only one box marked at a time
        # side = "s" or "t"
        
        index = int(index)

        if side == "s":
            self.sourceBoxList[index].isLinked = True
            self.sourceBoxList[index].linkType = "NT"
            self.sourceBoxList[index].notTranslated = True
            self.sourceBoxList[index].update()
            self.data.align[self.sent,index,0] = "NT"
            self.data.links[self.sent,tuple([index]),tuple([0])] = "NT"
            self.pushLinkTable([index],[0], "NT")
        elif side == "t":
            self.targetBoxList[index].isLinked = True
            self.targetBoxList[index].linkType = "NT"
            self.targetBoxList[index].notTranslated = True
            self.targetBoxList[index].update()
            self.data.align[self.sent,0,index] = "NT"
            self.data.links[self.sent, tuple([0]), tuple([index])] = "NT"
            self.pushLinkTable([0],[index], "NT")

	self.clearSelections()

    def notTranslatedArabic(self, link_type = "COR"):
        # default link type is "COR", unless otherwise specified
        doNotDoIt = False

        for i in range(1, len(self.sourceBoxList)):
            if self.sourceBoxList[i].selected == True and \
               self.sourceBoxList[i].isLinked == True:
                doNotDoIt = True
        for i in range(1, len(self.targetBoxList)):
            if self.targetBoxList[i].selected == True and \
               self.targetBoxList[i].isLinked == True:
                doNotDoIt = True
        if doNotDoIt:
                text = QLabel(formatBlock('''
                Oops: You cannot mark words as Not Translated
                if they are already linked to other words!
                Please delete the existing link before proceeding.
                '''))
                warnUser = WarningDialog(text)
                warnUser.exec_()                
        else:
            for i in range(1, len(self.sourceBoxList)):
                if self.sourceBoxList[i].selected == True:
                    self.sourceBoxList[i].isLinked = True
                    self.sourceBoxList[i].linkType = link_type
                    self.sourceBoxList[i].notTranslated = True
                    self.sourceBoxList[i].selected = False
                    self.sourceBoxList[i].update()
                    self.data.align[self.sent,i,0] = link_type
                    self.data.links[self.sent,tuple([i]),tuple([0])] = link_type
                    self.pushLinkTable([i],[0],link_type)
            for j in range(1, len(self.targetBoxList)):
                if self.targetBoxList[j].selected == True:
                    self.targetBoxList[j].isLinked = True
                    self.targetBoxList[j].linkType = link_type
                    self.targetBoxList[j].notTranslated = True
                    self.targetBoxList[j].selected = False
                    self.targetBoxList[j].update()
                    self.data.align[self.sent,0,j] = link_type
                    self.data.links[self.sent,tuple([0]),tuple([j])] = link_type
                    self.pushLinkTable([0],[j],link_type)

    def notTranslatedIncorrectArabic(self): 
        self.notTranslatedArabic("INC")

    def getLink(self, i, tok_type):
        for (sentence, i_tuple, j_tuple) in self.data.links.keys():
          if sentence == self.sent:
              i_list = list(i_tuple)
              j_list = list(j_tuple)

              if tok_type == "s":
                if i in i_list:
                    link_type = self.data.links[self.sent,i_tuple,j_tuple]
                    return (list(i_tuple),list(j_tuple),link_type)
              elif tok_type == "t":
                if i in j_list:
                    link_type = self.data.links[self.sent,i_tuple,j_tuple]
                    return (list(i_tuple),list(j_tuple),link_type)

    def getLinkRow(self, i, type):   # for current token, type
        for row in range(0, self.bottomTable.rowCount()):
            item1 = self.bottomTable.item(row, 1)
            item2 = self.bottomTable.item(row, 3)
            s_tokens = str(item1.text()).rstrip().split(" ")
            t_tokens = str(item2.text()).rstrip().split(" ")

            if type == "s":
                for s in s_tokens:
                  if i == int(s):
                      return row
            elif type == "t":
                for t in t_tokens:
                  if i == int(t): 
                      return row
        return -1  ## error

    def deleteWordFromLink(self, i, type):
        sent=self.sent
        r = -1        # row

        # If this is the last word on one side, then delete the whole link.

        doIt = False       
        if type == "s" and self.sourceBoxList[i].isLinked:
            doIt=True
        elif type == "t" and self.targetBoxList[i].isLinked:
            doIt=True
        if doIt:
            (s_list,t_list,link_type) = self.getLink(i, type)

            # delete the link
            r = self.getLinkRow(i, type)
            self.bottomTable.selectRow(r)
#            item = self.bottomTable.item(r,5)
#            linkType = item.text()
            self.deleteLink()

            # now create the link with remaining tokens
            if type == "s":
                s_list.remove(i)
            elif type == "t":
                t_list.remove(i)
                
            ######## Language Specific ########
            if self.language_mode in (DEFAULT, AR):
                if not s_list == [] and not t_list == []:
                    for s in s_list:
                        self.sourceBoxList[s].selected = True
                    for t in t_list:
                        self.targetBoxList[t].selected = True
                    if link_type == "COR":
                        self.correct()
                    else:
                        self.incorrect()
            else:
                if not s_list == [] and not t_list == []:
                    for s in s_list:
                        self.sourceBoxList[s].selected = True
                    for t in t_list:
                        self.targetBoxList[t].selected = True
                    self.correct()
                
                # return focus to next row (which now has old row number)
                if self.bottomTable.rowCount() > 0:
                    self.bottomTable.selectRow(r)
                    self.selectAppropriateBoxes()
            ######## Language Specific ########

        else:
            print "Cannot delete: not a member of a link"

    def highlight(self, i, type):
        # called from box with self.parent.highlight(self.index, self.type)
        # must highlight appropriate line in link table

        self.bottomTable.clearSelection()      

        row = self.getLinkRow(i, type)
        self.bottomTable.selectRow(row)
        item = self.bottomTable.item(row,0)
        self.bottomTable.scrollToItem(item)

    def selectAppropriateBoxes(self):

   	tableRow = self.bottomTable.currentRow()
        self.clearSelections()
  
        item1 = self.bottomTable.item(tableRow, 1)
        item2 = self.bottomTable.item(tableRow, 3)
        s_tokens = str(item1.text()).rstrip().split(" ")
        t_tokens = str(item2.text()).rstrip().split(" ")

	# print 's,t tokens:', s_tokens, t_tokens

        for s in s_tokens:
           if int(s) != 0:  
              self.sourceBoxList[int(s)].selected = True
              self.sourceBoxList[int(s)].update()
        for t in t_tokens:
           if int(t) != 0:
              self.targetBoxList[int(t)].selected = True
              self.targetBoxList[int(t)].update()
        
    def doCenterOn(self):
        # adjust view so newly highlighted boxes are viewable
        # typically called after SelectAppropriateBoxes
        
        tableRow = self.bottomTable.currentRow()

        item1 = self.bottomTable.item(tableRow, 1)
        item2 = self.bottomTable.item(tableRow, 3)
        s_tokens = str(item1.text()).rstrip().split(" ")
        t_tokens = str(item2.text()).rstrip().split(" ")        
        s = s_tokens[0]
        t = t_tokens[0]

        if int(s) == 0:
            box = self.targetBoxList[int(t)]
        else:
            box = self.sourceBoxList[int(s)]
        self.view.centerOn(box.pos())

    def isCompletelyLinked(self, sen):
        # test if all words in both source and target have link assigned
        if self.data.status[sen] == "rejected":
            return True
        for i in range(1, len(self.data.source[sen])):
            linkExists = False
            for j in range(0, len(self.data.target[sen])):
                if (sen,i,j) in self.data.align:
                    linkExists = True
                    break
            if linkExists is False:
                return False
        for j in range(1, len(self.data.target[sen])):
            linkExists = False
            for i in range(0, len(self.data.source[sen])):
                if (sen,i,j) in self.data.align:
                    linkExists = True
                    break
	    if linkExists is False:
		return False
	return True  
    
    def isPartiallyLinked(self, sen):    # at least one link in sentence?

        for i in range(1, len(self.data.source[sen])):
            for j in range(1, len(self.data.target[sen])):
                if (sen,i,j) in self.data.align:
                    return True
	return False

    def hasNoLinks(self, sen):
        # test if no words in source and target have link assigned
        #for i in range(1, len(source[sen])):
        print ("Testing hasNoLinks -- not currently implemented")    

    def pushLinkTable(self, s_token_num, t_token_num, link_type):

        # for sorting table contents, setSortingEnabled must be switched
        # off when populating the table. Afterwards it is set back on!?
         
        self.bottomTable.setSortingEnabled(False)         

        row = self.bottomTable.rowCount()
	self.bottomTable.insertRow(row)

	#source token(s) - column 0
	my_string = ""
	for i in range(0, len(s_token_num)):
            my_string = my_string + \
                   QString.fromUtf8(self.data.source[self.sent][s_token_num[i]]+" ")
        item = QTableWidgetItem(my_string)
#       item.setTextAlignment(Qt.AlignCenter )
	item.setFlags(item.flags() ^ Qt.ItemIsEditable)
	self.bottomTable.setItem(row, 0, item)   

	#source token number(s) - column 1
	my_string = ""
	for i in range(0, len(s_token_num)):
		my_string = my_string + str(s_token_num[i])+" "
	item = CustomQTableWidgetItem(my_string)
	item.setFlags(item.flags() ^ Qt.ItemIsEditable)
        size = QSize(30,100)
        item.setSizeHint(size)
#       item.setTextAlignment(Qt.AlignCenter)
	self.bottomTable.setItem(row, 1, item)   
 
	#target token(s) - column 2
	my_string = ""
	for i in range(0, len(t_token_num)):
		my_string = my_string + self.data.target[self.sent][t_token_num[i]]\
                            + " "
	item = QTableWidgetItem(my_string)
	item.setFlags(item.flags() ^ Qt.ItemIsEditable)
#       item.setTextAlignment(Qt.AlignCenter)
	self.bottomTable.setItem(row, 2, item)   

	#target token numbers(s) - column 3
	my_string = ""
	for i in range(0, len(t_token_num)):
		my_string = my_string + str(t_token_num[i]) + " "
	item = CustomQTableWidgetItem(my_string)
	item.setFlags(item.flags() ^ Qt.ItemIsEditable)
#       item.setTextAlignment(Qt.AlignCenter)
	self.bottomTable.setItem(row, 3, item)   

	#sentence number - column 4
	item = QTableWidgetItem(str(self.sent+1))
	item.setFlags(item.flags() ^ Qt.ItemIsEditable)
#       item.setTextAlignment(Qt.AlignCenter)
	self.bottomTable.setItem(row, 4, item)   

	#link type - column 5
	item = QTableWidgetItem(link_type)
	item.setFlags(item.flags() ^ Qt.ItemIsEditable)
#       item.setTextAlignment(Qt.AlignCenter)
	self.bottomTable.setItem(row, 5, item)   

	self.bottomTable.resizeColumnsToContents()

        self.bottomTable.setSortingEnabled(True)         

    def help(self):
        self.text_dialog = QDialog()
        text_dialog = self.text_dialog
        text_dialog.setModal(False)
        text_box = QPlainTextEdit()
        
        readme_filename = os.path.dirname(__file__)
        if os.name == 'nt':
            readme_filename += '\\README.txt'
        else:
            readme_filename += '/README.txt'
        try:
            readme_file = open(readme_filename, 'r')
        except:
            print "Cannot open readme file."
            QMessageBox.warning(None, "Error", "Cannot open readme file.")
            
        text = readme_file.read()
        text_box.setPlainText(text)
        layout = QHBoxLayout()
        layout.addWidget(text_box)
        text_dialog.setLayout(layout)
        text_dialog.setFixedSize(600, 500)
        text_dialog.show()
            
    def about(self):
        QMessageBox.information(None, "About",
        "LDC Word Aligner v" + version + "\n" + \
        """Linguistic Data Consortium
        Developed by Stephen Grimes
        Enhancements and bug fixes by
        Mishal Awadah and John Mayer
        Contact: sgrimes@ldc.upenn.edu""")

    def undo(self):
	if self.bottomTable.rowCount() == 0:
            text = QLabel(formatBlock('''
            Error: There is nothing to Undo        
            '''))
            warnUser = WarningDialog(text,self)
            warnUser.exec_()	
        else:
            row = self.bottomTable.rowCount()-1
            self.bottomTable.selectRow(row)
            self.deleteLink()
        self.clearSelections()

    def doQC(self):
        dialog = QualityControl(self.data, self.language_mode, self)
#       dialog = QDialog()
        dialog.resize(self.sizeHint())
        dialog.show()
#        dialog.exec_()

    def addText(self, x, y, text, i, type):
        point = QPointF(x,y)
        name = TextItem(self, text, point, self.scene, i, type, self.language_mode)
	return name

    def addBox(self, x, y, sent, i, type):
        point = QPointF(x, y)
        name = BoxItem(self, point, self.scene, sent, i, type,
                       self.view, self.data, self.language_mode)
	return name

    def rejectSentence(self):
        if self.sent in self.data.status.keys() and \
          self.data.status[self.sent] == "rejected":
            self.data.status[self.sent] = ""
        else:
            if self.clear():
                self.data.status[self.sent] = "rejected"

        self.updateAll()

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Space or event.key() == Qt.Key_C:
            self.correct()
	elif event.key() == Qt.Key_I:
            self.incorrect()
        ######## Language Specific ########
	elif event.key() == Qt.Key_O and self.language_mode in (DEFAULT, AR):
            self.notTranslatedArabic()
	elif event.key() == Qt.Key_T and self.language_mode in (DEFAULT, AR):
            self.notTranslatedIncorrectArabic()
        ######## Language Specific ########
	elif event.key() == Qt.Key_U:
            self.undo()
	elif event.key() == Qt.Key_N:
            self.nextSentence()
	elif event.key() == Qt.Key_P:
            self.previousSentence()
        elif event.key() == Qt.Key_Delete or event.key() == Qt.Key_D:
            self.deleteLink()


    def clear(self):        # remove all tags and links for a sentence
	text = QLabel(formatBlock('''
               Oops: Are you sure you want to 
               remove all annotation for this 
               sentence?
               '''))
	verifyContinue = DumbDialog(text,self)
	if verifyContinue.exec_():
            for (s,i,j) in self.data.align.keys():
                if s == self.sent:
                    del self.data.align[s,i,j]
            for (s,i,j) in self.data.links.keys():
                if s == self.sent:
                    del self.data.links[s,i,j]
            for (s,i) in self.data.sourceTags.keys():
                if s == self.sent:
                    self.data.sourceTags[s,i] = ""
            for (s,j) in self.data.targetTags.keys():
                if s == self.sent:
                    self.data.targetTags[s,j] = ""
            self.refresh()
            return True
        else:
            return False

    def clearSelections(self):
        for i in range(1,len(self.sourceBoxList)):
            self.sourceBoxList[i].selected = False
            self.sourceBoxList[i].update()
        for j in range(1,len(self.targetBoxList)):
            self.targetBoxList[j].selected = False 
            self.targetBoxList[j].update()
   
    def atLeastOneSourceAndTarget(self): 
	# check at least one word from each table is selected
	count1 = 0
	for i in range(1,len(self.sourceBoxList)):
	    if self.sourceBoxList[i].selected:
		     count1 += 1
	count2 = 0
	for i in range(1,len(self.targetBoxList)):
            if self.targetBoxList[i].selected:
		     count2 += 1

        if count1 == 0 or count2 == 0:
            ######## Language Specific ########
            if self.language_mode == CH:
                text = QLabel(formatBlock('''
                Error: You must align at least        
                one word from each of the             
                source and target tables.         
                '''))
                warnUser = WarningDialog(text,self)
                warnUser.exec_()
            ######## Language Specific ########
            return False
        else:
            return True

    def fontSelect(self):
        #if self.textFont:
        #    (font, ok) = QFontDialog.getFont(self.textFont)
        #else: 
        (font, ok) = QFontDialog.getFont()

        if not font:
            return

        # set font here    

    def wordAlreadyLinked(self):
        sent = self.sent

        alreadyLinked = False
        # if one word already linked
        for i in range(1, len(self.data.source[sent])):
              if self.sourceBoxList[i].selected:
                   if self.sourceBoxList[i].isLinked:
                       alreadyLinked = True
        for i in range(1, len(self.data.target[sent])):            
              if self.targetBoxList[i].selected:
                   if self.targetBoxList[i].isLinked:
                       alreadyLinked = True
        if alreadyLinked:
            return True
        else:
            return False

    def deleteLinkButLeaveCurrentSelections(self):
        # We are adding a word to an existing link.
        # plan:
        # record current selected boxes and their tags
        # delete link
        # restore box selections and their tags
        # allow new link to be created

        sent=self.sent
        i_list = []
        j_list = []

        # record boxes that are currently selected
        for i in range(1, len(self.data.source[sent])):
            if self.sourceBoxList[i].selected:
                i_list.append(i)
#                i_list_tags.append(self.data.sourceTags[sent,i])
        for j in range(1, len(self.data.target[sent])):
            if self.targetBoxList[j].selected:
                j_list.append(j)
#                j_list_tags.append(self.data.targetTags[sent,j])


        # delete all links involving words that had been selected
        for s in range(0,len(i_list)):
            rowNum = self.getLinkRow(i_list[s], "s")
            if rowNum != -1:
                self.bottomTable.selectRow(rowNum)
                self.deleteLink()
        for t in range(0,len(j_list)):
            rowNum = self.getLinkRow(j_list[t], "t")
            if rowNum != -1:
                self.bottomTable.selectRow(rowNum)
                self.deleteLink()

        # reselect boxes that were originally selected
        for s in range(0,len(i_list)):
            i = i_list[s]
            self.sourceBoxList[i].selected = True
        for t in range(0,len(j_list)):
            i = j_list[t]
            self.targetBoxList[i].selected = True
        return 1

    def createLink(self, link_type):
        sent = self.sent
        mayCreateLink = True
        tableRowToHighlight = None

        if not self.atLeastOneSourceAndTarget():
            mayCreateLink = False

        elif self.wordAlreadyLinked():
            tableRowToHighlight = self.deleteLinkButLeaveCurrentSelections()
                
        i_list = []
        j_list = []

        if mayCreateLink is True:
            for i in range(1,len(self.data.source[sent])):
      		for j in range(1,len(self.data.target[sent])):
		   if (self.sourceBoxList[i].selected and 
                       self.targetBoxList[j].selected):
 
                      self.data.align[sent,i,j] = link_type
                      self.sourceBoxList[i].isLinked = True
                      self.sourceBoxList[i].linkType = link_type
                      self.sourceBoxList[i].update()
                      self.sourceBoxList[i].notTranslated = False
                      self.targetBoxList[j].isLinked = True
                      self.targetBoxList[j].linkType = link_type
                      self.targetBoxList[j].update()
                      self.targetBoxList[j].notTranslated = False

                      #add lines
                      if i not in i_list:
			   i_list.append(i)
                      if j not in j_list:
                           j_list.append(j)
                      if not (i, j) in self.lines:    
			   self.lines[i, j] = self.addLine(i,j,link_type) 

            self.pushLinkTable(i_list,j_list,link_type)
            self.data.links[sent,tuple(i_list),tuple(j_list)] = link_type

        self.clearSelections()   # clear all selected boxes

        ######## Language Specific ########
        if self.language_mode == CH:
            # if word was added to link, select previous next word
            # for Chinese only
        
            if tableRowToHighlight:
                print i_list,"and",j_list
                i = i_list[0]
                j = j_list[0]
                if i != 0:
                    row = self.getLinkRow(i,"s")
                else:
                    row = self.getLinkRow(j,"t")
                self.bottomTable.selectRow(row)
                item = self.bottomTable.item(row,0)
                self.bottomTable.scrollToItem(item)
                self.selectAppropriateBoxes()
                # self.doCenterOn()
        ######## Language Specific ########

    def determineColor(self,l):
        color = QColor("#BEBEBE")
        ######## Language Specific ########
        if self.language_mode in (DEFAULT, AR):
            if l == "INC":
                color = QColor("#FFCC33")         # orange
            elif l == "COR":
                color = QColor("#99CC99")         # darker green
            elif l == "NT":
                color = QColor("#AFEEEE")         # light blue
            else:
                color = QColor("#BEBEBE")         # grey
        else:
            # Chinese
            if l == "SEM" or l == "FUN" or l == "PDE" or l == "CDE" or \
                   l == "MDE" or l == "DEP" or l == "DEC" or l == "DEM":
                color = QColor("#CCCCFF")
            elif l == "GIF" or l == "GIS" or l == "COI":
                color = QColor(Qt.green).light()
            elif l == "INC":
                color = QColor(Qt.red).light()
            elif l == "NT":
                color = QColor("#FF9900")
            else:
                color = QColor("#BEBEBE")
        ######## Language Specific ########
        return color

    def addLine(self, i, j, link_type):
        if (i, j) in self.lines:
            print "already exists!!!!"
        else:
            x1 = self.sourceBoxList[i].pos().x()+160
            y1 = self.sourceBoxList[i].pos().y()+15
            x2 = self.targetBoxList[j].pos().x()
            y2 = self.targetBoxList[j].pos().y()+15
            color = self.determineColor(link_type)
            pen = QPen()
            pen.setColor(color)
            line = QGraphicsLineItem(QLineF(x1,y1,x2,y2))
            line.setPen(pen)
            self.scene.addItem(line)
            return line

    def updateAll(self):
        # load a sentence from self.data structure and repaint screen:
        # draw new boxes, words, links, table
	sent = self.sent

        # make new scene
        self.scene = QGraphicsScene(self)
        self.view.setScene(self.scene)
#        self.view.setFocusPolicy(Qt.NoFocus)
        
        # use length of longer sentence	to set scene length    
        my_align_length = \
            (max(len(self.data.source[sent]), len(self.data.target[sent]))+1)*box_size
        rect = QApplication.desktop().availableGeometry()
        my_align_length = max(my_align_length, int(rect.height())) 
        self.scene.setSceneRect(0, 0, 500, my_align_length)
       
        # create boxes, tokens, and tags
        self.lines = {}
	self.sourceBoxList = []
	self.sourceTextList= []
        self.sourceTagList = []
	self.targetBoxList = []
	self.targetTextList= []
        self.targetTagList = []

	self.sourceBoxList.append("dummy") # token 0 is not displayed and is
	self.sourceTextList.append("dummy")# used for aligning <not translated> 
        self.sourceTagList.append("dummy")
        for i in range(1,len(self.data.source[sent])):
#           print "Sent",sent,"is",len(self.data.source[sent]),"long."
	   y_height = i * box_size - .5 * box_size
	   text = QString.fromUtf8(self.data.source[sent][i])
#           print i," ",self.data.source[sent][i]
	   self.sourceBoxList.append(self.addBox(sbox,y_height,sent,i,"s"))
           self.sourceTextList.append(self.addText(stext,y_height,text,i,"s"))
           tag = self.data.sourceTags[sent,i]
           self.sourceTagList.append(self.addText(stag,y_height,tag,i,"s"))

           # draw line
           line = QGraphicsLineItem(QLineF(sbox,y_height,sbox+160,y_height))
           line.setZValue(10)
           self.scene.addItem(line)           
        
        # draw bottom line and side lines
   	if len(self.data.source[sent]) > 1:
            y = y_height + box_size
            line = QGraphicsLineItem(QLineF(sbox,y,sbox+160,y))
            self.scene.addItem(line)           
                                   
	self.targetBoxList.append("dummy")
	self.targetTextList.append("dummy")
        self.targetTagList.append("dummy")
	for i in range(1,len(self.data.target[sent])):
	   y_height = i * box_size - .5 * box_size
           text = QString.fromUtf8(self.data.target[sent][i])
           self.targetBoxList.append(self.addBox(tbox,y_height,sent,i,"t"))
           self.targetTextList.append(self.addText(ttext,y_height,text,i,"t"))
           tag = self.data.targetTags[sent,i]
           self.targetTagList.append(self.addText(ttag,y_height,tag,i,"t"))
                                   
           # draw lines
           line = QGraphicsLineItem(QLineF(tbox,y_height,tbox+160,y_height))
           line.setZValue(10)
           self.scene.addItem(line)           

        # draw bottom line and side lines
 	if len(self.data.target[sent]) > 1:
            y = y_height + box_size
            line = QGraphicsLineItem(QLineF(tbox,y,tbox+160,y))
            self.scene.addItem(line)                          

        self.redrawTable()    # also draws links between boxes

        # set focus in source and translation tables
        item = self.sourceText.item(sent,0)
        self.sourceText.scrollToItem(item)
        self.sourceText.selectRow(sent)
        item = self.targetText.item(sent,0)
        self.targetText.scrollToItem(item)
        self.targetText.selectRow(sent)

        # if sentence market as rejected, do other things
        if sent in self.data.status.keys() and self.data.status[sent] == "rejected":
            self.scene = QGraphicsScene(self)
            self.view.setScene(self.scene)
#            self.view.setFocusPolicy(Qt.NoFocus)
            text1 = "Sentence marked as rejected"
            text2 = "No annotations recorded"
            text3 = "To restore, under Edit menu"
            text4 = " select (Un)reject sentence."
            self.addText(100,100,text1,1,"s")
            self.addText(100,140,text2,1,"s")
            self.addText(100,180,text3,1,"s")
            self.addText(100,220,text4,1,"s")

        ######## Language Specific ########
        if self.language_mode in (DEFAULT, AR):
            # reset comment area
            if sent in self.data.comment.keys():
                text = self.data.comment[sent]
            else:
                text = ""
            self.commentField.setText(text)
        ######## Language Specific ########

        # enable the appropriate sentence in source, target texts
        item = self.sourceText.item(sent,0)
        item.setFlags(item.flags() | Qt.ItemIsEnabled)
        item = self.targetText.item(sent,0)
        item.setFlags(item.flags() | Qt.ItemIsEnabled)
        
        # display sentence number above Source table
        myStr = "Current Sentence: "+str(self.sent+1)
        self.sourceText.setHorizontalHeaderLabels((myStr,""))

    def removeBox(self, box):        # associated with DoubleClicking
                                     # for Arabic?

        # remove all links associated with a given box
        if box is self.sourceBoxList[box.index]:
           for x,y,z in self.data.links.keys():
               if x == self.sent and box.index in y:
                   # delete record of link
                   for i in y:
                       for j in z:
                           del self.data.align[x,i,j]
                           self.removeLinkLines(i,j)

                           # change box color
                           self.changeBoxColor(i, "s")
                           self.changeBoxColor(j, "t")
                   del self.data.links[x,y,z]

        elif box is self.targetBoxList[box.index]:
            for x,y,z in self.data.align.keys():
               if x == self.sent and box.index in z:
                   # delete record of link
                   for i in y:
                       for j in z:
                           del self.data.align[x,i,j]
                           self.removeLinkLines(i,j)

                           # change box color
                           self.changeBoxColor(i, "s")
                           self.changeBoxColor(j, "t")
                   del self.data.links[x,y,z]

        self.clearSelections()      # clear all selected boxes

    def refresh(self):
        self.goToSentence(self.sent)

    def nextSentence(self):
        self.goToSentence(self.sent + 1)

    def previousSentence(self):
        self.goToSentence(self.sent - 1)

    def jumpSentence(self, num):
        self.goToSentence(num-1)

    def goToSentence(self, newSentNum):    # leap to arbitrary sentence number

        # check to make sure requested sentence number is valid
        if newSentNum >= len(self.data.source):
            text = QLabel(formatBlock('''
            Oops: You cannot progress to a
            sentence beyond the last!
            '''))
            warnUser = WarningDialog(text)
            warnUser.exec_()

        elif newSentNum < 0:
            text = QLabel(formatBlock('''
            Oops: You cannot go to a sentence before
               the first sentence!   
            '''))
            warnUser = WarningDialog(text,self)
            warnUser.exec_()

        else: 
            # set current source, target text items to not enabled
            # also change background color to red, green, or white
            item = self.sourceText.item(self.sent,0)
            item.setFlags(item.flags() ^ Qt.ItemIsEnabled)           
            isFullyLinked = self.isCompletelyLinked(self.sent)
            if isFullyLinked:
                isSomewhatLinked = False
                item.setBackgroundColor(QColor("#99CC99").light())
            else: 
                isSomewhatLinked = self.isPartiallyLinked(self.sent)
                if isSomewhatLinked:
                    item.setBackgroundColor(QColor("#CD143C").light().light())
                else:
                    item.setBackgroundColor(QColor("#FFFFFF"))
            item = self.targetText.item(self.sent,0)
            item.setFlags(item.flags() ^ Qt.ItemIsEnabled)
            if isFullyLinked:
                item.setBackgroundColor(QColor("#99CC99").light())
            elif isSomewhatLinked:
                item.setBackgroundColor(QColor("#CD143C").light().light())
            else:
                item.setBackgroundColor(QColor("#FFFFFF"))

            ######## Language Specific ########
            if self.language_mode in (DEFAULT, AR):
                # save any comment before proceeding
                self.data.comment[self.sent] = self.commentField.text()
            ######## Language Specific ########
                
            self.data.save()
            del self.scene                     #clear scene
            self.sent = newSentNum
            
            # create new scene
            self.updateAll()                   
            self.status.showMessage("File Saved...", 5000)

    def redrawTable(self):

         # for sorting table contents, setSortingEnabled must be switched
         # off when populating the table. Afterwards it is set back on!?
         
         self.bottomTable.setSortingEnabled(False) 
        
         self.lines = {}
         self.bottomTable.clear()
	 for i in range(0,self.bottomTable.rowCount()):
		 self.bottomTable.removeRow(0)
	 self.bottomTable.setHorizontalHeaderLabels(("Source Token(s)","#", \
                                    "Target Token(s)","#","Sent","Link Type"))
         keys = self.data.links.keys()
         keys.sort()
         for x,y,z in keys:
             if x == self.sent: 
                self.pushLinkTable(y,z,self.data.links[self.sent,y,z])
                for i in y:
                   for j in z:
                       if i>0 and j>0:
                           if not (i,j) in self.lines:
                               link = self.data.links[self.sent,y,z]
                               self.lines[i,j] = self.addLine(i,j,link) 
	 self.bottomTable.resizeColumnsToContents()

         self.bottomTable.setSortingEnabled(True)
