#!/usr/bin/python
"""Run Agave."""
# Filename: agave.py
import opsys, etc, mgmt, traffic, ui	# opsys needs to be imported first.
from thread import start_new_thread

# constants
VERSION = """2.19NS2"""
VERSION_HISTORY = """
Last Author:
	Chris
Changes: 
   	v1.10
   	Added read/write global list
   	Added import global list to peers dictionary
	
	v1.11
	moved methods to modules
	
	v2.1 Brent
	updated modules
	
	v2.6 Brent
	escaped non commands with $
	made copy of heartbeat keys for heartbeat delete dead peers for loop
	
	v2.7 Brent
	make agavebot send to all users and print message on agavebot's screen
	
	v2.8 Brent
	Fix screen clear
	
	v2.9 Brent
	Add $kick
	
	v2.11 Brent
	Change string testing to str.startswith()
	Add encryption
	
	v2.12 Brent
	Made agave more modular
	
	v2.13 Brent
	Added boss mode
	Added notifications when messages are received.
	
	v2.14 Brent
	Deleted agave.alert()
	Fixed nickname updating
	Made notifications only popup when the main window isnt agave
	Made notification clickable
	Made notifications not make extra icons - Believed fixed. Could not reliably replicate.
	
	v2.15
	Send heartbeat when peer added
	Added blank line above entry line
	Fixed extra lines from newline char in welcome caused by previous fix
	Fixed receive input inserting/overwriting multiline unsent messages
	Fixed scrolling dropping lines of unsent text
	Made messages use hanging indentation
	
	v2.16
	Made sure that clicking the balloon brings the main window to front even if minimized
	
	v2.17
	Add away/sleep mode (and adjust input method)
	Change window title when in boss or sleep mode
	Add "X is now in boss mode" for all modes
	
	v2.18
	Fixed away/sleep mode to save messages while away
	Extended sleeptimer to 10 mins
	
	v2.19
	Allow cursor to move through message.
	Added insert/replace toggling with insert button.
	Log messages
	Change join text to not include IP if nick is provided
	Make leaving IDU mode print all logged messages
	Fix cursor on IDUmode
	
	NO SLEEP BRANCH
	
	v2.19NS
	Removed sleep timer
	
	v2.19NS2
	Added sleep timer back in.
	Set sleep timer to 8 hours
	
	v2.19NS3
	Added agave as login to IDU
	
	To do: Change version number when change version moves above this line.
	v2.20+
	Implement scrolling
	Implement autocomplete
	Implement word wrap (instead of just line wrap)
	Add mode display in $whos
	Add timestamp option
	Make sleep optional and time adjustable
	Allow choice between IDU and FPGA-Build Boss modes
	Reject input that starts with the command char but isn't a command
	Clean up opsys (understand all of the windows calls)
	Add private messaging
	Allow change of command char?
	Auto-update?
"""

# Globals
BOSS_NUM = 5
msgLog = []
inBossMode = False
inSleepMode = False
inScrollMode = False
TITLE = "Agave v" + VERSION

def runThread(function):
	"""This runs any function in an infinite while loop and prints the return string."""
	while True:
		printList = function()
		if len(printList) != 0:
			msgLog.extend(printList)
			if inSleepMode:
				opsys.alert("Please update Agave.")
			elif inScrollMode:
				opsys.alert(printList)
			elif not inBossMode:
				ui.writeToConsole(printList)
				opsys.alert(printList)

def bossMode():
	"""Handles user interface while in boss mode."""
	global inBossMode
	inBossMode = True
	opsys.closePopup()
	traffic.sendText("entered BOSS mode.")
	emulateIDU()
	traffic.sendText("left BOSS mode.")
	inBossMode = False
	opsys.resumePopup()

def emulateIDU():
	"""Emulate an IDU"""
	ui.clear()
	ui.setInIDU(True)
	ui.writeToConsole(etc.IDU_TEXT)
	opsys.setTitleText("COM5:38400baud - Tera Term VT")
	
	ui.getUserMsg("", sleepEn=False, pwd=True, log=False)
	getUser = True
	while getUser:
		username = ""
		while username == "":
			username = ui.getUserMsg("SDIDU login: ", sleepEn=False, log=False)
		password = ui.getUserMsg("Password: ", sleepEn=False, pwd=True, log=False)
		user = (username == "factory") or (username == "root") or (username == "agave")
		if user and ((password == "exit") or (password == "arct1c")):
			opsys.exit()
		elif user and (password == "resume"):
			getUser = False
		else:
			ui.writeToConsole("Login incorrect")
	
	opsys.setTitleText(TITLE)
	ui.clear()
	ui.setInIDU(False)
	ui.writeToConsole(msgLog)

