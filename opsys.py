#!/usr/bin/python
"""Manage operating system functions."""
# Filename: opsys.py
from platform import system

ON_WINDOWS = system() == "Windows"
if ON_WINDOWS:
	# Perform Windows initializations
	import win32api, win32con, win32gui
	
	win32gui.SystemParametersInfo(win32con.SPI_SETFOREGROUNDLOCKTIMEOUT, 0, win32con.SPIF_SENDWININICHANGE | win32con.SPIF_UPDATEINIFILE)
	windowHandle = win32gui.GetForegroundWindow()
else:
	# Perform non-Windows initializations
	import os

if ON_WINDOWS:
	def closePopup():
		"""Closes the displayed popup."""
		nid = (hwnd, 0)
		win32gui.Shell_NotifyIcon(win32gui.NIM_DELETE, nid)
else:
	def closePopup():
		pass

if ON_WINDOWS:
	def setTitleText(title):
		"""Sets the window title text."""
		win32gui.SetWindowText(windowHandle, title)
else:
	def setTitleText(title):
		pass

if ON_WINDOWS:
	def resumePopup():
		"""Resumes displaying popups."""
		# Display the taskbar icon
		flags = win32gui.NIF_ICON | win32gui.NIF_MESSAGE | win32gui.NIF_TIP
		nid = (hwnd, 0, flags, win32con.WM_USER+20, hicon, "Agave")
		win32gui.Shell_NotifyIcon(win32gui.NIM_ADD, nid)
else:
	def resumePopup():
		pass

if ON_WINDOWS:
	def alert(body):
		"""Displays the popup."""
		if windowHandle != win32gui.GetForegroundWindow():
			if type(body) == type([]):
				body = "\n".join(body)
			flags = win32gui.NIF_MESSAGE | win32gui.NIF_INFO
			nid = (hwnd, 0, flags, win32con.WM_USER+20, 0, "", body, 10, "Agave", win32gui.NIIF_INFO)
			win32gui.Shell_NotifyIcon(win32gui.NIM_MODIFY, nid)
else:
	def alert(body):
		pass

if ON_WINDOWS:
	def exit():
		"""Exit the program."""
		win32gui.PostMessage(windowHandle, win32con.WM_CLOSE, 0, 0)
else:
	def exit():
		os._exit(0)

if ON_WINDOWS:
	def onDestroy(hwnd, msg, wparam, lparam):
		closePopup()
	
	def onTaskbarNotify(hwndDiscard, msg, wparam, lparam):
		# 1029 is the code for clicking on a balloon and
		#	win32con.WM_LBUTTONUP is the code for clicking on the icon (no balloon)
		# NIN_BALLOONUSERCLICK should be the code for clicking on a balloon,
		#	but I cannot find which module has this constant
		if (lparam == win32con.WM_LBUTTONUP) or (lparam == 1029):
			if win32gui.IsIconic(windowHandle):
				win32gui.ShowWindow(windowHandle, win32con.SW_RESTORE)
			win32gui.SetForegroundWindow(windowHandle)
		return 1
	
	# Register the Window class.
	wc = win32gui.WNDCLASS()
	hinst = wc.hInstance = win32api.GetModuleHandle(None)
	wc.lpszClassName = "PythonTaskbarDemo"
	wc.style = win32con.CS_VREDRAW | win32con.CS_HREDRAW;
	wc.hCursor = win32gui.LoadCursor( 0, win32con.IDC_ARROW )
	wc.hbrBackground = win32con.COLOR_WINDOW
	wc.lpfnWndProc = {win32con.WM_DESTROY: onDestroy, win32con.WM_USER+20 : onTaskbarNotify}
	classAtom = win32gui.RegisterClass(wc)
	
	# Create the Window.
	style = win32con.WS_OVERLAPPED | win32con.WS_SYSMENU
	hwnd = win32gui.CreateWindow(classAtom, "Agave Update", style, \
		0, 0, win32con.CW_USEDEFAULT, win32con.CW_USEDEFAULT, \
		0, 0, hinst, None)
	win32gui.UpdateWindow(hwnd)
	
	# Set the icon and tooltip
	hicon = win32gui.LoadIcon(0, win32con.IDI_APPLICATION)
	
	# Display the taskbar icon
	flags = win32gui.NIF_ICON | win32gui.NIF_MESSAGE | win32gui.NIF_TIP
	nid = (hwnd, 0, flags, win32con.WM_USER+20, hicon, "Agave")
	win32gui.Shell_NotifyIcon(win32gui.NIM_ADD, nid)
	
	def runPopup():
		win32gui.PumpMessages()
else:
	def runPopup():
		while True:
			pass

""" nid structure
typedef struct _NOTIFYICONDATA {
  HWND  hWnd;
  UINT  uID;
  UINT  uFlags;
  UINT  uCallbackMessage;
  HICON hIcon;
  TCHAR szTip[64];
  DWORD dwState;
  DWORD dwStateMask;
  TCHAR szInfo[256];
  union {
    UINT uTimeout;
    UINT uVersion;
  };
  TCHAR szInfoTitle[64];
  DWORD dwInfoFlags;
  GUID  guidItem;
  HICON hBalloonIcon;
} NOTIFYICONDATA, *PNOTIFYICONDATA;
"""
