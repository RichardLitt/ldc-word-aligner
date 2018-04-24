#!/ldc/bin/python2.6
# -*- coding: utf-8 -*-
# ui_components.py

# local modules
from utils import *
import dialogs

# class declarations
class TextItem(QGraphicsTextItem):
    """Each of the words displayed on the left window pane is a TextItem."""
    def __init__(self, parent, text, position, scene, i, type, language_mode):

	## These are hacks to control display of certain characters:

        # Arabic Hamza issue (for viewing correction only)
        hamza = re.compile("{")
        subs = u"\u0625"
        text2 = unicode(text)
        w2 = hamza.sub(subs, text2)

        ######## Language Specific ########
        if language_mode == CH:
            super(TextItem, self).__init__(w2)
            self.text = w2
            if type == "s":
                font = QFont(source_box_font[1], source_box_size[1], source_box_bold)
            elif type == "t":
                font = QFont(english_box_font, english_box_size[1], english_box_bold)
        elif language_mode == AR:
            # Plus sign issue - need RTL display override...
            plus = re.compile("\+")
            sub1 = "+"
            sub2 = u"\u202e"
            subs = sub2 + sub1
            w1 = plus.sub(subs, w2)
            super(TextItem, self).__init__(w1)   # not w2
            self.text = w1
            if type == "s":
                font = QFont(source_box_font[0], source_box_size[0], source_box_bold)
            elif type == "t":
                font = QFont(english_box_font, english_box_size[0], english_box_bold)
        elif language_mode == DEFAULT:
            super(TextItem, self).__init__(w2)
            if type == 's':
                font = QFont(source_box_font[1], source_box_size[1], source_box_bold)
            elif type == 't':
                font = QFont(english_box_font, english_box_size[1], english_box_bold)
        ############### End ###############

        self.parent = parent
	self.index = i
        self.type = type

        self.setFont(font)

        self.setPos(position)
        scene.addItem(self)
	self.setZValue(10)

    def contextMenuEvent(self, event):
        """Determines what options are available on a right-click"""
        i = self.index
        if self.type == "s":
            self.parent.sourceBoxList[i].contextMenuEvent(event)
        else:
            self.parent.targetBoxList[i].contextMenuEvent(event)


class TableClass(QTableWidget):
    """Bottom right link table."""
    def __init__(self, parent):
        QTableWidget.__init__(self, parent)
        self.parent = parent

        font=QFont(link_table_font, link_table_size, link_table_bold)
        self.setFont(font)

    def mousePressEvent(self, event):
        if self.itemAt(event.pos()) != None:
            self.selectRow(self.itemAt(event.pos()).row())
            self.parent.selectAppropriateBoxes()
            self.parent.doCenterOn()

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Down:
            r = self.parent.bottomTable.currentRow()
            if r < self.parent.bottomTable.rowCount():
                self.selectRow(r+1)
                self.parent.selectAppropriateBoxes()
                self.parent.doCenterOn()
        elif event.key() == Qt.Key_Up:
            r = self.parent.bottomTable.currentRow()
            if r >= 0:
                self.selectRow(r-1)
                self.parent.selectAppropriateBoxes()
                self.parent.doCenterOn()


class TableClass2(QTableWidget):
    """Source and target sentence navigation. Top right and middle right."""
    def __init__(self, parent, type, language_mode):
        QTableWidget.__init__(self, parent)
        self.parent = parent
        self.language_mode = language_mode
        
        ######## Language Specific ########
        if language_mode in (DEFAULT, CH):
            self.setLayoutDirection(Qt.LeftToRight)
        else:
            if type == "s":
                self.setLayoutDirection(Qt.RightToLeft)
            else:
                self.setLayoutDirection(Qt.LeftToRight)
        ######## Language Specific ########


    def mousePressEvent(self, event):
        if event.button() == Qt.RightButton:
             if self.itemAt(event.pos()) != None:                
                 row = self.itemAt(event.pos()).row()
                 myText = self.item(row,0).text()
                 dialog = dialogs.PopupDialog(myText, self.language_mode, self)
                 dialog.show()
                 dialog.exec_()

    def mouseDoubleClickEvent(self, event):
        row = self.itemAt(event.pos()).row()
        self.parent.goToSentence(row)