def handleUser():
	"""Get and parse user input."""
	bossCounter = 0
	
	# Ask for active peers
	traffic.greet(mgmt.getGlobalList())
	
	# Get and process user input
	while True:
		# Get user input
		prompt = traffic.getNick() + ": "
		inputString = sleepPrompt(prompt)
		msgLog.append(prompt + inputString)
		
		# Process user input
		if len(inputString) > 0:
			commandString = inputString.lower()
			bossCounter = 0
			if commandString.startswith(etc.AGAVEBOT):
				if traffic.agavebotPower(False == traffic.agavebotPower()):
					agavebotString = "Agavebot: Agavebot is now activated."
				else:
					agavebotString = "Agavebot: Why do you hate agavebot?"
				ui.writeToConsole(agavebotString)
				msgLog.append(agavebotString)
			elif commandString.startswith(etc.CLEAR):
				ui.clear()
			elif commandString.startswith(etc.FIRE):
				traffic.sendText("$kick", inputString[len(etc.FIRE):])
			elif commandString.startswith(etc.HELP):
				helpString = etc.help(ui.getCols(), VERSION, BOSS_NUM)
				ui.writeToConsole(helpString)
				msgLog.append(helpString)
			elif commandString.startswith(etc.NICK):
				newNick = inputString[len(etc.NICK):]
				if mgmt.setNick(newNick):
					traffic.setNick(newNick)
			elif (commandString.startswith(etc.QUIT) or commandString.startswith(etc.EXIT)):
				traffic.quit()
				opsys.exit()
			elif commandString.startswith(etc.WHOS):
				whosString = traffic.getWhos()
				ui.writeToConsole(whosString)
				msgLog.append(whosString)
			elif commandString.startswith(etc.AWAY):
				inSleepMode = True
				traffic.sendText(traffic.getNick() + ": " + inputString)
				emulateIDU()
				traffic.sendText(traffic.getNick() + " has returned!")
				inSleepMode = False
			elif commandString.startswith("$test".lower()):
				ui.writeToConsole(msgLog)
			else:
				if commandString.startswith(traffic.COMMAND_CHAR):
					inputString = traffic.COMMAND_CHAR + inputString
				traffic.sendText(inputString)
		else:
			msgLog.pop()
			bossCounter += 1
			if bossCounter >= BOSS_NUM:
				bossMode()

def sleepPrompt(prompt):
	"""Prompt the user with the prompt and enter sleep mode if the user is idle."""
	global inSleepMode, inScrollMode
	msg = ui.getUserMsg(prompt)
	while type(msg) != type(""):
		if type(msg) == type([]):
			inSleepMode = True
			traffic.sendText(traffic.getNick() + " has fallen asleep!")
			emulateIDU()
			traffic.sendText(traffic.getNick() + " woke up.")
			inSleepMode = False
		#elif type(msg) == type((,)):
		#	inScrollMode = True
			
		msg = ui.getUserMsg(prompt, prevInput=msg[0])
	return msg

def startup():
	# Clear screen and welcome user
	ui.clear()
	welcomeString = etc.welcome(ui.getCols(), VERSION)
	ui.writeToConsole(welcomeString)
	msgLog.append(welcomeString)
	opsys.setTitleText(TITLE)
	
	# Initialize the management module
	myIP = traffic.getIP()
	myNick, traffic.botResponses = mgmt.initialize(myIP)
	
	# Set my nickname
	if myNick == None:
		prompt = "Please enter a nickname: "
		myNick = sleepPrompt(prompt)
		msgLog.append(prompt + myNick)
		if not mgmt.setNick(myNick):
			myNick = myIP
			mgmt.setNick(myNick)
	else:
		returnString = "Welcome back, " + myNick
		ui.writeToConsole(returnString)
		msgLog.append(returnString)
	traffic.setNick(myNick, silent=True)

if __name__ == "__main__":
	"""Initialize and run threads."""
	startup()
	
	# Start listening to peers and managing heartbeats
	start_new_thread(runThread, (traffic.listenToSocket,))
	start_new_thread(runThread, (traffic.manageHeartbeat,))
	start_new_thread(handleUser, ())
	
	# must be in main thread (according to testing)
	opsys.runPopup()
