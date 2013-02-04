#!/usr/bin/python
"""Run Agave."""
# Filename: agave.py
import opsys, etc, traffic, database	# opsys needs to be imported first.
import random, time
from thread import start_new_thread

# constants
VERSION = """2.22"""

# Constants
HIBER_NUM = 5
TITLE = "Agave v" + VERSION


#LOCAL_IP = traffic.getIP()
LOCAL_IP = traffic.connectionPrompt()

import ui

# Modes
CHAT = 0
AWAY = 1
SLEEP = 2
HIBERNATE = 3
MODE_TEXT = ["chat", "away", "sleep", "hibernate", "unknown"]

peers = {}			# All active IPs and nicknames
heartbeats = {}		# Hold heartbeat info
mode = {}			# Hold current operation mode
HB_SEND = 15		# Number of seconds to wait between sending heartbeats
HB_DROP = 60		# Number of seconds to wait before dropping peers
botResponses = []	# Hold responses for agavebot
botPower = False	# Hold agavebot power
msgLog = []			# Hold log of all messages

peers["Printer"] = "192.168.40.180"

def handleUser():
	"""Get and parse user input."""
	global botPower
	hiberCounter = 0
	
	# Get and process user input
	while True:
		# Get user input
		prompt = peers[LOCAL_IP] + ": "
		inputString = sleepPrompt(prompt)
		msgLog.append(prompt + inputString)
		
		# Process user input
		if len(inputString) > 0:
			commandString = inputString.lower()
			hiberCounter = 0
			if commandString.startswith(etc.AGAVEBOT):
				botPower = not botPower
				if botPower:
					printMsg("Agavebot: Agavebot is now activated.")
				else:
					printMsg("Agavebot: Why do you hate agavebot?")
			elif commandString.startswith(etc.CLEAR):
				ui.clear()
			elif commandString.startswith(etc.KICK):
				traffic.sendText(traffic.KICK, inputString[len(etc.KICK):])
			elif commandString.startswith(etc.HELP):
				printMsg(etc.help(ui.getCols(), VERSION, HIBER_NUM))
			elif commandString.startswith(etc.NICK):
				if len(inputString[len(etc.NICK):]) > 2:
					database.setNick(inputString[len(etc.NICK):])
					peers[LOCAL_IP] = inputString[len(etc.NICK):]
					sendStatus()
				else:
					printMsg("Nicknames must be at least 3 characters long.")
			elif (commandString.startswith(etc.QUIT) or commandString.startswith(etc.EXIT)):
				traffic.sendText(traffic.QUIT, peers.keys())
				opsys.exit()
			elif commandString.startswith(etc.WHOS):
				whosString = "\nPeer IP addresses  | Mode       | Peer nicknames\n" + "".center(34,"-")
				for ip in peers:
					whosString += "\n"
					if ip == LOCAL_IP:
						whosString += "-->"
					else:
						whosString += "   "
					whosString += ip.ljust(18) + MODE_TEXT[mode[ip]].ljust(13) + peers[ip]
				printMsg(whosString)
			elif commandString.startswith(etc.AWAY):
				setMode(AWAY)
				emulateIDU()
				setMode(CHAT)
			elif commandString.startswith("$test".lower()):
				printMsg(msgLog, log=False)
			else:
				if commandString.startswith(traffic.COMMAND_CHAR):
					inputString = traffic.COMMAND_CHAR + inputString
				traffic.sendText(inputString, peers.keys())
		else:
			msgLog.pop()
			hiberCounter += 1
			if hiberCounter >= HIBER_NUM:
				setMode(HIBERNATE)
				opsys.closePopup()
				emulateIDU()
				setMode(CHAT)
				opsys.resumePopup()

def processMessage():
	"""Parse incoming commands and print messages."""
	while True:
		msg, sendersIP = traffic.listenToSocket()
		
		# Update heartbeat
		heartbeats[sendersIP] = time.time()
		if not sendersIP in peers:
			peers[sendersIP] = sendersIP
			mode[sendersIP] = len(MODE_TEXT)-1
			sendStatus(traffic.GREET, ips=sendersIP)
			printMsg(peers[sendersIP] + " has joined the party.")
		
		# Parse or print message
		if msg.startswith(traffic.QUIT):
			delPeer(sendersIP)
		elif msg.startswith(traffic.HEARTBEAT):
			parseStatus(msg[len(traffic.HEARTBEAT):], sendersIP)
		elif msg.startswith(traffic.GREET):
			parseStatus(msg[len(traffic.GREET):], sendersIP)
			sendStatus()
		elif msg.startswith(traffic.KICK):
			traffic.sendText(traffic.QUIT, peers.keys())
			opsys.exit()
		else:
			if msg.startswith(traffic.AGAVEBOT):
				printMsg("Agavebot: " + msg[len(AGAVEBOT):])
			elif msg.startswith(traffic.COMMAND_CHAR + traffic.COMMAND_CHAR):
				printMsg(peers[sendersIP] + ": " + msg[len(traffic.COMMAND_CHAR):])
			else:
				printMsg(peers[sendersIP] + ": " + msg[:])
			if botPower:
				msg = botResponses[random.randint(0, len(botResponses)-1)]
				traffic.sendText(traffic.AGAVEBOT + msg, peers.keys())
				printMsg("Agavebot: " + msg)