class BoxItem(QGraphicsItem):
    """Each of the TextItem's in the left column is contained within a BoxItem.
    The BoxItem changes color to reflect various properties of the word, such as
    links. It also serves as a user interface object recieving mouse-clicks and such.
    """
    def __init__(self, parent, position, scene, sent, i, type, view, data, 
                 language_mode, style=Qt.SolidLine, rect=None, matrix=QMatrix()):
        super(BoxItem, self).__init__()
        self.parent = parent
        self.data = data
        self.language_mode = language_mode

        ########### Language Specific ##########
        if self.language_mode == AR:
            self.tags = AR_tags
        elif self.language_mode == CH:
            self.tags = CH_tags
        else:
            self._readInTags()
        ########### Language Specific ##########

        if rect is None:
             rect = QRectF(0, 0, 160, box_size)

	self.index = i
        self.rect = rect
        self.style = style
        self.setPos(position)
        self.setMatrix(matrix)
        self.notTranslated = False
        self.selected = False
        self.type = type       #  "s" or "t"
        self.sent = sent
        self.view = view
        self.scene = scene

        self.isLinked = False
	for w,x,y in self.data.align.keys():
           if type == "s":
	      if w == sent and x == i:	
	          self.isLinked = True
                  self.linkType = self.data.align[w,x,y]  # COR, INC, etc.
                  if y == 0:
                      self.notTranslated = True
           elif type == "t":
	      if w == sent and y == i:	
	          self.isLinked = True
                  self.linkType = self.data.align[w,x,y]  # COR, INC, etc.
                  if x == 0:
                      self.notTranslated = True
        scene.addItem(self)

    def _readInTags(self):
        """Load context menu tags from file."""
        
        # Default tags: <delete existing tag>
        self.tags = []
        tag_filepath = os.path.dirname(__file__)
        if os.name == 'nt':
            tag_filepath += '\\tags.txt'
        else:
            tag_filepath += '/tags.txt'
        tag_file = open(tag_filepath, 'r')
        for line in tag_file:
            if line[0] == '#':
                continue
            line_s = line.split()
            if line_s:
                self.tags.append((" ".join(line_s[:-1]), line_s[-1]))
        tag_file.close()
        self.tags.append(("<delete existing tag>", ""))

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            if self.selected:
                self.selected = False
            else:

                if event.modifiers() & Qt.ControlModifier:
                # select multiple links at once for combining using CTRL

                    # save list of currently selected links
                    sprev = [0]
                    tprev = [0]
                    for i in range(1,len(self.parent.sourceBoxList)):
                        if self.parent.sourceBoxList[i].selected:
                            sprev.append(1)
                        else:
                            sprev.append(0)
                    for j in range(1,len(self.parent.targetBoxList)):
                        if self.parent.targetBoxList[j].selected:
                            tprev.append(1)
                        else:
                            tprev.append(0)
                    
                    # do same as if CTRL was not pressed (see below)
                    if self.isLinked:
                        self.parent.highlight(self.index, self.type)
                        self.parent.selectAppropriateBoxes()
                    else:
                        self.selected = True

                    # now reinstate previous selections
                    for i in range(1,len(sprev)):
                        if sprev[i] == 1:
                            self.parent.sourceBoxList[i].selected = True
                    for i in range(1,len(tprev)):
                        if tprev[i] == 1:
                            self.parent.targetBoxList[i].selected = True

                else:                  # CTRL not pressed, normal behavior
                    if self.isLinked:
                        self.parent.highlight(self.index, self.type)
                        self.parent.selectAppropriateBoxes()
                    else:
                        self.selected = True
            self.update()
    

    def mouseDoubleClickEvent(self, event):
        self.parent.deleteWordFromLink(self.index, self.type)


    def boundingRect(self):
        return self.rect.adjusted(-2, -2, 2, 2)

    def paint(self, painter, option, widget):

        pen = QPen()
        pen.setWidth(1)
	pen.setColor(Qt.white)
        painter.setPen(pen)
	painter.drawRect(self.rect)

        if self.selected:
            color = QColor(Qt.blue).light()
        elif self.isLinked:
            color = self.parent.determineColor(self.linkType)
            ######## Language Specific ########
            if self.language_mode in (AR, DEFAULT):
                if self.notTranslated:
                    if color == QColor("#FFCC33"): # INC
                        color = QColor(Qt.red).light()   
                    else:
                        color = QColor("#AFEEEE")  # COR, light blue
            ######## Language Specific ########

        else:
            color = QColor("#fafad2")      #light goldenrod yellow

        brush = QBrush(color)                        
        painter.fillRect(self.rect, brush)


    def contextMenuEvent(self, event):
        """Action to be taken on right click."""
        wrapped = []
        menu = QMenu(self.parentWidget())
        
        for text, tag in self.tags:
            wrapper = functools.partial(self.menuCall, tag)
            wrapped.append(wrapper)
            menu.addAction(text, wrapper)
        
        menu.exec_(event.screenPos())


    def changeTag(self, tag):
        sent = self.sent
        i = self.index

        if self.type == "s":
            self.data.sourceTags[sent, i] = tag

            # remove old TextBox from Scene
            self.parent.sourceTagList[i].text = ""
            self.parent.sourceTagList[i].update()
            tagTextBox = self.parent.sourceTagList[i]
            y = tagTextBox.pos().y()
            self.parent.scene.removeItem(self.parent.sourceTagList[i])
            del tagTextBox

            # add new TextBox to Scene
            self.parent.sourceTagList[i] = self.parent.addText(stag,y,tag,i,"s")

        elif self.type == "t":
            self.data.targetTags[sent, i] = tag

            # remove old TextBox from Scene
            tagTextBox = self.parent.targetTagList[i]
            y = tagTextBox.pos().y()
            self.parent.scene.removeItem(tagTextBox)
            del tagTextBox
            
            # add new TextBox to Scene
            self.parent.targetTagList[i] = self.parent.addText(ttag,y,tag,i,"t")


    def menuCall(self, tag):
        i = self.index
        sent = self.sent

        # prevent changing tags of "Not translated" links
        if self.type == "s":
            cTag = self.data.sourceTags[sent,i]  # current Tag
        elif self.type == "t":
            cTag = self.data.targetTags[sent,i]
        if cTag == "COO" or cTag == "CON" or cTag == "INC":
            text = QLabel(formatBlock('''
            Please delete the link first before changing the tag.
            '''))
            warnUser = dialogs.WarningDialog(text)
            warnUser.exec_()     
            return

        # prevent changing tags to "Not translated" if already linked
        if tag == "COO" or tag == "CON" or tag == "INC":
            if self.isLinked == True:
                text = QLabel(formatBlock('''
                Error: Please delete the existing link before 
                marking as COO, CON, or INC! Thanks!
                '''))
                warnUser = dialogs.WarningDialog(text)
                warnUser.exec_()
                return

        # change Tag (removes current text box and replaces with new one)
        self.changeTag(tag)

        ######## Language Specific ########
        if self.language_mode == CH:
            # Create an NT link or update link type
        
            if tag == "COO" or tag == "CON" or tag == "INC":
                self.parent.notTranslatedChinese(i, self.type)
            elif self.isLinked == True:   # change link

                # gather tags for all words linked to word just tagged
                s_tags=[]
                t_tags=[]
                (s_list,t_list,type) = self.parent.getLink(i, self.type)
                for s in s_list:
                    if (sent,s) in data.sourceTags:
                        s_tags.append(data.sourceTags[sent,s])
                for t in t_list:
                    if (sent,t) in data.targetTags:
                        t_tags.append(data.targetTags[sent,t])
                link_type = self.parent.determineLinkTypeCH(s_tags, \
                                                            t_tags,len(s_list))

                # highlight table row and boxes so that we can create link      
                row = self.parent.getLinkRow(i, self.type)
                self.parent.bottomTable.selectRow(row)
                self.parent.selectAppropriateBoxes()
                # self.parent.doCenterOn()

                # link is deleted and recreated as new link type
                self.parent.createLink(link_type)
        ######## Language Specific ########

