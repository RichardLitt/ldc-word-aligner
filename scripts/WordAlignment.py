
''' Module used for a variety of manipulations of WA files. '''

Kate Peterson, September - October 2011
petka@ldc.upenn.edu'''

import codecs
from os import path

def changeExtension(filename,newExtension):
    nameparts = filename.split('.')
    nameparts[-1] = newExtension
    return str.join('.',nameparts)

def copen(filename, mode='rb'):
    '''Makes sure we open files with utf-8 encoding.'''
    if (mode == 'r') or (mode == 'w'):
        mode += 'b'
    return codecs.open( filename, mode, encoding='utf-8')

def groupTuples(listIn):
    # First pass: group alignments with the same source token/tokens
    mappings = dict()
    # Make sure we only enter each sourceID once
    for tup in listIn:
        if tup[0] in mappings.keys(): # sourceID already has a targetID mapped
            # append new targetID to list associated with sourceID
            mappings.update(\
                {tup[0]:[y for y in (x for x in mappings[tup[0]])] + [tup[1]]})
        else:
            mappings.update({tup[0]: [tup[1]]})
    # Second pass: group sourceIDs that have the same group of targetIDs
    backMap = dict()     # index of occurringTargList --> list of sourceIDs
    groupTargLists = []    # List rather than backMap.values() so we can index

    for sourceID, targetList in mappings.iteritems():
        if sorted(targetList) in groupTargLists: # source shares these targets
            # update the list of sources associated with the target list index
            tlindex = groupTargLists.index(sorted(targetList))
            backMap.update({tlindex: [y for y in (x for x in backMap[tlindex])]
                                + [sourceID]})
        else: # thus far the target list is unique, make new entry
            groupTargLists.append( sorted(targetList) )
            backMap.update({groupTargLists.index(sorted(targetList)):
                            [sourceID]})
    # Assemble final pairings
    return sorted([(srcs,groupTargLists[tindex]) for tindex,srcs in \
                backMap.iteritems()])

def groupAlignments(listIn):
    ''' Similar to groupTuples(), but does not group alignments with 0,
    which corresponds to Null or untranslated tokens.
    Accepts a list of (str,str) ungrouped tuples, 
    returns a list of (list,list) tuples with only one item in each list 
    whenever one of these items is '0', but otherwise grouped.
    Where ([0] , [m1,m2]) is separated as ([0],[m1]) and ([0],[m2])
    and ([n1,n2], [0]) is separated as ([n1],[0]) and ([n2],[0]).'''
    grouped = groupTuples(listIn)
    for i in range(len(grouped)):
        tup = grouped[i]
        expanded = []
        if 0 in tup[0]:
            if len(tup[1]) > 1:
                for x in tup[1]:
                    expanded.append(([0],[x]))
                    grouped.insert(i,expanded)
                    grouped.pop(i)
        elif 0 in tup[1]:
            if len(tup[0]) > 1:
                for x in tup[0]:
                    expanded.append(([x],[0]))
                    grouped.insert(i,expanded)
                    grouped.pop(i)
    return sorted(grouped)
    

def ungroupTuples(listIn):
    ''' Takes a list of (list,list) tuples and returns a list of 
    (item,item) tuples.'''
    output = []
    for tuple in listIn:
        for a in tuple[0]:
            for b in tuple[1]:
                output.append((a,b))
    return sorted(output)

def parseWAAlignments(alignStrings):
    '''Takes a list of alignment strings from a WA file. 
    Returns a list of (list,list) alignment tuples.'''
    import re
    alignments = []
    for string in alignStrings:
        parts = string.split("//")[0].split("<==>")
        alignPattern = re.compile(r'(\d+) ')
        sourceTokens = alignPattern.findall(parts[0])
        targetTokens = alignPattern.findall(parts[1])
        alignments.append(([int(x) for x in sourceTokens],
                           [int(y) for y in targetTokens]))
    return alignments

'''class Alignment:
    source = []
    target = []
    type = ''

    def __init__(self,sourceList,targetList, type=None):
        source = sourceList
        target = targetList
        if type is not None:
            self.type = type'''

class Sentence:
 
    def __init__(self,input=None,type="WA"):
        self.sTokens = []
        self.tTokens = []
        self.alignments = []
        self.status = ''
        if input is not None and type=="WA":
            self.initFromWA(input)

    def initFromWA(self,s):
        '''Args: self and list of lines within <sentence> tags in WA file.'''
        self.status = s[0][s[0].index("status")+9:-2]
        self.sTokens = s[1][3:].split()
        self.tTokens = s[2][3:].split()
        self.alignments = parseWAAlignments(s[s.index('<alignment>\n')+1:\
                                                  s.index('</alignment>\n')])
        # Make sure alignments are grouped except for Null/untranslated
        self.alignments = groupAlignments(ungroupTuples(self.alignments))

    def reversed(self):
        ''' Returns a new Sentence object with the source and target 
        swapped.'''
        flippedAligns = []
        for a in self.alignments:
            flippedAligns.append((a[1],a[0]))
        reversed = Sentence()
        reversed.sTokens = self.tTokens
        reversed.tTokens = self.sTokens
        reversed.alignments = flippedAligns
        return reversed

    def getUngroupedAlignments(self):
        return ungroupTuples(self.alignments)

    def groupedAlignmentsNotNull(self):
        return groupAlignments(self.ungroupedAlignmentsNotNull())
    
    def ungroupedAlignmentsNotNull(self):
        output = []
        for tuple in self.getUngroupedAlignments():
            if 0 not in tuple[0] and 0 not in tuple[1]:
                output.append(tuple)
        return output

    def formatAlignmentsLong(self):
        '''Return the lines that beloing in the .wa <alignment> section.'''
        waLines = []
        properlyGrouped = groupAlignments(self.getUngroupedAlignments())
        for a in sorted(properlyGrouped):
        # COR is an alignment type needed for the graphical align software
            if '0' in a[0]:
                waLine = '%s <==> %s // COR // %s <==> %s\n' % (
                    str.join(' ',(str(x) for x in a[0])),
                    str.join(' ',(str(y) for y in a[1])), #.wa indexes from 1
                    'NT',
                    str.join(' ',(self.tTokens[int(z)-1] for z in a[1])))
                waLines.append(waLine)
            elif '0' in a[1]:
                waLine = '%s <==> %s // COR // %s <==> %s\n' % (
                    str.join(' ',(str(x) for x in a[0])),
                    str.join(' ',(str(y) for y in a[1])), #.wa indexes from 1
                    str.join(' ',(self.sTokens[int(w)-1] for w in a[0])),
                    'NT')
                waLines.append(waLine)
            else:
                try:
                    waLine = '%s <==> %s // COR // %s <==> %s\n' % (
                        ' '.join(str(x) for x in a[0]),
                        ' '.join(str(y) for y in a[1]), #.wa indexes from 1
                        ' '.join(self.sTokens[int(w)-1] for w in a[0]),
                        ' '.join(self.tTokens[int(z)-1] for z in a[1]))
                    waLines.append(waLine)
                except IndexError:
                    "Token id given in alignment doesn't correspond with token \
                    in sentence."
                    break
                
        return waLines
    
    def formatAlignments(self):
        '''Return the lines that beloing in the .wa <alignment> section.'''
        waLines = []
        properlyGrouped = groupAlignments(self.getUngroupedAlignments())
        for a in sorted(properlyGrouped):
        # COR is an alignment type needed for the graphical align software
            try:
                waLine = '%s <==> %s // COR // \n' % (
                    str.join(' ',(str(x) for x in a[0])),
                    str.join(' ',(str(y) for y in a[1])))
                waLines.append(waLine)
            except IndexError:
                "Token id given in alignment doesn't correspond with token \
                in sentence."
                break
        return waLines

    def fineIntersect(self,otherSentence):
        ''' Returned intersection is still ungrouped.'''
        x = self.getUngroupedAlignments()
        y = otherSentence.getUngroupedAlignments()
        intersection = []
        
        for a in x:
            if a in y: 
                intersection.append(a)
        
        return intersection

    def coarseIntersect(self,otherSentence):
        ''' Returned intersection is grouped.'''
        intersection = []
        
        for a in self.alignments:
            if a in otherSentence.alignments: 
                intersection.append(a)

        return intersection

    def fineUnion(self,otherSentence):
        union = ungroupTuples(self.alignments)
        other = ungroupTuples(otherSentence.alignments)
        for tup in other:
            if tup not in union:
                union.append(tup)
        return sorted(union)

class WordAlignment:

    def __init__(self,inputFile=None):
        self.sentences = []
        if inputFile is None:
            self.fileName = ''
        else:
            self.fileName = path.basename(inputFile)
            self.path = path.dirname(inputFile)
            waFile = copen(inputFile,'r')
            self.initFromWA(waFile)

    def coarsePrecision(self,standardWA, ignoreUntranslated = False):
        ''' Compares self against a word alignment standard.
        Returns precision (treating a many-to-many group as one alignment).'''
        proposed = 0
        correctlyProposed = 0 
        if ignoreUntranslated:
            for i in range(len(self.sentences)): 
                if self.sentences[i].status != "rejected" and \
                        standardWA.sentences[i].status != "rejected":
                    for a in self.sentences[i].groupedAlignmentsNotNull():
                        proposed += 1
                        if a in standardWA.sentences[i].groupedAlignmentsNotNull(): 
                            correctlyProposed += 1
            return correctlyProposed / (1.0*proposed)
        else:
            for i in range(len(self.sentences)): 
                if self.sentences[i].status != "rejected" and \
                        standardWA.sentences[i].status != "rejected":
                    for a in self.sentences[i].alignments:
                        proposed += 1
                        if a in standardWA.sentences[i].alignments: 
                            correctlyProposed += 1
            return correctlyProposed / (1.0*proposed)

    def coarseRecall(self,standardWA, ignoreUntranslated = False):
        ''' Compares self against a word alignment standard.
        Returns recall (treating a many-to-many group as one alignment).'''
        correct = 0
        correctlyProposed = 0
        if ignoreUntranslated:
            for i in range(len(self.sentences)): 
                if self.sentences[i].status != "rejected" and \
                        standardWA.sentences[i].status != "rejected":
                    for a in standardWA.sentences[i].groupedAlignmentsNotNull():
                        correct += 1
                        if a in self.sentences[i].groupedAlignmentsNotNull(): 
                            correctlyProposed += 1
            return correctlyProposed / (1.0*correct)
        else:
            for i in range(len(self.sentences)): 
                if self.sentences[i].status != "rejected" and standardWA.sentences[i].status != "rejected":
                    for tup in standardWA.sentences[i].alignments:
                        correct += 1
                        if tup in self.sentences[i].alignments: 
                            correctlyProposed += 1
            return correctlyProposed / (1.0*correct)

    def finePrecision(self,standardWA, ignoreUntranslated = False):
        ''' Compares self against a word alignment standard.
        Returns precision (using individual one-to-one alignments).'''
        proposed = 0
        correctlyProposed = 0
        if ignoreUntranslated:
            for i in range(len(self.sentences)): 
                if self.sentences[i].status != "rejected" and \
                        standardWA.sentences[i].status != "rejected":
                    for a in self.sentences[i].ungroupedAlignmentsNotNull():
                        proposed += 1
                        if a in standardWA.sentences[i].ungroupedAlignmentsNotNull(): 
                            correctlyProposed += 1
            return correctlyProposed / (1.0*proposed)
        else:
            for i in range(len(self.sentences)): 
                if self.sentences[i].status != "rejected" and \
                        standardWA.sentences[i].status != "rejected":
                    for a in self.sentences[i].getUngroupedAlignments():
                        proposed += 1
                        if a in standardWA.sentences[i].getUngroupedAlignments(): 
                            correctlyProposed += 1
            return correctlyProposed / (1.0*proposed)

    def fineRecall(self,standardWA, ignoreUntranslated = False):
        ''' Compares self against a word alignment standard.
        Returns recall (using individual one-to-one alignments).'''
        correct = 0
        correctlyProposed = 0
        if ignoreUntranslated:
            for i in range(len(self.sentences)): 
                if self.sentences[i].status != "rejected" and \
                        standardWA.sentences[i].status != "rejected":
                    for a in standardWA.sentences[i].ungroupedAlignmentsNotNull():
                        correct += 1
                        if a in self.sentences[i].ungroupedAlignmentsNotNull(): 
                            correctlyProposed += 1
            return correctlyProposed / (1.0*correct)
        else:
            for i in range(len(self.sentences)): 
                if self.sentences[i].status != "rejected" and \
                        standardWA.sentences[i].status != "rejected":
                    for a in standardWA.sentences[i].getUngroupedAlignments():
                        correct += 1
                        if a in self.sentences[i].getUngroupedAlignments(): 
                            correctlyProposed += 1
            return correctlyProposed / (1.0*correct)

    def coarsefscore(self,standardWA,b=1,ignoreUntranslated=False):
        ''' Takes three arguments:
        Self, the standard WA file we are comparing against, and optionally
        a numeric value for how much more important recall is than precision.
        Returns the F score with many-to-many counting as one alignment.'''
        if ignoreUntranslated:
            p = self.coarsePrecision(standardWA,True)
            r = self.coarseRecall(standardWA,True)
        else:
            p = self.coarsePrecision(standardWA)
            r = self.coarseRecall(standardWA)
        return ((1 + pow(b,2))*p*r)/((p*pow(b,2))+r)

    def finefscore(self,standardWA,b=1,ignoreUntranslated=False):
        ''' Takes three arguments:
        Self, the standard WA file we are comparing against, and optionally
        a numeric value for how much more important recall is than precision.
        Returns the F score with many-to-many alignments split into
        one-to-one alignments for comparison.'''
        if ignoreUntranslated:
            p = self.finePrecision(standardWA,True)
            r = self.fineRecall(standardWA,True)
        else:
            p = self.finePrecision(standardWA)
            r = self.fineRecall(standardWA)
        return ((1 + pow(b,2))*p*r)/((p*pow(b,2))+r)

    def fineIntersection(self,otherWA):
        ''' Returns a new WA object with only the alignments in the 
        fine intersection.'''
        newWA = WordAlignment()
        for i in range(len(self.sentences)):
            newS = Sentence()
            newS.sTokens = self.sentences[i].sTokens
            newS.tTokens = self.sentences[i].tTokens
            intersec = self.sentences[i].fineIntersect(otherWA.sentences[i])
            newS.alignments = groupAlignments(intersec)
            newWA.sentences.append(newS)
        return newWA

    def reversed(self):
        ''' Returns a new WordAlignment with source and target swapped.'''
        newWA = WordAlignment()
        newWA.fileName = self.fileName
        newWA.path = self.path

        for s in self.sentences:
            newWA.sentences.append(s.reversed())

        return newWA

    def exportReversed(self):
        newWA = self.reversed()
        newWA.exportWA(self.path + "/" + self.fileName + ".reversed")

    def exportBerk(self,newName):
        berk = open(newName,'w')
        for s in self.sentences:
            aligns = s.getUngroupedAlignments()
            newline = ''
            for a in aligns:
                if a[0] != 0 and a[1] != 0:
                    newline = newline+ '%d-%d ' % (a[0]-1,a[1]-1)
            newline = newline+'\n'
            berk.write(newline)
        berk.close()

    def findDifferences(self,otherWA):
        '''Print out each fine alignment that does not occur in the intersection	of the files' alignments and indicate which file has the alignment.
	'''

	for i in range(len(self.sentences)): # deal with sentences
            fineSelf = self.sentences[i].getUngroupedAlignments()
            fineOther = otherWA.sentences[i].getUngroupedAlignments()
            union = self.sentences[i].fineUnion(otherWA.sentences[i])
            for tup in union:
                if tup in fineSelf:
                    if tup not in fineOther:
                        print '<<',tup,'  \t',
                        print "sentence in list at %s" % str(i)
                elif tup in fineOther: # in other, not in self
                    print '  ',tup,'>>\t',
                    print "sentence %s" % str(i)

    def importWASentence(self,s):
        '''Takes a list of strings, the WA file contents within <sentence> tags.
        Makes a sentence object, initializes it with WA info, 
        and appends it to the WA object.'''
        self.sentences.append( Sentence(s) )

    def initFromWA(self, waFile):
        toProcess = waFile.readlines()
        
        while toProcess != []:
            sent = toProcess[:toProcess.index("</sentence>\n")]
            self.importWASentence(sent)
            # Remove that sentence section from the part remaining
            toProcess = toProcess[toProcess.index("</sentence>\n")+3:]
        
    def initFromSentences(self, sentences):
        ''' Initialize a waFile with a list of sentences.'''
        self.sentences = sentences

    def appendWA(self, waFile):
        '''Append another WA file to the end of the current one.'''
        self.sentences = self.sentences + waFile.sentences

    def separateAfter(self, N):
        '''Argument: an integer N
        Make a separate WA file, leaving N sentences in the first.
        Returns self and the new wa file.'''
        newWA = WordAlignment()
        newWA.initFromSentences(self.sentences[N:])
        self.sentences = self.sentences[:N]
        return self, newWA

    def exportWA(self, path=None):
        if path is None:
            output = copen(self.path +'/'+self.fileName+ ".wa",'w')
        else:
            output = copen(path,'w')
        
        sentenceCount = 1
        for s in self.sentences:
            output.write('<sentence id="%s" status="%s">\n' %(sentenceCount,
                                                              s.status))
            output.write('// %s\n' % ' '.join(s.sTokens)) # source sentence
            output.write('// %s\n' % ' '.join(s.tTokens)) # translated sentence
            output.write('<source>\n')
            for i in range(len(s.sTokens)):
                output.write('%s %s : \n' %(i+1,s.sTokens[i]))
            output.write('</source>\n')
            output.write('<translation>\n')
            for i in range(len(s.tTokens)):
                output.write('%s %s : \n' %(i+1,s.tTokens[i]))
            output.write('</translation>\n<alignment>\n')
            output.writelines(s.formatAlignmentsLong())
            output.write('</alignment>\n</sentence>\n\n\n')
            sentenceCount += 1
        output.close()
    
    def exportEmpty(self,newName = None):
        if newName is None:
            output = copen(self.path +'/'+self.fileName+ ".wa.empty",'w')
        else:
            output = copen(newName,'w')
        
        sentenceCount = 1
        for s in self.sentences:
            output.write('<sentence id="%s" status="%s">\n' %(sentenceCount,
                                                              s.status))
            output.write('// %s\n' % ' '.join(s.sTokens)) # source sentence
            output.write('// %s\n' % ' '.join(s.tTokens)) # translated sentence
            output.write('<source>\n')
            for i in range(len(s.sTokens)):
                output.write('%s %s : \n' %(i+1,s.sTokens[i]))
            output.write('</source>\n')
            output.write('<translation>\n')
            for i in range(len(s.tTokens)):
                output.write('%s %s : \n' %(i+1,s.tTokens[i]))
            output.write('</translation>\n<alignment>\n')
            # We leave this empty.
            output.write('</alignment>\n</sentence>\n\n\n')
            sentenceCount += 1
        output.close()

    def exportReducedWA(self, maxLength):
        '''Parameters: maximum sentence length,                                 
        the source and translation extensions as strings.         
        Exports a WA without sentences that have more tokens than maximum.'''
        if self.path[-1] == '/':
            newWA = copen(self.path+self.fileName+'.reduced.wa','w')
        else:
            newWA = copen(self.path+'/'+self.fileName+'.reduced.wa','w')

        sentenceCount = 1
        for s in self.sentences:
            if len(s.sTokens) <= maxLength:
                newWA.write('<sentence id="%s" status="%s">\n' %(sentenceCount,
                                                              s.status))
                newWA.write('// %s\n' % ' '.join(s.sTokens)) # source sentence
                newWA.write('// %s\n' % ' '.join(s.tTokens)) # translated  
                newWA.write('<source>\n')
                for i in range(len(s.sTokens)):
                    newWA.write('%s %s : \n' %(i+1,s.sTokens[i]))
                newWA.write('</source>\n')
                newWA.write('<translation>\n')
                for i in range(len(s.tTokens)):
                    newWA.write('%s %s : \n' %(i+1,s.tTokens[i]))
                newWA.write('</translation>\n<alignment>\n')
                newWA.writelines(s.formatAlignmentsLong())
                newWA.write('</alignment>\n</sentence>\n\n\n')
                sentenceCount += 1
        newWA.close()


    def makeBerkeleyData(self, maxLength, sourceExt, transExt):
        '''Parameters: maximum sentence length, 
        the source and translation extensions as strings.
        Exports a Berkeley format alignment file without sentences that have 
        more tokens than maximum, and exports corresponding tokenized files.'''
        if self.path[-1] == '/':
            berk = copen(self.path+self.fileName+'.reduced.align','w')
            source = copen(self.path+self.fileName+'.reduced'+sourceExt,'w')
            trans = copen(self.path+self.fileName+'.reduced'+transExt,'w')    
        else:
            berk = copen(self.path+'/'+self.fileName+'.reduced.align','w')
            source = copen(self.path+'/'+self.fileName+'.reduced'+sourceExt,'w')
            trans = copen(self.path+'/'+self.fileName+'.reduced'+transExt,'w')  

        for s in self.sentences:
            if len(s.sTokens) <= maxLength:
                aligns = s.getUngroupedAlignments()
                newline = ''
                for a in aligns:
                    if a[0] != 0 and a[1] != 0:
                        newline = newline+ '%d-%d ' % (a[0]-1,a[1]-1)
                newline = newline+'\n'
                berk.write(newline)
                
                source.write(' '.join(s.sTokens)+'\n')
                trans.write(' '.join(s.tTokens)+'\n')
            else:
                print "Omitting sentence id=%d with length %d" \
                    % (self.sentences.index(s)+1, len(s.sTokens))
        berk.close()
        source.close()
        trans.close()
