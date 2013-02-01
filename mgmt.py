#!/usr/bin/python
"""Manage the Google doc interface."""
# Filename: mgmt.py
import gspread

DOCUMENT = gspread.login("agavechat@gmail.com", "agav3chat").open("agavelist")
WORKSHEET = DOCUMENT.get_worksheet(0)
GLOBAL_LIST = WORKSHEET.col_values(1)  # IPs and nicknames from the Google doc

def initialize(myIP):
	"""Get my row and return my nickname and agavebot's replies."""
	global MY_ROW, MY_IP
	
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
	update = (len(newNick) > 0)
	if update:
		WORKSHEET.update_cell(MY_ROW, 2, newNick)
	return update

def getGlobalList():
	"""Return the IP list from Google docs."""
	return GLOBAL_LIST
