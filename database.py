#!/usr/bin/python
"""Manage the Google doc interface."""
# Filename: database.py
import gspread

DOCUMENT = gspread.login("agavechat@gmail.com", "agav3chat").open("agavelist")
WORKSHEET = DOCUMENT.get_worksheet(0)

def initialize(myIP):
	"""Get my row and return my nickname and agavebot's replies."""
	global GLOBAL_LIST, MY_ROW, MY_IP
	
	GLOBAL_LIST = WORKSHEET.col_values(1)	# GetIPs and nicknames from the Google doc
	
	MY_IP = myIP
	
	if myIP in GLOBAL_LIST:
		MY_ROW = GLOBAL_LIST.index(myIP) + 1
		myNick = WORKSHEET.cell(MY_ROW, 2).value
	else:
		MY_ROW = len(GLOBAL_LIST) + 1
		WORKSHEET.update_cell(MY_ROW, 1, myIP)
		myNick = None
	
	botReplies = DOCUMENT.get_worksheet(1).col_values(1)
	
	return myNick, botReplies

def setNick(newNick):
	"""Update Google doc with my new nickname."""
	# Note: newNick must be longer than 2 chars
	WORKSHEET.update_cell(MY_ROW, 2, newNick)

def getGlobalList():
	"""Return the IP list from Google docs."""
	return GLOBAL_LIST
