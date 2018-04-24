#!/usr/bin/env python2.6
# -*- coding: utf-8 -*-
# alignerAR.#VERSION#.py

from mainform import *

def helpMsg():
	"""Help message that is printed when -h is used"""
	print "Usage: Command line flags:"
	print "-h --help\n\tDisplays usage information"
        print "\nSpecify language mode (Default is none):"
        print "-l --language-mode [AR | Arabic] [CH | Chinese] [DE | Default]"
	print "\nFor basic input, use one\n"
	print "-f --file-wa <filename>\n\tSpecify .wa input file"
	print "\nFor complex input, must use [-s, -t, and -w]\n"
	print "-s --source-token <filename>\n\tSpecify source token input file"
	print "-t --trans-token <filename>\n\tSpecify translation token input file"
	print "-r --source-raw <filename>\n\tSpecify source raw input file"
	print "-q --trans-raw <filename>\n\tSpecify translation raw input file"
	print "-w --wa-out <filename>\n\tSpecify .wa output file"
	print "\nFor loading a specific sentence on startup:\n"
	print "-i --index-start\n\tSpecify index of initial displayed sentence"
        print "-a --alignment-highlight\n\tSpecify alignment to highlight in sentence. \
        \n\tMust be used with -i"


class Usage(Exception):
    """Used to trap all exceptions in one place and provide a single error exit point for main."""
    def __init__(self, msg):
        self.msg = msg


def main():
    # Vars
    paFilename = None
    fileWa = None
    sourceTok = None
    transTok = None
    sourceRaw = None
    transRaw = None
    waOut = None
    # User input vars
    indexStart = 0
    highlightAlignment = 0
    no_file = False # File dialog boolean
    language_mode = None

    try:
        # parse command line
        try:
            opts, args = getopt.getopt(sys.argv[1:], "hf:s:t:r:q:w:i:a:l:",
                                       ["help","file-wa=","source-token=",
                                        "trans-token=","source-raw=",
                                        "trans-raw=","wa-out=","index-start=",
                                        "alignment-highlight=", "language-mode="])
        except getopt.GetoptError, msg:
            raise Usage(msg)

        try:
            # process command line arguments
            opts_p = [o[0] for o in opts]
            complex_opts = ['-s', '-t', '-r', '-q', '-w',
                            '--source-token', '--trans-token', '--source-raw',
                            '--trans-raw', '--wa-out']
            for opt, arg in opts:
                if opt in ("-h","--help"):
                    helpMsg()
                    return 0
                elif opt in ("-f","--file-wa"):
                    fileWa = arg
                    for x in complex_opts:
                        assert x not in opts_p, "Invalid arguments"
                    assert os.path.isfile(fileWa), fileWa + " doesn't exist"
                elif opt in ("-s","--source-token"):
                    sourceTok = arg
                    assert os.path.isfile(sourceTok), sourceTok + " doesn't exist"
                elif opt in ("-t","--trans-token"):
                    transTok = arg
                    assert os.path.isfile(transTok), transTok + " doesn't exist"
                elif opt in ("-r","--source-raw"):
                    sourceRaw = arg
                    assert os.path.isfile(sourceRaw), sourceRaw + " doesn't exist"
                elif opt in ("-q","--trans-raw"):
                    transRaw = arg
                    assert os.path.isfile(transRaw), transRaw + " doesn't exist"
                elif opt in ("-w","--wa-out"):
                    waOut = arg
                elif opt in ("-i","--index-start"):
                    indexStart = int(arg)
                    assert indexStart > 0, "Invalid sentence number"
                elif opt in ('-a', '--alignment-highlight'):
                    assert '-i' in opts_p or '--alignment-highlight' in \
                           opts_p, "-a can only be used with -i"
		    if arg[0] in ('s', 't'):
			    highlightAlignment = (arg[0], int(arg[1:]))
		    else:
			    highlightAlignment = ('s', int(arg))
                    assert highlightAlignment[1] > 0, str(highlightAlignment[1]) + ": Invalid alignment number"
                elif opt in ('-l', '--language-mode'):
                    if arg in ('AR', 'Arabic', 'arabic'):
                        language_mode = AR
                    elif arg in ('CH', 'Chinese', 'chinese'):
                        language_mode = CH
		    elif arg in ('DE', 'Default', 'DEFAULT', 'default'):
			language_mode = DEFAULT
		    else:
			raise Usage("Invalid language selected")
                else:
                    print opt,arg
            ## assert '-l' in opts_p or \
            ##        '--language-mode' in opts_p or \
            ##        len(opts) == 0, "Must specify language"
            for x in ('-s', '-t', '-w'):
                if x in opts_p:
                    assert '-s' in opts_p and \
                           '-t' in opts_p and \
                           '-w' in opts_p and \
                           '-f' not in opts_p and \
                           '--file-wa' not in opts_p, "Invalid arguments: Must provide " \
                           "mandatory complex arguments"
        except AssertionError, msg:
		raise Usage(msg)

        # Decide which files to open
        if fileWa != None:
		paFilename = fileWa
        elif sourceTok != None and transTok != None and waOut != None:
		try:
			createWAFile(sourceTok, transTok, waOut, sourceRaw, transRaw)
		except AssertionError, e:
			raise Usage(e)
		paFilename = waOut

        app = QApplication(sys.argv)
        rect = QApplication.desktop().availableGeometry()

        ### File Handling ##########
        # emish: Open file dialog if cmdline was not used
        if not paFilename:
            # New or open dialog
	    x = StartupDialog(language_mode)
            if x.exec_():
		if not language_mode:
			paFilename, language_mode = x.getInfo()
		else:
			paFilename, dummy = x.getInfo()
            else:
                sys.exit(0)

	if not language_mode:
		language_mode = DEFAULT
	print language_mode
        form = MainForm(paFilename, indexStart, highlightAlignment, language_mode)
        form.resize(int(rect.width()), int(rect.height()))
        form.show()
        app.exec_()

    except Usage, err:
        print >>sys.stderr, err.msg
        print >>sys.stderr, "for help use --help"
        return 2
    
    return 0

if __name__ == "__main__":
    sys.exit(main())

