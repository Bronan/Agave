#!/usr/bin/python
"""Manage message traffic."""
# Filename: traffic.py
import os, random, socket, time

LOCAL_IP = socket.gethostbyname(socket.gethostname())	# Gets local IP address
PORT = 7721												# Port to send packets on
peers = {}												# All active IPs and nicknames
HB_SEND = 15											# Number of seconds to wait between sending heartbeats
HB_DROP = HB_SEND * 4									# Number of seconds to wait before dropping peers
heartbeats = {}											# Hold heartbeat info
botResponses = {}										# Hold responses for agavebot
botPower = False										# Hold agavebot power

# Command Strings
COMMAND_CHAR = "$"
AGAVEBOT = (COMMAND_CHAR + "agavebot ").lower()
GREET = (COMMAND_CHAR + "greet ").lower()
HEARTBEAT = (COMMAND_CHAR + "heartbeat ").lower()
KICK = (COMMAND_CHAR + "kick").lower()
NICK = (COMMAND_CHAR + "nick ").lower()
QUIT = (COMMAND_CHAR + "quit").lower()

def listenToSocket():
	"""Get incoming messages."""
	listenToSocket.output = []
	
	socketIn = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) # Create socket
	socketIn.bind(('', PORT))									# Bind socket to specified port
	data, addr = socketIn.recvfrom(1024)						# Get up to 1024 bytes (inclusive) and store in data, put sender's ip in addr[0].
	if data:
		processMessage(data, addr[0])
	socketIn.close()
	
	return listenToSocket.output

def processMessage(encryptedMsg, sendersIP):
	"""Parse incoming commands and print messages."""
	newPeer = not sendersIP in peers
	
	msg = decrypt(encryptedMsg)
	
	# Parse or print message
	if msg.startswith(QUIT):
		delPeer(listenToSocket, sendersIP)
	elif msg.startswith(NICK):
		updateNick(sendersIP, msg[len(NICK):])
	elif msg.startswith(HEARTBEAT):
		updateNick(sendersIP, msg[len(HEARTBEAT):])
	elif msg.startswith(GREET):
		updateNick(sendersIP, msg[len(GREET):])
		sendHeartbeat(sendersIP)
	elif msg.startswith(KICK):
		quit()
		os._exit(0)
	else:
		if msg.startswith(AGAVEBOT):
			listenToSocket.output.append("Agavebot: " + msg[len(AGAVEBOT):])
		elif msg.startswith(COMMAND_CHAR + COMMAND_CHAR):
			listenToSocket.output.append(peers[sendersIP] + ": " + msg[len(COMMAND_CHAR):])
		else:
			listenToSocket.output.append(peers[sendersIP] + ": " + msg[:])
		agavebot()
	
	# Update heartbeat
	if not msg.startswith(QUIT):
		heartbeats[sendersIP] = time.time()
		if not sendersIP in peers:
			peers[sendersIP] = sendersIP
			greet(sendersIP)
		if newPeer:
			listenToSocket.output.append(peers[sendersIP] + " has joined the party.")

def agavebot():
	"""Agavebot auto responder."""
	if botPower:
		msg = botResponses[random.randint(0, len(botResponses)-1)]
		sendText(AGAVEBOT + msg)
		listenToSocket.output.append("Agavebot: " + msg)

def agavebotPower(newState=None):
	global botPower
	if newState != None:
		botPower = newState
	return botPower

def quit():
	"""Send quit message to peers."""
	sendText(QUIT)

def greet(ip):
	"""Greet potential peers when I come online."""
	sendText(GREET + peers[LOCAL_IP], ip)

def sendText(text, ipAddr=None):
	"""Send input string to one peer"""
	if ipAddr == None:
		ipList = peers.keys()
	elif type(ipAddr) == type(""):	# if string
		ipList = [ipAddr]
	elif type(ipAddr) == type([]):	# if list
		ipList = ipAddr
	elif type(ipAddr) == type({}):	# if dict
		ipList = ipAddr.keys()
	
	encryptedMsg = encrypt(text)
	
	for ip in ipList:
		if ip != LOCAL_IP:
			try:
				socketOut = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
				socketOut.sendto(encryptedMsg, (ip, PORT))
				socketOut.close()
			except socket.error:
				pass

def encrypt(msgToCode):
	msgToCode = str(msgToCode)
	codedMsg = ""
	idx = 0
	while idx < len(msgToCode)-1:
		codedMsg += chr(ord(msgToCode[idx])^ord(msgToCode[idx+1]))
		idx += 1
	codedMsg += chr(ord(msgToCode[len(msgToCode)-1])^ord("&"))
	return codedMsg

def decrypt(msgToDecode):
	msgToDecode = str(msgToDecode)
	msgDecoded = chr(ord(msgToDecode[len(msgToDecode)-1])^ord("&"))
	
	idx = len(msgToDecode)-2
	while idx >= 0:
		msgDecoded = chr(ord(msgToDecode[idx])^ord(msgDecoded[0])) + msgDecoded
		idx -= 1
	return msgDecoded

def getNick():
	"""Return my current nickname."""
	return peers[LOCAL_IP]

def getIP():
	"""Return my IP"""
	return LOCAL_IP

def setNick(newNick, silent=False):
	"""Set my nickname."""
	peers[LOCAL_IP] = newNick
	
	if not silent:
		sendText(NICK + newNick)

def getWhos():
	"""Return a printable string of all current users with a header about myself."""
	listString = "My nickname: " + peers[LOCAL_IP] +\
	"\nMy IP address: " + LOCAL_IP
	if len(peers) <= 1:
		listString += "\n\nThere are no other users online."
	else:
		listString += "\n\nPeer IP addresses | Peer nicknames\n" +\
		"".center(34,"-")
		for ip in peers:
			if ip != LOCAL_IP:
				listString += "\n" + ip.ljust(20) + peers[ip]
	return listString

def delPeer(threadFunction, ip):
	"""Delete the specified peer"""
	if ip in peers:
		threadFunction.output.append(peers[ip] + " has left the party.")
		del peers[ip]
		del heartbeats[ip]

def updateNick(ip, newNick):
	"""Change the specified peer's nickname"""
	if ip in peers:
		if newNick != peers[ip]:
			listenToSocket.output.append(peers[ip] + " is now known as " + newNick)
	peers[ip] = newNick

def sendHeartbeat(ip=None):
	"""Send the heartbeat message so peers know that I'm online."""
	heartbeatMessage = HEARTBEAT + peers[LOCAL_IP]
	if ip == None:
		sendText(heartbeatMessage)
	else:
		sendText(heartbeatMessage, ip)

def manageHeartbeat():
	"""Regulate heartbeat sends and drop peers that are dead."""
	manageHeartbeat.output = []
	
	time.sleep(HB_SEND)
	
	sendHeartbeat()
	
	dropTime = time.time() - HB_DROP
	IPs = heartbeats.keys()
	for ip in IPs:
		if (ip != LOCAL_IP) and (heartbeats[ip] < dropTime):
			delPeer(manageHeartbeat, ip)
	
	return manageHeartbeat.output