class CustomQTableWidgetItem(QTableWidgetItem):
    def __init__(self, text):
        QTableWidgetItem.__init__(self, text)

    def __cmp__(self, other):
        print "Sorting"
       	a2 = str(self.text()).rstrip(" ").split(" ")
        b2 = str(other.text()).rstrip(" ").split(" ")
        a3 = tuple(a2)
        b3 = tuple(b2)
        return cmp(a3,b3)
    
    def __lt__(self, other):
#        print "Less than"
       	a = str(self.text()).rstrip(" ").split(" ")
        b = str(other.text()).rstrip(" ").split(" ")
        for i in range(0,len(a)):
            a[i] = int(a[i])
        for i in range(0,len(b)):
            b[i] = int(b[i])
        a = tuple(a)
        b = tuple(b)
#        print "Comparing",a,b,
#        if a < b:
#            print "True"
#        else:
#            print "False"
        return a < b        


class NavArea(QWidget):
    """Contains buttons for navigating sentences."""
    def __init__(self, language_mode, parent):
        QWidget.__init__(self, parent)
        self.parent = parent
            
	buttonPrevious = QPushButton("&Previous")
	buttonPrevious.setToolTip("Annotate previous sentence")
	self.connect(buttonPrevious, SIGNAL("clicked()"), \
                              self.parent.previousSentence)
	buttonNext = QPushButton("&Next")
	buttonNext.setToolTip("Annotate next sentence")
	self.connect(buttonNext, SIGNAL("clicked()"), self.parent.nextSentence)
	spinBoxLayout = QHBoxLayout()

        spinBoxLayout.addSpacing(50)
        spinBoxLayout.addWidget(buttonPrevious)
        spinBoxLayout.addSpacing(30)
        spinBoxLayout.addWidget(buttonNext)
        spinBoxLayout.addSpacing(200)

        ######## Language Specific ########
        if language_mode in (AR, DEFAULT):
            buttonDelete = QPushButton("&Delete")
            buttonDelete.setToolTip("Delete highlighted link from table")
            self.connect(buttonDelete, SIGNAL("clicked()"), self.parent.deleteLink)
            spinBoxLayout.addWidget(buttonDelete)
            spinBoxLayout.addSpacing(30)
        ######## Language Specific ########
        
        self.setLayout(spinBoxLayout)