def manageHeartbeat():
	"""Regulate heartbeat sends and drop peers that are dead."""
	while True:
		time.sleep(HB_SEND)
		
		sendStatus()
		
		dropTime = time.time() - HB_DROP
		IPs = heartbeats.keys()
		for ip in IPs:
			if (ip != LOCAL_IP) and (heartbeats[ip] < dropTime):
				delPeer(ip)

def sendStatus(command=traffic.HEARTBEAT, ips=peers.keys()):
	"""Updates peers with current mode and nick and tell them I'm alive."""
	traffic.sendText(command + chr(mode[LOCAL_IP]) + peers[LOCAL_IP], ips)

def parseStatus(msg, ip):
	"""Change ip's nick to the new nick."""
	setMode(msg[0], ip)
	newNick = msg[1:]
	if peers[ip] != newNick:
		printMsg(peers[ip] + " is now known as " + newNick)
		peers[ip] = newNick

def setMode(newMode, ip=LOCAL_IP):
	"""Change to the specified mode."""
	# Make sure it's a valid mode
	if newMode >= len(MODE_TEXT)-1:
		newMode = len(MODE_TEXT)-1
	
	# Update the mode if it's different
	if newMode != mode[ip]:
		mode[LOCAL_IP] = newMode
		
		# Tell someone the news
		if ip == LOCAL_IP:
			sendStatus()
		elif mode[LOCAL_IP] == CHAT:
			printMsg(peers[ip] + " is now in " + MODE_TEXT[mode[ip]] + " mode.")
		else:
			msgLog.append(peers[ip] + " is now in " + MODE_TEXT[mode[ip]] + " mode.")

def delPeer(ip):
	"""Delete the specified peer"""
	if ip in peers:
		printMsg(peers[ip] + " has left the party.")
		del peers[ip]
		del heartbeats[ip]

def printMsg(msg, log=True):
	"""This handles printing and alerting in the various modes."""
	if log:
		msgLog.append(msg)
	
	if mode[LOCAL_IP] == CHAT:
		ui.writeToConsole(msg)
		opsys.alert(msg)
	elif mode[LOCAL_IP] == AWAY:
		pass
	elif mode[LOCAL_IP] == SLEEP:
		opsys.alert("Please update Agave.")
	elif mode[LOCAL_IP] == HIBERNATE:
		pass

def sleepPrompt(prompt):
	"""Prompt the user with the prompt and enter sleep mode if the user is idle."""
	msg = ui.getUserMsg(prompt)
	while type(msg) != type(""):
		if type(msg) == type([]):
			setMode(SLEEP)
			emulateIDU()
			setMode(CHAT)
		msg = ui.getUserMsg(prompt, prevInput=msg[0])
	return msg

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
		user = (username == "factory") or (username == "root")
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

if __name__ == "__main__":
	"""Initialize and run threads."""
	# Set current mode
	mode[LOCAL_IP] = CHAT
	
	# Clear screen and welcome user
	ui.clear()
	printMsg(etc.welcome(ui.getCols(), VERSION))
	opsys.setTitleText(TITLE)
	
	# Initialize the database module
	dbNick, botResponses = database.initialize(LOCAL_IP)
	
	myNick = dbNick
	
	# Get nickname
	if myNick == None:
		prompt = "Please enter a nickname: "
		myNick = sleepPrompt(prompt)
		msgLog.append(prompt + myNick)
	else:
		returnString = "Welcome back, " + myNick
		printMsg(returnString)
		msgLog.append(returnString)
	
	# Make sure nickname is long enough
	if len(myNick) < 3:
		errorMsg = "Nickname must be longer than 2 characters. Defaulting to IP."
		printMsg(errorMsg)
		msgLog.append(errorMsg)
		myNick = LOCAL_IP
	
	# Store nickname
	if myNick != dbNick:
		database.setNick(myNick)
	peers[LOCAL_IP] = myNick
	
	# Start listening to peers and managing heartbeats
	start_new_thread(processMessage, ())
	start_new_thread(manageHeartbeat, ())
	start_new_thread(handleUser, ())
	
	# Ask for active peers
	sendStatus(traffic.GREET, ips=database.getGlobalList())
	
	# must be in main thread (according to testing, not theory)
	opsys.runPopup()	#handle popup notifications
