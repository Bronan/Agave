#!/usr/bin/python
"""Handles user interface using the curses method."""
# Filename: ui.py
import curses, math

# Initialize
CONSOLE = curses.initscr()	# Creates curses handle for IO
prevInputRows = 1			# number of rows the user has dedicated for input

CONSOLE.scrollok(1)			# Turn on scrolling
CONSOLE.keypad(1)			# Allow entry from the keypad
CONSOLE.timeout(600000)		# wait 600000 ms before entering sleep mode
curses.noecho()				# Turn off character echo
numRows, numCols = CONSOLE.getmaxyx()
CONSOLE.move(numRows-1, 0)	# Position cursor

INDENT_SIZE = 5				# Store number of spaces to use for indentation
inInsertMode = True			# Track if the text entry is in insert or replace mode
inIDU = False				# Use for printing
# Constants
# For use with scrolling
PAGEUP = 339
PAGEDOWN = 338
SHIFTHOME = 388
SHIFTEND = 384

def writeToConsole(msg):
	"""Write the message to the console while leaving the user input section alone."""
	if type(msg) == type([]):
		for entry in msg:
			printMsg(entry)
	else:
		printMsg(msg)

def printMsg(msg):
	"""Prints one message to the console."""
	msg = str(msg)
	
	# Where am I?
	rowNum, colNum = CONSOLE.getyx()
	numRows, numCols = CONSOLE.getmaxyx()
	if inIDU:
		printLine = numRows-prevInputRows
	else:
		printLine = numRows-prevInputRows - 1
	
	# Write each line
	for line in msg.splitlines():
		line, lineRows = msgLength(line)
		
		# insert the message
		CONSOLE.move(printLine-lineRows, 0)
		CONSOLE.scroll(lineRows)
		insertnln(lineRows)
		CONSOLE.addstr(printLine-lineRows, 0, line)
	
	# Restore the cursor position
	CONSOLE.move(rowNum, colNum)
	CONSOLE.refresh()

def msgLength(msg):
	"""Determine the number of rows needed for printing and return the number of rows and the formatted message."""
	# Size of console
	numRows, numCols = CONSOLE.getmaxyx()
	
	# Format
	msg = hangingIndent(msg, numCols)
	
	# Determine number of rows
	lineRows = int(math.ceil(float(len(msg))/numCols))
	if lineRows == 0:
		lineRows = 1
	
	# Return
	return msg, lineRows

def setInIDU(newInIDU):
	global inIDU
	inIDU = newInIDU

def hangingIndent(msg, numCols):
	"""Return msg formatted for hanging indentation."""
	insertPoint = numCols
	while insertPoint < len(msg):
		msg = msg[:insertPoint] + "".center(INDENT_SIZE) + msg[insertPoint:]
		insertPoint += numCols
	
	return msg

def insertnln(n=1):
	"""Insert n blank lines below the cursor."""
	idx = 0
	while idx < n:
		CONSOLE.insertln()
		idx = idx + 1

