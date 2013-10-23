import sys, os
import re
import argparse as ap
import math

parser = ap.ArgumentParser()
parser.add_argument('input', help='input file')
parser.add_argument('-o', '--out', help='output file')
parser.add_argument('--override', help='override input file', default=False)
args = parser.parse_args()

def getFileFormat(fileName):
	f = open(fileName)
	line = f.readline()
	if '\r\n' == line[-2:]:
		return "DOS"
	elif '\n' == line[-1]:
		return "UNIX"
	else:
		return "MAC"
		
def defaultScriptLang(scriptLang):
	if scriptLang:
		return scriptLang
	else:
		return "python" 
		
_LINE_SEP_DICT = {'DOS':'\r\n', 'UNIX':'\n', 'MAC':'\r'}
_COMMENT_MARKER_DICT = {'tex':'%', 'c':'//', 'cpp':'//', 'java':'//', 'python':'#'}


_FILE_NAME=args.input
_FILE_EXT=os.path.splitext(_FILE_NAME)[1][1:] # do not include '.'
_COMMENT_MARKER=_COMMENT_MARKER_DICT[_FILE_EXT]
_FILE_FORMAT=getFileFormat(_FILE_NAME)
_LINE_SEP=_LINE_SEP_DICT[_FILE_FORMAT]
print 'File name: ' + _FILE_NAME
print 'Comment marker: ' + _COMMENT_MARKER
print 'File format: ' + _FILE_FORMAT

_SCRIPT_START = re.compile(_COMMENT_MARKER + r"\s*scriptstart:?(\w*)")
_SCRIPT_END = re.compile(_COMMENT_MARKER + r"\s*scriptend")
_SCRIPT_MODE = False
_SCRIPT_LANG = None
_SCRIPT = [] # hold script content
_RV_START = _COMMENT_MARKER + "PDS start Python Document Script generated, Do !!NOT!! modify\n"
_RV_END = '\n' + _COMMENT_MARKER + "PDS end\n"
_RV = [] # return value of _SCRIPT
_DOC = [] # new document content

##############################
# LaTeX
# global options for use in script
floatopt=None
centering=None
width=None
caption=None
label=None
numfloatsperrow=None
subcaptions=None

def clearOptitions():
	global floatopt, centering, width, caption, label, numfloatsperrow, subcaptions
	floatopt=None
	centering=None
	width=None
	caption=None
	label=None
	numfloatsperrow=None
	subcaptions=None
	
def defaultOptions():
	global floatopt, centering, width, numfloatsperrow, subcaptions
	if floatopt==None: floatopt=r'ht'
	if centering==None: centering=True
	if numfloatsperrow==None: numfloatsperrow=1;
	if width==None: width=r'%.2f\linewidth' % (0.9/numfloatsperrow) # depend on numfloatsperrow
	if subcaptions==None: subcaptions=[""] # or [None]
	
def insertgraph(filename):
	defaultOptions()
	s = '\n\\begin{figure}[%s]\n' % floatopt
	if centering:
		s += '\\begin{centering}\n'
	s += '\\includegraphics[width=%s]{%s}\n' % (width, filename)
	if centering:
		s += '\\end{centering}\n'
	if caption:
		s += '\\caption{%s}\n' % caption
	if label:
		s += '\\label{%s}\n' % label
	s += '\\end{figure}\n'
	clearOptitions()
	return s
	
def insertgraphics(filenames):
	global numfloatsperrow
	if (numfloatsperrow == None):
		numfloatsperrow = math.ceil(math.sqrt(len(filenames)))
	defaultOptions()
	s = '\n\\begin{figure}[%s]\n' % floatopt
	if centering:
		s += '\\begin{centering}\n'
		
	while len(subcaptions) < len(filenames):
		subcaptions.append("")		
	for (i,filename) in enumerate(filenames):
		s += '\\subfloat[%s]{'  % subcaptions[i]
		s += '\\begin{centering}\n'
		s += '\\includegraphics[width=%s]{%s}\n' % (width, filename)
		s += '\\end{centering}\n}' 
		if (i+1) % numfloatsperrow == 0: # numer floats per row
			s += '\n\n'
		else:
			s += ' '
	
	if centering:
		s += '\\end{centering}\n'
	if caption:
		s += '\\caption{%s}\n' % caption
	if label:
		s += '\\label{%s}\n' % label
	s += '\\end{figure}\n'
	clearOptitions()
	return s

