import re

_SCRIPTSTART = re.compile(r"%\s*scriptstart:?(\w*)")
print _SCRIPTSTART.match("% scriptstart:python") != None
print _SCRIPTSTART.match("% scriptstart:python ab").group(1)
print _SCRIPTSTART.match("% scriptstart").group(1) == ""
print _SCRIPTSTART.match("% script") # None
# print _SCRIPTSTART.match("% script").group(1) #AttributeError

_SCRIPTEND = re.compile(r"%\s*scriptend")
print _SCRIPTEND.match(r"%scriptend:python") != None
