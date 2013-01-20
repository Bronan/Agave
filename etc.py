#!/usr/bin/python
"""Help and Welcome functions"""
# Filename: etc.py
import collections

# Command Strings
COMMAND_CHAR = "$"
AGAVEBOT = (COMMAND_CHAR + "agavebot").lower()
AWAY = (COMMAND_CHAR + "away ").lower()
CLEAR = (COMMAND_CHAR + "clear").lower()
EXIT = (COMMAND_CHAR + "exit").lower()
KICK = (COMMAND_CHAR + "kick ").lower()
HELP = (COMMAND_CHAR + "help").lower()
NICK = (COMMAND_CHAR + "nick ").lower()
QUIT = (COMMAND_CHAR + "quit").lower()
WHOS = (COMMAND_CHAR + "whos").lower()

HELP_DICT = {\
	AGAVEBOT: "Toggles agavebot.",\
	AWAY + "away_msg": "Enters away mode.",\
	CLEAR: "Clears the screen.",\
	EXIT + " or " + QUIT: "Quits the current session.",\
	HELP: "Displays this help message.",\
	NICK + "new_nick" : "Changes your nickname to new_nick.",\
	WHOS: "Lists all active users."}

ORDERED_HELP_DICT = collections.OrderedDict(sorted(HELP_DICT.items(), key=lambda t: t[0]))

def help(numCols, version, HIBER_NUM):
	"""Returns help text to be displayed when requested."""
	helpString = str("Agave Help v" + version).center(numCols) + "\n" + \
	"".center(numCols,"-") + "\n" + \
	'"You look like I could use a drink."'.center(numCols) + "\n" + \
	"".center(numCols,"-") + "\n"
	
	commandWidth = 0
	for command, text in ORDERED_HELP_DICT.items():
		commandWidth = max(len(command), commandWidth)
	commandWidth += 2	# Provide a minimum of two spaces between the commands and the help text.
	for command, text in ORDERED_HELP_DICT.items():
		helpString += command.ljust(commandWidth) + text + "\n"
	
	helpString += "Press enter " + str(HIBER_NUM) + " times to enter hibernation mode.\n"
	
	return helpString

def welcome(numCols, version):
	"""Returns welcome text to be displayed at startup."""
	return str("Agave v" + version).center(numCols) + "\n" + \
	"".center(numCols,"-") + "\n" + \
	'"60% of the time, it works every time."'.center(numCols) + "\n" + \
	"".center(numCols,"-") + "\n" + \
	("For help, type " + HELP + ".").center(numCols) + "\n"

IDU_TEXT = """PUMA U-Boot 1.3.3 (Feb 22 2011 - 23:07:55)

CPU:   MPC880ZPnn at 50 MHz: 8 kB I-Cache 8 kB D-Cache FEC present
Board: PUMA GEN2
DRAM:  64 MB
FLASH: 32 MB
In:    serial
Out:   serial
Err:   serial
Net:   FEC ETHERNET, FEC2 ETHERNET
FPGA:  0x4a55ffff
ACTIVE FPGA MTD BANK 2
CFPGA Programmed
FPGA:  0x00000000
FPGA:  0x00000000

External Interrupt IRQ1 is activated
FPGA:  0x00000100

External Interrupt IRQ1 is activated
FPGA:  0x00000100

External Interrupt IRQ1 is activated
FPGA:  0x00000100

External Interrupt IRQ1 is activated
FPGA:  0x00000100

External Interrupt IRQ1 is activated
FPGA:  0x00000100

External Interrupt IRQ1 is activated
Type password in 2 second to enter bootloader prompt
Un-Protected 4 sectors
ACTIVE FPGA MTD BANK 2
CFPGA Programmed
FPGA:  0x00000000
ACTIVE KERNEL BANK 2
ACTIVE APP BANK 1
## Booting image at 04300000 ...
   Image Name:   Linux-2.4.25
   Created:      2011-02-02   7:10:21 UTC
   Image Type:   PowerPC Linux Kernel Image (gzip compressed)
   Data Size:    1160355 Bytes =  1.1 MB
   Load Address: 00000000
   Entry Point:  00000000
   Verifying Checksum ... OK
   Uncompressing Kernel Image ... OK
Linux version 2.4.25 (root@debian-200) (gcc version 3.2.2 20030217 (Yellow Dog Linux 3.0 3.2.2-2a_1)) #1120 Tue Feb 1 23:10:13 PST 2011
PATCH DEFINED
PQUCODE: USB SOF patch installed
On node 0 totalpages: 16384
zone(0): 16384 pages.
zone(1): 0 pages.
zone(2): 0 pages.
Kernel command line: root=/dev/mtdblock7 ro rootfstype=jffs2 init=/bin/init mtdparts=phys:0x40000(uboot),0x40000(uboot_env),0x40000(CFPGA1),0x40000(CFPGA2),0x200000(Kernel1),0x200000(Kernel2),0xA00000(Application1),0xA00000(Application2),0x700000(/config) ccard=45000007
PQPIC: Init IRQ
PQUART: Serial Console Init
SCC3 UART Enabled baudrate=38400, BRG2-CD=80
Calibrating delay loop... 49.76 BogoMIPS
Page-cache hash table entries: 16384 (order: 4, 65536 bytes)
POSIX conformance testing by UNIFIX
Initializing RT netlink socket
Starting kswapd
pty: 256 Unix98 ptys configured
RAMDISK driver initialized: 16 RAM disks of 65536K size 1024 blocksize
PQRM: Init
VFS: Mounted root (jffs2 filesystem) readonly.
SCC3 UART Enabled baudrate=38400, BRG2-CD=80
*** PUMA System Initialization ***

Loading Select IPC Driver
Loading Jiffies Driver
Loading IO Driver
switch type IO = 0
enable_irq(2) unbalanced
Loading SPI BUS Driver
HOST ALLOC : Registering object successful
Trying to free free IRQ21
Loading I2C Engine Driver
Loading I2C BUS Driver
HOST ALLOC : Registering object for IIC successful
Loading EEPROM Driver
Loading FRAM Driver
Loading FAN Driver
Loading RTC Driver
Loading JTAG Driver
Loading ROH Driver
Loading Framer-Modem Sync Driver
Loading Framer Driver
enable_irq(4) unbalanced
Loading System Control Driver
Loading SNMP Switch Driver
Loading SNMP Marvell Switch Driver
Synch the system time from RTC...
Running Param Process...
Running Network Manager...
Running Log Process...
Running Time License Process...
Creating Links...
killall: syslogd: no process killed
Running StdIO Process...
Loading UPL Switch Driver
Loading GIGE UPL Switch Driver
Loading Marvell UPL Switch Driver
Running Switch Process...
AS
Running Controller Card Process...
Running Upper PS Card Process...
Running Lower PS Card Process...
Running East Modem Process...
modem_main : Unified Modem detected, baudrate set to 115200; modem_type[3]
Running UI Daemon...
Running FTP Server...
Running Mailer Process...
BetaFTPD active
Running monitor_call button...
Running USB PM Process...
Running Reconfig Server...

"""