def getUserMsg(prompt, sleepEn=True, pwd=False, log=True, prevInput=None):
	"""Read the user's input and reset for new input"""
	global inInsertMode, prevInputRows, inScrollMode
	
	numRows, numCols = CONSOLE.getmaxyx()	# Get console size
	cursorPosition = 0						# Store position in msg
	
	if prevInput == None:
		msg = ""
	else:
		msg = prevInput
	
	lastChar = ""
	while lastChar != "\n":
		if pwd:
			msgFormatted = hangingIndent(prompt, numCols)
		else:
			msgFormatted = hangingIndent(prompt + msg, numCols)
		
		# Determine number of rows dedicated for input
		inputRows = int(math.ceil((len(msgFormatted)+1.0)/numCols))			# 1 is for next char
		# Catch where cursor is first char on next line
		if inputRows != int(math.ceil((len(msgFormatted)+0.0)/numCols)):	# .0 is for floating point
			msgFormatted += "".center(INDENT_SIZE)
		
		# Scroll prompt to the correct position
		if prevInputRows != inputRows:
			CONSOLE.scroll(inputRows-prevInputRows)
			prevInputRows = inputRows
		
		# Find cursor position
		if pwd:
			cursorRow, cursorCol = divmod(len(prompt)-INDENT_SIZE, numCols-INDENT_SIZE)
			if len(prompt) < INDENT_SIZE:
				cursorRow += 1
				cursorCol -= numCols-INDENT_SIZE
		else:
			cursorRow, cursorCol = divmod(cursorPosition+len(prompt)-INDENT_SIZE, numCols-INDENT_SIZE)
			if cursorPosition + len(prompt) < INDENT_SIZE:
				cursorRow += 1
				cursorCol -= numCols
		cursorCol += INDENT_SIZE
		
		# Print the current message and get the next char
		CONSOLE.addstr(numRows-inputRows, 0, msgFormatted)
		CONSOLE.clrtobot()
		char = CONSOLE.getch(numRows-inputRows+cursorRow, cursorCol)
		
		# Update sleep mode
		if (char == -1) and sleepEn:
			return [msg]
		
		# Fix numpad input
		if char == 458:			#Numpad /
			char = ord("/")
		elif char == 459:		#Numpad enter
			char = ord("\n")
		elif char == 463:		#Numpad *
			char = ord("*")
		elif char == 464:		#Numpad -
			char = ord("-")
		elif char == 465:		#Numpad +
			char = ord("+")
		
		if char == ord("\b"):	#Backspace
			if cursorPosition > 0:
				msg = msg[:cursorPosition-1] + msg[cursorPosition:]
				cursorPosition -= 1
		elif char == 330:		#Delete
			if cursorPosition < len(msg):
				msg = msg[:cursorPosition] + msg[cursorPosition+1:]
		elif char == 381:		#Shift Delete
			cursorPosition = 0
			msg = ""
		# Handle cursor movement
		elif char == 260:		#Left
			if cursorPosition > 0:
				cursorPosition -= 1
		elif char == 261:		#Right
			if cursorPosition < len(msg):
				cursorPosition += 1
		elif char == 258:		#Down
			cursorPosition += numCols - INDENT_SIZE
			if cursorPosition > len(msg):
				cursorPosition = len(msg)
		elif char == 259:		#Up
			cursorPosition -= numCols - INDENT_SIZE
			if cursorPosition < 0:
				cursorPosition = 0
		elif char == 262:		#Home
			cursorPosition -= (cursorPosition+len(prompt)-INDENT_SIZE) % (numCols-INDENT_SIZE)
			if cursorPosition < 0:
				cursorPosition = 0
		elif char == 358:		#End
			cursorPosition += numCols-INDENT_SIZE-((cursorPosition+len(prompt)-INDENT_SIZE) % (numCols-INDENT_SIZE))-1
			if cursorPosition > len(msg):
				cursorPosition = len(msg)
		# Handle autocomplete:
		elif char == ord("\t"):	#Tab
			pass
		#elif char == 351:		#Shift Tab
		# Handle scrolling
		elif char == 338:		#Page Down
			inScrollMode = True
		elif char == 339:		#Page Up
			inScrollMode = True
		elif char == 388:		#Shift Home
			inScrollMode = True
		elif char == 384:		#Shift End
			inScrollMode = False
		# Handle insert
		elif char == 331:		#Insert
			inInsertMode = not inInsertMode
		elif char == 389:		#Shift Insert
			inInsertMode = True
		# F-Keys
		#elif (char > 264) and (char < 277): #F-keys
		#elif (char > 276) and (char < 289): #Shift F-keys
		# Non-printable ascii chars
		elif char == 27:		#Esc
			pass
		# Process ascii chars
		elif (char < 256) and (char > 0):
			lastChar = chr(char)
			if lastChar != "\n":
				if inInsertMode:
					msg = msg[:cursorPosition] + lastChar + msg[cursorPosition:]
				else:
					if cursorPosition < len(msg):
						msg = msg[:cursorPosition] + lastChar + msg[cursorPosition+1:]
					else:
						msg += lastChar
				cursorPosition += 1
	
	# Print user input to display area and clear entry area
	if pwd:
		printMsg(prompt)
	else:
		printMsg(prompt + msg)
	CONSOLE.scroll(-1*(prevInputRows))
	prevInputRows = 0
	
	# Return fetched message
	return msg

def clear():
	"""Clear the screen."""
	CONSOLE.clear()
	CONSOLE.clearok(1)
	CONSOLE.refresh()
	numRows, numCols = CONSOLE.getmaxyx()
	CONSOLE.move(numRows-1, 0)	# Position cursor

def getCols():
	rows, cols = CONSOLE.getmaxyx()
	return cols
