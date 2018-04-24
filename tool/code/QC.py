#!/ldc/bin/python2.6
# -*- coding: utf-8 -*-
# QC.py

from utils import *

class QualityControl(QMainWindow):
   def __init__(self, data, language_mode, parent=None):
        super(QMainWindow, self).__init__(parent)   
        self.parent = parent
        self.data = data
        self.language_mode = language_mode
        ######## Language Specific ########
        if self.language_mode in (DEFAULT, AR):
           font = QFont(source_box_font[0],14,QFont.Normal)
        else:
           font = QFont(source_box_font[1],14,QFont.Normal)
        ######## Language Specific ########
        self.setFont(font)
    	self.setWindowTitle("Quality Control Window")

        label = QLabel("Language: ")
        ######## Language Specific ########
        if self.language_mode == AR:
           self.rSource = QRadioButton("Arabic")
        elif self.language_mode == CH:
           self.rSource = QRadioButton("Chinese")
        else:
           self.rSource = QRadioButton("Source")
        ######## Language Specific ########
        self.rEnglish = QRadioButton("English")

        self.wordSearch = QLineEdit()
        searchButton = QPushButton("Search")
        self.connect(searchButton, SIGNAL("clicked()"), self.search)
        self.exactMatchBox = QCheckBox("Whole word matches only")

	self.table = QualityControlTable(self)
      	self.table.setColumnCount(9)
        self.table.setAlternatingRowColors(True)
	self.table.setSelectionBehavior(QTableWidget.SelectRows)
	self.table.setSelectionMode(QTableWidget.SingleSelection)
        self.table.setHorizontalHeaderLabels(("Sent#", "Search Term", \
               "English Link","Token #s","Source Link","Token #s", "Link Type"))
	self.table.resizeColumnsToContents()
#        self.connect(self.table, SIGNAL("accept()"), self, SLOT("accept()"))

#        self.okButton = QPushButton("Return to main program")
#	self.connect(self.okButton, SIGNAL("clicked()"), self, SLOT("accept()"))


# SPLITTER STUFF
        radioSplitter = QSplitter(Qt.Vertical)
        radioSplitter.addWidget(self.rSource)
        radioSplitter.addWidget(self.rEnglish)

        topSplitter = QSplitter(Qt.Horizontal)
        topSplitter.addWidget(label)
        topSplitter.addWidget(radioSplitter)
        topSplitter.addWidget(self.wordSearch)
        topSplitter.addWidget(searchButton)
        topSplitter.addWidget(self.exactMatchBox)

        mainSplitter = QSplitter(Qt.Vertical)
        mainSplitter.addWidget(topSplitter)
        mainSplitter.addWidget(self.table)
#       mainSplitter.addWidget(self.okButton)
        mainSplitter.setStretchFactor(0,0)
        mainSplitter.setStretchFactor(1,10)
#        mainSplitter.setStretchFactor(2,0)

        self.setCentralWidget(mainSplitter)


# LAYOUT STUFF
#        radioLayout = QVBoxLayout()
#        radioLayout.addWidget(self.rSource)
#        radioLayout.addWidget(self.rEnglish)
      
#        topLayout = QHBoxLayout()
#        topLayout.addWidget(label)
#        topLayout.addLayout(radioLayout)
#        topLayout.addWidget(self.wordSearch)
#        topLayout.addWidget(searchButton)
#        topLayout.addWidget(self.checkBox)     
        
#        mainLayout = QVBoxLayout()
#        mainLayout.addLayout(topLayout)
#        mainLayout.addWidget(self.table)
##        mainLayout.addWidget(self.okButton)
#	self.setLayout(mainLayout)
        
        self.rEnglish.setChecked(True)
        self.search()

   def valid(self, sent, l1, l2):   
       # check whether search term appears in link

       # if searching for English word:
       if self.rEnglish.isChecked():
           string = str(self.wordSearch.text())  # .strip()
           t_toks = list(l2)
           s = self.data.target[sent]