def inserttable(filename):
	defaultOptions()
	f = open(filename, 'U') # to Unix
	lines = f.readlines()
	f.close()
	r = len(lines)
	c = len(lines[0].split('\t'))
	s = '\n\\begin{table}[%s]\n' % floatopt
	if centering:
		s += '\\begin{center}\n'
	s += '\\begin{tabular}{' + 'c'*c + '}\n'
	s += '\\hline\n'
	for (i, line) in enumerate(lines):
		lines[i] = line.replace('\t', ' & ').replace('\n', ' \\\\\n')
	if r > 0:
		s += lines[0] + '\\hline\n' # header
	if r > 1:
		s += ''.join(lines[1:])
	s += '\\hline\n'	
	s += '\\end{tabular}\n'	
	if centering:
		s += '\\end{center}\n'
	if label:
		s += '\\label{%s}\n' % label
	if caption:
		s += '\\caption{%s}\n' % caption
	s += '\\end{table}\n'
	clearOptitions()
	return s
	
# end LaTeX
############################

# _SUBMODULE_NAME = 'pds_' + _FILE_EXT
# exec('from %s import *' % _SUBMODULE_NAME)

f = open(_FILE_NAME, 'U') # open as unix

lines = f.readlines();

for (i,line) in enumerate(lines):
	_DOC.append(line) # keep original code unchanged
	_LINE_NUMBER = i + 1
	if _SCRIPT_START.match(line) != None:
		m = _SCRIPT_START.match(line)
		if not _SCRIPT_MODE:
			_SCRIPT_MODE = True
			_SCRIPT_LANG = defaultScriptLang(m.group(1))
			_SCRIPT = [] # clear _SCRIPT when a new script block start
			_RV = [] # clear _RV
			
		else:
			raise Exception(_COMMENT_MARKER + "scriptend expected before line %d" % _LINE_NUMBER)
	elif _SCRIPT_END.match(line) != None:
		m = _SCRIPT_END.match(line)
		if _SCRIPT_MODE:
			_SCRIPT_MODE = False
			_SCRIPT_LANG = None
			# Process _SCRIPT and add _RV to _DOC
			print _SCRIPT
			exec(''.join(_SCRIPT)) # _SCRIPT should set _RV as return value
			if len(_RV) > 0:
				_DOC.append(_RV_START)
				_DOC.extend(_RV)
				_DOC.append(_RV_END)
		else:
			raise Exception(_COMMENT_MARKER + "scriptstart:<lang> expected before line %d" % _LINE_NUMBER)
	else:
		if _SCRIPT_MODE:
			if line.startswith(_COMMENT_MARKER*2) or \
				line.startswith(_COMMENT_MARKER + '#') or \
				not line.strip(): # '%%', '%#', or blank line
				pass
			elif line.startswith(_COMMENT_MARKER): # '%' scriptcode
				_SCRIPT.append(line[len(_COMMENT_MARKER):]) # delete %
			else:
				raise Exception("you must comment in script mode at line %d" % _LINE_NUMBER)
		else: # Not in scirpt mode
			pass

f.close()

if args.out:
	OUTPUT_FILE = args.out
elif args.override:
	OUTPUT_FILE = _FILE_NAME
else:
	(fn, ext) = os.path.splitext(_FILE_NAME)
	OUTPUT_FILE = fn+".pds"+ext

f = open(OUTPUT_FILE, 'w')
f.writelines(_DOC)
f.close()
