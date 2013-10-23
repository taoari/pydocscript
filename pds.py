import sys, os
import re
import numpy as np
import argparse as ap

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

_FILE_NAME=args.input		
_FILE_FORMAT=getFileFormat(_FILE_NAME)

_SCRIPT_START = re.compile(r"%\s*scriptstart:?(\w*)")
_SCRIPT_END = re.compile(r"%\s*scriptend")
_SCRIPT_MODE = False
_SCRIPT_LANG = None
_SCRIPT = [] # hold script content
_RV_START = "%%PDS start Python Document Script generated, Do !!NOT!! modify\n"
_RV_END = "\n%%PDS end\n"
_RV = [] # return value of _SCRIPT
_DOC = [] # new document content

# global options for use in script
floatopt=None
centering=None
width=None
caption=None
label=None

def clearOptitions():
	global floatopt, centering, width, caption, label
	floatopt=None
	centering=None
	width=None
	caption=None
	label=None
	
def defaultOptions():
	global floatopt, centering, width
	if floatopt==None: 
		floatopt=r'htpb'
	if centering==None: 
		centering=True
	if width==None: 
		width=r'\linewidth'
	
def insertgraph(filename):
	defaultOptions()
	s = '\n\\begin{figure}[%s]\n' % floatopt
	if centering:
		s += '\\centering\n'
	s += '\\includegraphics[width=%s]{%s}\n' % (width, filename)
	if label:
		s += '\\label{%s}\n' % label
	if caption:
		s += '\\caption{%s}\n' % caption
	s += '\\end{figure}\n'
	_RV.append(s)
	clearOptitions()

def inserttable(filename):
	defaultOptions()
	f = open(filename, 'U') # to Unix
	lines = f.readlines()
	f.close()
	r = len(lines)
	c = len(lines[0].split('\t'))
	s = '\n\\begin{table}[%s]\n' % floatopt
	if centering:
		s += '\\centering\n'
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
	if label:
		s += '\\label{%s}\n' % label
	if caption:
		s += '\\caption{%s}\n' % caption
	s += '\\end{table}\n'
	_RV.append(s)
	clearOptitions()
	
#def inserttable(filename):
	#defaultOptions()
	#t = np.genfromtxt(filename)
	#(r,c) = t.shape
	#s = '\n\\begin{table}[%s]\n' % floatopt
	#if centering:
		#s += '\\centering\n'
	#s += '\\begin{tabular}{' + 'c'*c + '}\n'
	#s += '\\hline\n'
	#data = []
	#for tr in t: # tr: table row
		#data.append(' & '.join(str(tr)[1:-1].split()) + r'\\' + '\n')
	#if r > 0:
		#s += data[0] + '\\hline\n' # header
	#if r > 1:
		#s += ''.join(data[1:])
	#s += '\\hline\n'	
	#s += '\\end{tabular}\n'	
	#if label:
		#s += '\\label{%s}\n' % label
	#if caption:
		#s += '\\caption{%s}\n' % caption
	#s += '\\end{table}\n'
	#_RV.append(s)
	#clearOptitions()
	
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
			# print line
			
		else:
			raise Exception("%%scriptend expected before line " % _LINE_NUMBER)
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
			raise Exception("%%scriptstart:<lang> expected before line %d" % _LINE_NUMBER)
	else:
		if _SCRIPT_MODE:
			if line.startswith("%%"):
				pass
			elif line.startswith("%"):
				_SCRIPT.append(line[1:]) # delete %
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

