#File: makeFileBuilder.py

#Author: Adar Guy
#contact: adarguy10@gmail.com


import sys
import os
import os.path
import re

AdDepList = []

def parser(srcfile):
	Hfile = ''
	line = srcfile.readline()
	if not line.strip() or re.search('^//',line):
		return '1'
	elif re.search('^/[*]',line):
		while True:
			if '*/' in line:
				break
			line = srcfile.readline()
		return '1'
	elif re.search('^#include\s+',line):
		if re.search('^#include\s+".*[.h]"$',line):
			parsed = re.findall('"([^"]*)"', line)
			Hfile = parsed[0]			
			return Hfile
		else:
			return '1'
	else:
		return 'b'

def complications(ADlist, Hfile, index, fname):
	sources = files()
	SRCS = sources[2]
	filesD = sources[4]
	if Hfile not in filesD:
		print('Error: '+fname+': contains #include for missing file '+Hfile)
	else:
		ADlist = ADlist + AdditionalDependencies(Hfile, index)	
	return ADlist

def AdditionalDependencies(fname, index):
	ADlist = []
	global AdDepList
	if fname not in AdDepList:
		AdDepList.append(fname)
	else:
		return ADlist	
	if os.path.isfile(fname):
		try:
			srcfile = open(fname, 'r')
			Hfile = ''	
			while True:
				parsed = parser(srcfile)
				if '1' in parsed:
					pass
				elif re.search('.h',parsed):
					Hfile = parsed
					ADlist.append(Hfile)
					ADlist = complications(ADlist, Hfile, index, fname)
				else:
					break
			srcfile.close()			
			return ADlist
		except:
			reason = sys.exc_info()
			print('Error: ', reason[1])
	else:
		if not fname:
			return ADlist
		print('Error: File Path not found for '+fname)
		
def files():
	SRCS = []
	OBJS = []
	Sline = 'SRCS = '
	Oline = 'OBJS = '
	filesD = []
	Oindex=0
	for fl in os.listdir():
		filesD.append(fl)
		if re.search('(.c|.C|.cc|.cpp)$',fl):
			SRCS.append(fl)
			OBJS.append(re.sub('(.c|.C|.cc|.cpp)$','.o',fl))
			Sline = Sline + fl + ' '
			Oline = Oline + OBJS[Oindex] + ' '
			Oindex = Oindex+1
	files = [Sline,Oline, SRCS, OBJS, filesD]
	return files

def rules(SRCS, OBJS):
	index=0
	RULES = ''
	for src in SRCS:
		ADline = ''
		ADline2 = ''
		global AdDepList
		AdDepList = []
		seen = set()
		ADlist = AdditionalDependencies(SRCS[index], index)
		try:	
			for AD in ADlist:
				if AD not in seen:
					ADline = ADline+' '+AD
					seen.add(AD)
		except:
			pass
		RULES = (RULES+'\n'+OBJS[index]+': '+src+ADline+'\n')
		if re.search('(.C|.cc|.cpp)$',src):
			RULES = RULES+'\t$(CXX) $(CPPFLAGS) $(CXXFLAGS) -c '+src+'\n'
		elif re.search('(.c)$',src):
			RULES = RULES+'\t$(CC) $(CPPFLAGS) $(CFLAGS) -c '+src+'\n'
		index=index+1
	return RULES

def program():
	PROG = ('\nPROG = prog.exe\n'+'\n$(PROG): '+'$(OBJS)\n'+'\t$(CC) $(LDFLAGS) $(OBJS) $(LDLIBS) -o $(PROG)\n')
	return PROG

def clean():
	CLEAN = '\nclean:\n\trm -f $(OBJS)'
	return CLEAN

def main():
	try:
		folderpath = sys.argv[1]
		os.chdir(folderpath)
	except:
		pass
	srcANDobj = files()
	Makefile = open('Makefile', 'w+')
	Makefile.write(srcANDobj[0]+'\n')
	Makefile.write('\n'+srcANDobj[1]+'\n')
	Makefile.write(program())
	Makefile.write(rules(srcANDobj[2], srcANDobj[3]))
	Makefile.write(clean())
	Makefile.close()

if __name__ == '__main__':
	main()