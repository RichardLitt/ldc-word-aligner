#!/usr/bin/python

'''
When called as a script, computes F-score in the specified method.
'''

from optparse import OptionParser
from WordAlignment import *

usage = "usage: %prog [options] FILE1 FILE2"
parser = OptionParser(usage=usage)
parser.add_option("-g", "--group-align", action="store_true",
                  dest="groupAlignments", default=False,
                  help="Treat many-to-many grouped alignments as units, rather than evaluating individual one-to-one alignment links.")
parser.add_option("-f","--fmeasure", dest="fmeasure", default="1",
                  help="Specify an F-measure weight N giving recall N times as much importance as precision. Default is 1, equal importance.")
parser.add_option("-i","--ignoreNT", action="store_true",
                  dest="ignoreNull", default=False,
                  help="Do not count not-translated links when comparing.")

def main():
    (options, args) = parser.parse_args()
    if len(args) != 2:
        parser.print_help()
    else:
        evalWA = WordAlignment(args[0])
        goldWA = WordAlignment(args[1]) # Gold standard alignment

        if len(evalWA.sentences) != len(goldWA.sentences):
            print "Uh oh! Files do not have the same number of sentences."
        elif options.ignoreNull:
            ''' For now the default behavior prints both fine and coarse.'''
            print "Fine precision is:", evalWA.finePrecision(goldWA,True)
            print "Fine recall is:", evalWA.fineRecall(goldWA,True)
            print "Fine F1 score is:", evalWA.finefscore(goldWA,1,True)
            print "Fine F2 score is:", evalWA.finefscore(goldWA,2,True)
            print "Fine F.5 score is:", evalWA.finefscore(goldWA,0.5,True)
            if options.fmeasure != "1":
                print "Fine F%s score is:" % (options.fmeasure),
                print evalWA.finefscore(goldWA,float(options.fmeasure),True)
            
            print "Coarse precision is:", evalWA.coarsePrecision(goldWA,True)
            print "Coarse recall is:", evalWA.coarseRecall(goldWA,True)
            print "Coarse F1 score is:", evalWA.coarsefscore(goldWA,1,True)
            print "Coarse F2 score is:", evalWA.coarsefscore(goldWA,2,True)
            print "Coarse F.5 score is:", evalWA.coarsefscore(goldWA,0.5,True)
            if options.fmeasure != "1":
                print "Coarse F%s score is:" % (options.fmeasure),
                print evalWA.coarsefscore(goldWA,float(options.fmeasure),True)
        else:
            ''' For now the default behavior prints both fine and coarse.'''
            print "Fine precision is:", evalWA.finePrecision(goldWA)
            print "Fine recall is:", evalWA.fineRecall(goldWA)
            print "Fine F1 score is:", evalWA.finefscore(goldWA,1)
            print "Fine F2 score is:", evalWA.finefscore(goldWA,2)
            print "Fine F.5 score is:", evalWA.finefscore(goldWA,0.5)
            if options.fmeasure != "1":
                print "Fine F%s score is:" % (options.fmeasure),
                print evalWA.finefscore(goldWA,float(options.fmeasure))
            
            print "Coarse precision is:", evalWA.coarsePrecision(goldWA)
            print "Coarse recall is:", evalWA.coarseRecall(goldWA)
            print "Coarse F1 score is:", evalWA.coarsefscore(goldWA,1)
            print "Coarse F2 score is:", evalWA.coarsefscore(goldWA,2)
            print "Coarse F.5 score is:", evalWA.coarsefscore(goldWA,0.5)
            if options.fmeasure != "1":
                print "Coarse F%s score is:" % (options.fmeasure),
                print evalWA.coarsefscore(goldWA,float(options.fmeasure))
            
            
main()