#           print "\n"
#           print t_toks
#           print c
#           print "Search string:",string.lower()
#           print "Checking in:",cstring.lower()
           if self.exactMatchBox.isChecked():
               for k in range(0,len(t_toks)):
                   if s[t_toks[k]].lower() == string.lower():
                       return True
               return False   # string not equal to any word
           else:
               c = []
               for k in range(0,len(t_toks)):
                   c.append(s[t_toks[k]])
               cstring = " ".join(c)
               if string.lower() in cstring.lower():
                   return True
               else:
                   return False

       elif self.rSource.isChecked():
           string = self.wordSearch.text()
           s_toks = list(l1)
           s = self.data.source[sent]        

           if self.exactMatchBox.isChecked():
               for k in range(0, len(s_toks)):
                   if unicode(QString.fromUtf8(s[s_toks[k]])) == string:
                       return True
               return False
           else:
               c = QStringList()
               space = QString(" ")
               for k in range(0,len(s_toks)):
                   c.append(unicode(QString.fromUtf8(s[s_toks[k]])))
               cstring = c.join(space)
               if cstring.contains(string):
                   return True
               else:
                   return False

   def search(self):
       self.table.setSortingEnabled(False)

       string = self.wordSearch.text()

       # reset table
       self.table.clear()
       for row in range(0,self.table.rowCount()):
           self.table.removeRow(0)
           
      ######## Language Specific ########
       if self.language_mode == AR:
          self.table.setHorizontalHeaderLabels(("Sent#", "Search Term", "English Link",
                                                "Tags","Arabic Link","Tags",
                                                "Link Type","Eng.Tkn#s","Arb.Tkn#s"))
       elif self.language_mode == CH:
          self.table.setHorizontalHeaderLabels(("Sent#", "Search Term", "English Link",
                                                "Tags","Chinese Link","Tags",
                                                "Link Type","Eng.Tkn#s","Chn.Tkn#s"))
       else:
          self.table.setHorizontalHeaderLabels(("Sent#", "Search Term", "English Link",
                                                "Tags","Source Link","Tags",
                                                "Link Type","Eng.Tkn#s","Src.Tkn#s"))
       ######## Language Specific ########
       row = -1
       for (s,l1,l2) in self.data.links.keys():
           
           if self.valid(s,l1,l2):    
    
               row = row + 1
               self.table.insertRow(row)

               # Sentence Number (Col. 0)
               item = QTableWidgetItem(str(s+1))
               item.setTextAlignment(Qt.AlignCenter)
               item.setFlags(item.flags() ^ Qt.ItemIsEditable)
               self.table.setItem(row,0,item)

               # Search term (Col. 1)
               item = QTableWidgetItem(string)
               item.setTextAlignment(Qt.AlignCenter)
               item.setFlags(item.flags() ^ Qt.ItemIsEditable)
               self.table.setItem(row,1,item)
                   
               # English Words (Col. 2)
               sent = self.data.target[s]
               en_l = []
               for r in range(0,len(l2)):
                    en_l.append(sent[l2[r]])
               en = " ".join(en_l)
               item = QTableWidgetItem(en)
               item.setTextAlignment(Qt.AlignCenter)
               item.setFlags(item.flags() ^ Qt.ItemIsEditable)
               self.table.setItem(row,2,item)

               # English Tags (Col. 3)
               tag_l = []
               for r in range(0,len(l2)):
                   if l2[r] != 0:
                       if self.data.targetTags[s,l2[r]] != "":
                           tag_l.append(self.data.targetTags[s,l2[r]])
               tags = ", ".join(tag_l)
               item = QTableWidgetItem(tags)
               item.setFlags(item.flags() ^ Qt.ItemIsEditable)
               self.table.setItem(row,3,item)
            
               # Arabic/Chinese Words (Col. 4)
               source_l = []
               sent = self.data.source[s]
               for r in range(0,len(l1)):
                   source_l.append(sent[l1[r]])
               source = " ".join(source_l)
               source2 = QString.fromUtf8(source)
               item = QTableWidgetItem(source2)
               item.setTextAlignment(Qt.AlignCenter)
               self.table.setItem(row,4,item)               

               # Arabic/Chinese Tags (Col. 5)
               tag_l = []
               for r in range(0,len(l1)):
                   if l1[r] != 0:
                       if self.data.sourceTags[s,l1[r]] != "":
                           tag_l.append(self.data.sourceTags[s,l1[r]])
               tags = ", ".join(tag_l)
               item = QTableWidgetItem(tags)
               item.setFlags(item.flags() ^ Qt.ItemIsEditable)
               self.table.setItem(row,5,item)

               # Link Type (Col. 6)
               item = QTableWidgetItem(self.data.links[s,l1,l2])
               item.setTextAlignment(Qt.AlignCenter)
               item.setFlags(item.flags() ^ Qt.ItemIsEditable)
               self.table.setItem(row,6,item)              

               # English Token Numbers (Col. 7)
               l = list(l2)
               for r in range(0, len(l)):
                   l[r] = str(l[r])
               text = " ".join(l)
               item = QTableWidgetItem(text)
               item.setTextAlignment(Qt.AlignCenter)
               self.table.setItem(row,7,item)


               # Arabic/Chinese Token Numbers (Col. 8)
               l = list(l1)
               for r in range(0,len(l)):
                   l[r] = str(l[r])
               text = " ".join(l)
               item = QTableWidgetItem(text)
               item.setTextAlignment(Qt.AlignCenter)
               self.table.setItem(row,8,item)


       self.table.resizeColumnsToContents()

       self.table.setSortingEnabled(True)


class QualityControlTable(QTableWidget):
    def __init__(self, parent):
        QTableWidget.__init__(self, parent)
        self.parent = parent

    def mouseDoubleClickEvent(self, event):
       # get sent, source position of link to highlight
       row = self.parent.table.itemAt(event.pos()).row()
       item = self.parent.table.item(row,0)
       sent = int(item.text())-1
       
       item = self.parent.table.item(row,7)
       digits = item.text()
       first = re.compile("^(\d+)")
       pos = int(first.match(digits).group(1))

       # load correct sentence
       self.parent.parent.goToSentence(sent)

       # highlight correct link (row in table)
       #print "Selecting link containing English token",pos
       self.parent.parent.highlight(pos,"t")
       
       # select boxes corresponding to selected table row
       self.parent.parent.selectAppropriateBoxes()
       self.parent.parent.doCenterOn()


