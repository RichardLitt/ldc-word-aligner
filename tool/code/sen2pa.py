#!/ldc/bin/python2.6
# sen2pa.py
"""A stand-alone module used only for creating new projects. It can be run
from the command line, and as a result shares no state with the rest of
the aligner modules.
"""

import sys,re,getopt

def usage():
	print 'Usage: sen2pa.py'
	print '-h\n\tHelp'
	print '-s <path/filename.tkn>\n\tSource Token File'
	print '-t <path/filename.tkn>\n\tTranslation Token File'
	print '-w <path/filename.wa>\n\tOutput Word Align File'
	print '\nOptional:'
	print '-r <path/filename.raw>\n\tSource Raw File'
	print '-q <path/filename.raw>\n\tTranslation Raw File'
	print '-c\n\tUse Comments'
	print '\nLong options not implemented in this script\n'


def main(argv):
	
	try:
		opts, args = getopt.getopt(argv, "hs:t:w:r:q:c")
	except GetoptError, err:
		print str(err)
		usage()
		sys.exit(2)
	
	sourceTkn = None
	transTkn = None
	outputWa = None
	sourceRaw = None
	transRaw = None
	useComments = False
	
	for opt, arg in opts:
		if opt == '-h':
			usage()
			sys.exit()
		elif opt == '-s':
			sourceTkn = arg
		elif opt == '-t':
			transTkn = arg
		elif opt == '-w':
			outputWa = arg
		elif opt == '-r':
			sourceRaw = arg
		elif opt == '-q':
			transRaw = arg
		elif opt == '-c':
			useComments = True

	if sourceTkn == None or transTkn == None or outputWa == None:
		print 'need to define s,t,w'
		usage()
		sys.exit(2)

	try:
		st = open(sourceTkn, 'r')
		tt = open(transTkn, 'r')
		wa = open(outputWa, 'w')
		if sourceRaw != None:
			sr = open(sourceRaw, 'r')
		if transRaw != None:
			tr = open(transRaw, 'r')
	except err:
		print 'Some invalid filename',err
	
	numSents = 0
	for line in st:
		numSents += 1
	# Check all files have equal lines
	def check(fp):
		count = 0
		for line in fp:
			count += 1
		assert numSents == count, "Files don't have equal lines"
		fp.seek(0)
	check(tt)
	if sourceRaw:
		check(sr)
	if transRaw:
		check(tr)
	st.seek(0)
	
# CHANGE HERE
	
	for x in range(numSents):
		sent = x+1
		
		head = '<sentence id="'+str(sent)+'" status="">'
		wa.write( head + '\n')
		
		stline = st.readline().strip()
		wa.write( '// ' + stline + '\n')
		stokens = re.split(' ',stline)
	
		ttline = tt.readline().strip()
		wa.write( '// ' + ttline + '\n')
		ttokens = re.split(' ',ttline)
		
		if sourceRaw != None:
			srline = sr.readline().strip()
			wa.write( '## ' + srline + '\n')
		else:
			wa.write('##' + '\n')
			
		if transRaw != None:
			trline = tr.readline().strip()
			wa.write( '## ' + trline + '\n')
		else:
			wa.write('##' + '\n')
			
		wa.write( '<source>\n')
		for y in range(len(stokens)):
			wa.write( str(y+1) + ' ' + stokens[y] + ' : \n')
		wa.write( '</source>\n')
		
		wa.write( '<translation>\n')
		for y in range(len(ttokens)):
			wa.write( str(y+1) + ' ' + ttokens[y] + ' : \n')
		wa.write( '</translation>\n')
		
		wa.write( '<alignment>\n')
		# new WA file, so nothing goes here
		wa.write( '</alignment>\n')

		if useComments:
			wa.write( 'Comment: \n')
		
		wa.write( '</sentence>\n\n\n')

	wa.flush()
	wa.close()
if __name__ == '__main__':
	main(sys.argv[1:])
