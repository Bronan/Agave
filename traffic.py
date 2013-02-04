#!/usr/bin/python
"""Manage message traffic."""
# Filename: traffic.py
import socket

# Command Strings
COMMAND_CHAR = "$"
AGAVEBOT = (COMMAND_CHAR + "agavebot").lower()
GREET = (COMMAND_CHAR + "greet").lower()
HEARTBEAT = (COMMAND_CHAR + "heartbeat").lower()
KICK = (COMMAND_CHAR + "kick").lower()
QUIT = (COMMAND_CHAR + "quit").lower()

LOCAL_IP = socket.gethostbyname(socket.gethostname())	# Gets local IP address
PORT = 7721												# Port to send packets on
def connectionPrompt(connectionType):
  
	if connectionType[0:1] == 'L':
		print "Using Local IP: " + socket.gethostbyname(socket.gethostname())
		return socket.gethostbyname(socket.gethostname())
		
	elif connectionType[0:1] == 'R':
		myIP = urllib2.urlopen('http://ip.42.pl/raw').read()
		print "Using Public IP: " + myIP
		return myIP
		
	elif connectionType[0:1] == 'M':
		myIP = raw_input("IP Address: ")
		myIP =str(myIP)
		print "Using Manual IP: " + myIP
		return myIP
	else:
		print 'INVALID INPUT'
		connectionPrompt()

def listenToSocket():
	"""Get incoming messages."""
	socketIn = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) # Create socket
	socketIn.bind(('', PORT))									# Bind socket to specified port
	data, addr = socketIn.recvfrom(1024)						# Get up to 1024 bytes (inclusive) and store in data, put sender's ip in addr[0].
	if data:
		msg = decrypt(data)
	else:
		msg = ""
	socketIn.close()
	
	return msg, addr[0]

def sendText(text, ipAddr):
	"""Send input string to one peer"""
	if type(ipAddr) == type(""):	# if string
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

def getIP():
	"""Return my IP"""
	return LOCAL_IP