class ButtonArea(QWidget):
    """Contains buttons for user actions."""
    def __init__(self,parent):
        QWidget.__init__(self,parent)
        self.parent = parent

	# Create right-middle buttons above link table
        buttonAreaLayout = QHBoxLayout()
        buttonUndo = QPushButton("&Undo")
        buttonUndo.setToolTip("Remove last link from table")
        self.connect(buttonUndo, SIGNAL("clicked()"), self.parent.undo)
        buttonClear = QPushButton("Clear")
        self.connect(buttonClear, SIGNAL("clicked()"), self.parent.clear)
        buttonDelete = QPushButton("&Delete")
        buttonDelete.setToolTip("Delete highlighted link from table")
        self.connect(buttonDelete, SIGNAL("clicked()"), self.parent.deleteLink)
        buttonRefresh = QPushButton("Refresh")
        buttonRefresh.setToolTip("Reload sentence to see updated word tags")
        self.connect(buttonRefresh, SIGNAL("clicked()"), self.parent.refresh)

        buttonAreaLayout.addSpacing(40)
        buttonAreaLayout.addWidget(buttonUndo)
        buttonAreaLayout.addSpacing(40)
        buttonAreaLayout.addWidget(buttonClear)
        buttonAreaLayout.addSpacing(40)
        buttonAreaLayout.addWidget(buttonDelete)
        buttonAreaLayout.addSpacing(40)
        buttonAreaLayout.addWidget(buttonRefresh)
        buttonAreaLayout.addSpacing(40)

        sizePolicy = QSizePolicy(QSizePolicy.Minimum, QSizePolicy.Minimum)
        self.setSizePolicy(sizePolicy)
        self.setLayout(buttonAreaLayout)

class LinkButtons(QWidget):
    """Contains buttons for creating/removing links between tokens."""
    def __init__(self, language_mode, parent):
        QWidget.__init__(self,parent)
        self.parent = parent

        # Left Side Layout
	buttonCorrect = QPushButton("&Correct")
	self.connect(buttonCorrect, SIGNAL("clicked()"), self.parent.correct)
	buttonIncorrect = QPushButton("&Incorrect")
	self.connect(buttonIncorrect, SIGNAL("clicked()"), self.parent.incorrect)
        leftBottomLayout = QHBoxLayout()
        sizePolicy = QSizePolicy(QSizePolicy.Minimum, QSizePolicy.Minimum)
        self.setSizePolicy(sizePolicy)

        leftBottomLayout.addWidget(buttonCorrect)
        leftBottomLayout.addWidget(buttonIncorrect)

        ######## Language Specific ########
        if language_mode in (AR, DEFAULT):
            buttonNotTrans = QPushButton("N&ot Translated")
            buttonNotTransInc = QPushButton("Not &Translated Incorrect")
            self.connect(buttonNotTrans, SIGNAL("clicked()"), \
                                       self.parent.notTranslatedArabic)
            self.connect(buttonNotTransInc, SIGNAL("clicked()"), \
                                       self.parent.notTranslatedIncorrectArabic)
            leftBottomLayout.addWidget(buttonNotTrans)
            leftBottomLayout.addWidget(buttonNotTransInc)
            leftBottomLayout.insertSpacing(0,40)
            leftBottomLayout.insertSpacing(2,40)
            leftBottomLayout.insertSpacing(4,40)
            leftBottomLayout.insertSpacing(6,40)
            leftBottomLayout.insertSpacing(8,40)

            leftSideLayout = QVBoxLayout()
            leftSideLayout.addLayout(leftBottomLayout)

            # comment field
            CommentLayout = QHBoxLayout()
            commentLabel = QLabel("Comments:  ")
            self.parent.commentField = QLineEdit()
            font = QFont(source_text_font[0], source_text_size[0], source_text_bold)
            self.parent.commentField.setFont(font)
            CommentLayout.addWidget(commentLabel)
            CommentLayout.addWidget(self.parent.commentField)
            leftSideLayout.addLayout(CommentLayout)
            
        else:
            leftBottomLayout.insertSpacing(0,150)
            leftBottomLayout.insertSpacing(2,30)
            leftBottomLayout.insertSpacing(4,150)

            leftSideLayout = QVBoxLayout()
            leftSideLayout.addLayout(leftBottomLayout)
        ######## Language Specific ########
        
        self.setLayout(leftSideLayout)

