#!/ldc/bin/python
# -*- coding: utf-8 -*-

import sys
import os
import re
import shutil
import codecs
from unicodedata import *
from PyQt4.QtCore import *
from PyQt4.QtGui import *

import utils
import dialogs

class DataStructure():
    def __init__(self,paFilename,lang):
        self.paFilename = paFilename
        self.lang = lang

        # this is each individual pair, useful for drawing lines
        self.align = {}         # align[sent,s_i,t_j] = link_type

        # this has multiple words in one link
        self.links = {}         # links[sent,(s_i1, ...),(t_j1,...)] = link_type

        self.sourceTags = {}    # sourceTags[sent,token] = tag (3-letter code)
        self.targetTags = {}    # targetTags[sent,token] = tag (3-letter code)

        self.source_sent=[]     # source_sent[i] - ith sentence as one string
        self.target_sent=[]
        self.untokenized_list=[]
        self.source=[]          # source[i] - the ith sentence as list of tokens
        self.target=[]

        self.status = {}        # status[i] - True if ith sentence rejected
        self.comment = {}       # comment[i] - comment on sentence i

        self.load()


    def updateLinkType(self, sent, s_list, t_list, link_type):

        self.links[sent,tuple(s_list),tuple(t_list)] = link_type

        for s in s_list:
            for t in t_list:
                self.align[sent,s,t] = link_type


    def load(self):        
        try:
            paFile = open(self.paFilename, "r")
        except IOError, msg:
            print msg
            print "Steve, there was a file load error", sys.exc_info()[0]
            sys.exit(2)

        try:
            self.source_sent=[]    
            self.target_sent=[]
            self.source=[]         
            self.target=[]
            self.untokenized_list=[]

            read_source=False
            read_translation=False
        
            beginSent = re.compile("<sentence id=\"(\d+)(.*)\">")
            endSent = re.compile("</sentence>")
            beginT = re.compile("<translation>")
            beginS = re.compile("<source>")
            endT = re.compile("</translation>")
            endS = re.compile("</source>")
            word = re.compile("^(\d+) (\S+) : (.*)$")
            link = re.compile("^(\d+.*) <==> (\d+.*?) \/\/ (\w+) \/\/") 
            comment = re.compile("^Comment: (.*)")
            leftBraceRE = re.compile("{")
            untokenized = re.compile("## (.*)")
            subs = "ÂœóñÈ"    # alef with hamza below
            raw_toggle = False
            source_text = None
            target_text = None
            for line in paFile:
                if link.match(line):
                    s_toks = link.match(line).group(1).split(" ")
                    t_toks = link.match(line).group(2).split(" ")
                    type = link.match(line).group(3)
                    for i in range(0,len(s_toks)):
                        s_toks[i] = int(s_toks[i])
                        for j in range(0,len(t_toks)):
                            t_toks[j] = int(t_toks[j])
                            self.align[sent-1,s_toks[i],t_toks[j]] = type      
                    self.links[sent-1,tuple(s_toks),tuple(t_toks)] = type        
                elif beginSent.match(line):
                    sent = int(beginSent.match(line).group(1))
                    source_line=["<not translated>"]
                    target_line=["<not translated>"]
                    self.status[sent-1] = ""
                    self.comment[sent-1] = ""
                    if "rejected" in beginSent.match(line).group(2):
                        self.status[sent-1] = "rejected"

                elif endSent.match(line):
                    self.source_sent.append(source_text)
                    self.target_sent.append(target_text)
                    source_text = None
                    target_text = None
                    self.source.append(source_line)
                    self.target.append(target_line)
                    raw_toggle = False
                # emish
                elif line[:2] == "##":
                    if not raw_toggle:
                        raw_toggle = not raw_toggle
                        if line[2:] != "\n":
                            source_text = line[2:]
                    else:
                        raw_toggle = not raw_toggle
                        if line[2:] != "\n":
                            target_text = line[2:]
                elif beginS.match(line):
                    read_source=True
                elif beginT.match(line):
                    read_translation=True
                elif endS.match(line):
                    read_source=False
                    if not source_text:
                        source_text = " ".join(source_line[1:len(source_line)])
                elif endT.match(line):
                    read_translation=False
                    if not target_text:
                        target_text = " ".join(target_line[1:len(target_line)])
                elif word.match(line) and read_source:
                    source_line.append(word.match(line).group(2))
                    self.sourceTags[sent-1, int(word.match(line).group(1))] = \
                            word.match(line).group(3)
                elif word.match(line) and read_translation:
                    target_line.append(word.match(line).group(2))
                    self.targetTags[sent-1, int(word.match(line).group(1))] = \
                            word.match(line).group(3)
                elif comment.match(line):
                    if comment.match(line).group(1):
                        text = comment.match(line).group(1)
                        text2 = QString.fromUtf8(text)
                        self.comment[sent-1] = text2
                    else:
                        self.comment[sent-1] = ""
                elif untokenized.match(line):
                    self.untokenized_list.append(untokenized.match(line).group(1))

            ## if we loaded untokenized data, do nothing
            ## otherwise store tokenized data as untokenized for reference sentences
            ## self.source_sent is what will be displayed
            if len(self.untokenized_list) == len(self.source_sent):
                for i in range(0,len(self.source_sent)):
                    self.source_sent[i] = self.untokenized_list[i]

            paFile.close()
        except Exception, e:
            print e
            app2 = QApplication(sys.argv)
            text = QLabel(utils.formatBlock('''
            Input file has corrupt data; program cannot cannot load.
            Please report this problem to Steve.
            '''))
            warnUser = dialogs.WarningDialog(text)
            warnUser.show() 
            app2.exec_()       

    def save(self):
        base = os.path.basename(self.paFilename)
        dir = os.path.dirname(self.paFilename)

        # write the file
        try:
           file = open(self.paFilename, "w")  #, encoding="utf-8")
           for sent in range(0,len(self.source_sent)):
              file.write("<sentence id=\""+str(sent+1)+"\"")
              if sent in self.status.keys() and self.status[sent] == "rejected":
                  file.write(" status=\"rejected\">\n")
              else:
                  file.write(" status=\"\">\n")
              if len(self.untokenized_list) != 0:
                  file.write("// ") 
                  for i in range(1,len(self.source[sent])):
                      file.write(self.source[sent][i]+" ")
                  file.write("\n")
                  file.write("// "+self.target_sent[sent]+"\n")
                  file.write("## "+self.source_sent[sent]+"\n")
              else:
                  file.write("// "+self.source_sent[sent]+"\n")
                  file.write("// "+self.target_sent[sent]+"\n")              
              file.write("<source>\n")
              for i in range(1,len(self.source[sent])):
                if (sent, i) in self.sourceTags:
                   file.write(str(i)+" "+self.source[sent][i]+" : ")
                   file.write(self.sourceTags[sent,i] + "\n")
                else:
                   file.write(str(i)+" "+self.source[sent][i]+" : \n")
              file.write("</source>\n")
              file.write("<translation>\n")
              for i in range(1,len(self.target[sent])): 
                if (sent, i) in self.targetTags:
                  file.write(str(i)+" "+self.target[sent][i]+" : ")
                  file.write(self.targetTags[sent,i] + "\n")
                else:
                  file.write(str(i)+" "+self.target[sent][i]+" : \n")
              file.write("</translation>\n")
              file.write("<alignment>\n")
              for w,x,y in self.links.keys():
                  if w == sent:
                     for i in x:
                         file.write(str(i)+" ")
                     file.write("<==> ")
                     for i in y:
                         file.write(str(i)+" ")
                     file.write("// "+str(self.links[w,x,y])+" // ")
                     for i in x:
                         file.write(self.source[int(w)][int(i)]+" ")
                     file.write("<==> ")
                     for i in y:
#                        file.write(int(w) int(i))
                         file.write(self.target[int(w)][int(i)]+" ")
                     file.write("\n")
              file.write("</alignment>\n")
              if self.lang == "AR":
                  file.write("Comment: ")
                  contents = QString(self.comment[sent]).toUtf8()
                  file.write(contents)
                  file.write("\n")
              file.write("</sentence>\n\n\n")

           file.close()
        except IOError ,e:
            print e
            #app2 = QApplication(sys.argv)
            text = QLabel(utils.formatBlock('''
            There was a problem saving.  Please do not continue, as even if
            the program continues to work, there may be data loss/truncation. 
            Please immediately report this problem to Steve and note which
            file you were working on.
            '''))
            warnUser = dialogs.WarningDialog(text)
            warnUser.exec_() 
            #app2.exec_()              

    def needsSave(self):
        print ("Does the file need to be saved?")


    def saveGiza(self):
        giza = self.paFilename + ".giza"
        file = open(giza, "w")

        # write the file
        for sent in range(0,len(self.source_sent)):
         if sent in self.status.keys() and self.status[sent] == "rejected":
          file.write("rejected\n")
         else:
          items = self.links.keys()
          items.sort()
          for (s,x,y) in items:
            if s == sent:
              s_list = list(x)
              t_list = list(y)
     
              # handle MET tags 
              mta = 0

              ## print source tokens in link
              if s_list[0] != 0:
                file.write(str(s_list[0]))
                if not (self.sourceTags[s,s_list[0]] == '' or self.sourceTags[s,s_list[0]] == 'FUN' or \
                  self.sourceTags[s,s_list[0]] == 'MET'):
                      file.write("["+self.sourceTags[s,s_list[0]]+"]")

                      # handle MET tags         
                      if (self.sourceTags[s,s_list[0]] == 'MET'):
                           mta = 1

                for i in range(1,len(s_list)):
                   file.write(","+str(s_list[i]))
                   if not (self.sourceTags[s,s_list[i]] == '' or self.sourceTags[s,s_list[i]] == 'FUN' or \
                     self.sourceTags[s,s_list[i]] == 'MET'):
                         file.write("["+self.sourceTags[s,s_list[i]]+"]")

                         # handle MET tags
                         if (self.sourceTags[s,s_list[i]] == 'MET'):
                               mta = 1

              ## print translation tokens in link
              file.write("-")
              if t_list[0] != 0:
                file.write(str(t_list[0]))
                if not (self.targetTags[s,t_list[0]] == '' or self.targetTags[s,t_list[0]] == 'FUN' or \
                  self.targetTags[s,t_list[0]] == 'MET'):
                       file.write("["+self.targetTags[s,t_list[0]]+"]")

                       # handle MET tags
                       if (self.targetTags[s,t_list[0]] == "MET"):
                             mta = 1

                for j in range(1,len(t_list)):
                   file.write(","+str(t_list[j]))
                   if not (self.targetTags[s,t_list[j]] == '' or self.targetTags[s,t_list[j]] == 'FUN' or \
                     self.targetTags[s,t_list[j]] == 'MET'):
                           file.write("["+self.targetTags[s,t_list[j]]+"]")

                           # handle MET tags
                           if (self.targetTags[s,t_list[j]] == "MET"):
                                 mta = 1

              ## print link type
              if (mta == 1):
                   self.links[s,x,y] = "MTA"
              if self.links[s,x,y] == "NT":
                   self.links[s,x,y] = "NTR"    
              if self.links[s,x,y] == "INC":
                   self.links[s,x,y] = "TIN"
              file.write("("+self.links[s,x,y]+") ")

          file.write("\n")

        file.close()


    def saveGizaWithoutTagsOrLinkTypes(self):
        giza = self.paFilename + ".giza"
        file = open(giza, "w")

        # write the file
        for sent in range(0,len(self.source_sent)):
          items = self.links.keys()
          items.sort()
          for (s,x,y) in items:
            if s == sent:
              s_list = list(x)
              t_list = list(y)
              if s_list[0] != 0:
                file.write(str(s_list[0]))
                if self.sourceTags[s,s_list[0]] != '':
                   file.write("["+self.sourceTags[s,s_list[0]]+"]")
                for i in range(1,len(s_list)):
                   file.write(","+str(s_list[i]))
                   if self.sourceTags[s,s_list[i]] != '':
                      file.write("["+self.sourceTags[s,s_list[i]]+"]")
              file.write("-")
              if t_list[0] != 0:
                file.write(str(t_list[0]))
                if self.targetTags[s,t_list[0]] != '':
                   file.write("["+self.targetTags[s,t_list[0]]+"]")
                for j in range(1,len(t_list)):
                   file.write(","+str(t_list[j]))
                   if self.targetTags[s,t_list[j]] != '':
                      file.write("["+self.targetTags[s,t_list[j]]+"]")
              file.write("("+self.links[s,x,y]+") ")
          file.write("\n")
        file.close()


    def saveTokensSourceCh(self):
        # tokens space delimited, no offsets

        saveSourceFile = self.paFilename + ".cmn.tkn"   
        file = open(saveSourceFile, "w")

        # write tokens to file
        for i in range(0, len(self.source_sent)):
            contents = QString(self.source_sent[i]).toUtf8()
            file.write(self.source_sent[i])
            file.write("\n")
        file.close()    

    def saveTokensTargetCh(self):
        # tokens space delimited, no offsets

        saveTargetFile = self.paFilename + ".eng.tkn"
        file = open(saveTargetFile, "w")

        # write tokens to file
        for i in range(0, len(self.target_sent)):
            file.write(self.target_sent[i])
            file.write("\n")
        file.close()


