#!/usr/bin/python
'''this guy will prompt the user for connection type and return local_IP or public_IP. 
You're welcome.'''


import string, urllib2, socket

def connectionPrompt():
  connectionType = raw_input("Local(L) or Remote(R) Connection?: ")
	connectionType = str(connectionType)

	connectionType = connectionType.upper()

	if connectionType[0:1] == 'L':
		print "Using Local IP: " + socket.gethostbyname(socket.gethostname())
		return socket.gethostbyname(socket.gethostname())
		
	elif connectionType[0:1] == 'R':
		myIP = urllib2.urlopen('http://ip.42.pl/raw').read()
		print "Using Public IP: " + myIP
		return myIP

		
	else:
		print 'INVALID INPUT'
		connectionPrompt()
