#!/usr/bin/env python

import sys
import re
import os

# array to store dict of commit data
commits = []
fileMap = {"M": [], "A": [], "D": []}
messages = []


def prepareFileMessage(fileMap):

	finalMessage = ""

	for status in fileMap.keys():

		if len(fileMap[status]) < 1:
			continue
		
		if status == "M":
			finalMessage += "* *Files Modified:* \n"
		elif status == "D":
			finalMessage += "* *Files Deleted:* \n"
		elif status == "A":
			finalMessage += "* *Files Added:* \n"
		
		finalMessage += "\n".join(fileMap[status]) + "\n\n"

	
	if len(finalMessage) > 0:
		finalMessage = "Following files were modified for this: \n" + finalMessage
	return finalMessage



def parseFileList(fileList):

	files = fileList.splitlines()

	for f in files:
		status = f[0]
		fileName = f[1::].strip()
		
		if status in fileMap and fileName not in fileMap[status]:
			fileMap[status].append(fileName)




def parseCommit(commitLines):
	# dict to store commit data
	commit = {}
	# iterate lines and save
	for nextLine in commitLines:
		if nextLine == '' or nextLine == '\n':
			# ignore empty lines
			pass
		elif bool(re.match('commit', nextLine, re.IGNORECASE)):
			# commit xxxx
			if len(commit) != 0:		## new commit, so re-initialize
				commits.append(commit)
				commit = {}
			commit = {'hash' : re.match('commit (.*)', nextLine, re.IGNORECASE).group(1) }
		elif bool(re.match('merge:', nextLine, re.IGNORECASE)):
			# Merge: xxxx xxxx
			pass
		elif bool(re.match('author:', nextLine, re.IGNORECASE)):
			# Author: xxxx <xxxx@xxxx.com>
			m = re.compile('Author: (.*) <(.*)>').match(nextLine)
			commit['author'] = m.group(1)
			commit['email'] = m.group(2)
		elif bool(re.match('date:', nextLine, re.IGNORECASE)):
			# Date: xxx
			pass
		elif bool(re.match('    ', nextLine, re.IGNORECASE)):
			# (4 empty spaces)
			if commit.get('message') is None:
				commit['message'] = nextLine.strip()
		else:
			print ('ERROR: Unexpected Line: ' + nextLine)

if __name__ == '__main__':
	parseCommit(sys.stdin.readlines())

	# print commits
	for commit in commits:
		hash = commit['hash']
		changed_files = os.popen("git diff-tree --no-commit-id --name-status -r " + hash).read()
		messages.insert(0, commit['message'])
		parseFileList(changed_files)

	print("# " + ("\n# ".join(messages)) + "\n\n" + prepareFileMessage(fileMap))
