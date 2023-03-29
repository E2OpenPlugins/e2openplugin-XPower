from __future__ import absolute_import
from __future__ import print_function
# for localized messages  	 
from . import _

from Screens.Screen import Screen
from Components.Sources.List import List
from Components.ActionMap import ActionMap, HelpableActionMap
from Screens.HelpMenu import HelpableScreen
from Components.Pixmap import Pixmap
from Components.Button import Button
from Components.Label import Label
from Tools.LoadPixmap import LoadPixmap
from Tools.Directories import resolveFilename, SCOPE_PLUGINS, SCOPE_SKIN_IMAGE
from Screens.ChoiceBox import ChoiceBox
from Screens.MessageBox import MessageBox
from Components.Sources.StaticText import StaticText
from Components.config import config

from enigma import eTimer

import telnetlib
import os
from os import path as os_path

from .xpowerut import ixpowerUt, xpowerUt
from .xpoweredit import xpowerEdit
from .xpowerhlp import xpowerHelp

# Global
version = "1.59"

OS_XP = "0"
OS_WIN7 = "1"
OS_LINUX = "2"
OS_RPC= "5"
OS_WIN8 = "3"

SHUTDOWN = "0"
SUSPEND = "1"
HIBERNATE = "2"

class xpowerSummary(Screen):
	skin = """
	<screen position="0,0" size="96,64">
		<widget source="title" render="Label" position="0,0" size="96,12" font="FdLcD;12" halign="left" foregroundColor="#00ccc040" />
		<widget source="pcname" render="Label" position="0,12" size="200,40" font="FdLcD;40" halign="left" valign="center" foregroundColor="#00f0f0f0"/>
		<widget source="bouquet" render="Label" position="0,52" size="96,12" font="FdLcD;12" halign="left" foregroundColor="#00ccc040"/>
	</screen>"""

	def __init__(self, session, parent):
		Screen.__init__(self, session, parent = parent)
		self["title"] = StaticText(_(parent.setup_title))
		self["pcname"] = StaticText("")
		self["bouquet"] = StaticText("")
		self.onShow.append(self.addWatcher)
		self.onHide.append(self.removeWatcher)

	def addWatcher(self):
		self.parent.onChangedEntry.append(self.selectionChanged)
		self.parent["config"].onSelectionChanged.append(self.selectionChanged)
		self.selectionChanged()

	def removeWatcher(self):
		self.parent.onChangedEntry.remove(self.selectionChanged)
		self.parent["config"].onSelectionChanged.remove(self.selectionChanged)

	def selectionChanged(self):
		self["pcname"].text = self.parent.getCurrentEntry()
		self["bouquet"].text = self.parent.getCurrentValue()

class xpower(Screen, HelpableScreen):
	skin = """
	<screen position="center,center" size="560,430" title="XPower" >

		<ePixmap name="red"    position="0,0"   zPosition="2" size="140,40" pixmap="skin_default/buttons/red.png" transparent="1" alphatest="on" />
		<ePixmap name="green"  position="140,0" zPosition="2" size="140,40" pixmap="skin_default/buttons/green.png" transparent="1" alphatest="on" />
		<ePixmap name="yellow" position="280,0" zPosition="2" size="140,40" pixmap="skin_default/buttons/yellow.png" transparent="1" alphatest="on" /> 
		<ePixmap name="blue"   position="420,0" zPosition="2" size="140,40" pixmap="skin_default/buttons/blue.png" transparent="1" alphatest="on" /> 

		<widget name="key_red" position="0,0" size="140,40" valign="center" halign="center" zPosition="4"  foregroundColor="white" font="Regular;20" transparent="1" shadowColor="background" shadowOffset="-2,-2" /> 
		<widget name="key_green" position="140,0" size="140,40" valign="center" halign="center" zPosition="4"  foregroundColor="white" font="Regular;20" transparent="1" shadowColor="background" shadowOffset="-2,-2" /> 
		<widget name="key_yellow" position="280,0" size="140,40" valign="center" halign="center" zPosition="4"  foregroundColor="white" font="Regular;20" transparent="1" shadowColor="background" shadowOffset="-2,-2" />
		<widget name="key_blue" position="420,0" size="140,40" valign="center" halign="center" zPosition="4"  foregroundColor="white" font="Regular;20" transparent="1" shadowColor="background" shadowOffset="-2,-2" />

		<widget source="config" render="Listbox" position="10,40" size="545,360" scrollbarMode="showOnDemand">
			<convert type="TemplatedMultiContent">
				{"template": [
						MultiContentEntryPixmapAlphaTest(pos = (15, 2), size = (48, 38), png = 0), # index 0 is the PC pixmap (for pixmap it is png= )
						MultiContentEntryText(pos = (90, 6), size = (120, 35), font=0, flags = RT_HALIGN_LEFT, text = 1), # index 1 is the Name (for text it is text= )
						MultiContentEntryPixmapAlphaTest(pos = (220, 2), size = (40, 40), png = 2), # index 2 is the system pixmap
						MultiContentEntryText(pos = (290, 3), size = (250, 20), font=1, flags = RT_HALIGN_LEFT, text = 3), # index 3 is the IP
						MultiContentEntryText(pos = (290, 23), size = (250, 20), font=1, flags = RT_HALIGN_LEFT, text = 4), # index 4 is the MAC
						],
					"fonts": [gFont("Regular", 30),gFont("Regular", 18)],
					"itemHeight": 45
				}
			</convert>
		</widget>

		<ePixmap pixmap="skin_default/div-h.png" position="0,406" zPosition="1" size="560,2" />
		<ePixmap alphatest="on" pixmap="skin_default/icons/clock.png" position="480,413" size="14,14" zPosition="3"/>
		<widget font="Regular;18" halign="left" position="505,410" render="Label" size="55,20" source="global.CurrentTime" transparent="1" valign="center" zPosition="3">
			<convert type="ClockToText">Default</convert>
		</widget>
		<ePixmap pixmap="skin_default/buttons/key_menu.png" position="430,408" zPosition="3" size="35,25" alphatest="on" transparent="1" />
		<widget name="statusbar" position="10,410" size="420,20" font="Regular;18" />

	</screen>"""

	def __init__(self, session, plugin_path):
		self.skin = xpower.skin
		self.session = session
		self.ppath = plugin_path
		self.setup_title = _("XPower")

		Screen.__init__(self, session)
		HelpableScreen.__init__(self)

		self["key_red"] = Button(_("Close"))
		self["key_green"] = Button(_("Add/Edit"))
		self["key_yellow"] = Button(_("Delete"))
		self["key_blue"] = Button(_("Help"))

		self.list = []

		self["config"] = List(self.list)
		self["statusbar"] = Label()
		self.text = _("User defined...")

		self["XPowerActions"] = HelpableActionMap(self, "XPowerActions",
			{
			"red": (self.cancel, _("Close plugin")),
			"green": (self.keyOK, _("Add/Edit item")),
			"yellow": (self.deleteItem, _("Delete selected item")),
			"blue": (self.help, _("Help")),
			"bouqdn": (self.bouqDown, self.text),
			"cancel": (self.cancel, _("Close plugin")),
			"ok": (self.keyOK, _("Add/Edit item")),
			"menu": (self.showMenu, _("Select power management")),

			"shutdown": (self.shutdown, _("Shutdown")),
			"wakeup": (self.wakeup, _("WakeUp")),
			"abort": (self.abort, _("Abort shutdown / reboot")),
			"restart": (self.reboot, _("Reboot")),
			"suspend": (self.suspend, _("Suspend")),
			"hibernate": (self.hibernate, _("Hibernate")),
			"edit": (self.startMoving, _("Enable/disable moving item")),
			}, -1)
		self["XPowerEditActions"] = HelpableActionMap(self, "DirectionActions",
			{
			"moveUp":	(self.moveUp, _("Move item up")),
			"moveDown":	(self.moveDown, _("Move item down")),
			}, -1)
		self.edit = 0
		self.idx = 0
		self.changes = False
		self["h_prev"] = Pixmap()
		self["h_next"] = Pixmap()
		self.showPrevNext()

		self.ipStr = _("IP:")+" "
		self.macStr = _("MAC:")+" "

		self.menu = []
		self.menu.append((_("WakeUp"), "wakeup"))
		self.menu.append((_("Suspend"), "suspend"))
		self.menu.append((_("Shutdown"), "shutdown"))
		self.menu.append((_("Reboot"), "reboot"))
		self.menu.append((_("Hibernate"), "hibernate"))
		self.menu.append((_("Abort shutdown / reboot"), "abort"))

		self.pcinfo = None
		self.showPCsList()

		self.commandTimer = eTimer()
		self.commandTimer.timeout.get().append(self.sendDelayed)
		
		self.onShown.append(self.prepare)
		self["config"].onSelectionChanged.append(self.statusbarText)

		self.onChangedEntry = []


	# for summary (+ changedEntry):
	def getCurrentEntry(self):
		current = self["config"].getCurrent()
		return ixpowerUt.remotepc[current[1]]['name']
	def getCurrentValue(self):
		self.statusbarText()
		return _("BouqDn: %s") % (self.text)
	def createSummary(self):
		return xpowerSummary
	###

	def startMoving(self):
		self.edit = not self.edit
		if self.edit and config.plugins.xpower.sort.value:
			self.message(_("It has not sense change order if is set list sorting..."), 5)
			self.edit = False
			self.showPrevNext()
			return
		self.idx = self["config"].getIndex()
		self.showPrevNext()
	def showPrevNext(self):
		if self.edit:
			self["h_prev"].show()
			self["h_next"].show()
		else:
			self["h_prev"].hide()
			self["h_next"].hide()
	def moveUp(self):
		if self.edit and self.idx -1 >= 0:
			self.moveDirection(-1)
	def moveDown(self):
		if self.edit and self.idx +1 < self["config"].count():
			self.moveDirection(1)
	def moveDirection(self, direction):
			self["config"].setIndex(self.idx)
			tmp = self["config"].getCurrent()
			self["config"].setIndex(self.idx+direction)
			tmp2 = self["config"].getCurrent()
			self["config"].modifyEntry(self.idx, tmp2)
			self["config"].modifyEntry(self.idx+direction, tmp)
			self.idx+=direction
			self.changes = True

	def prepare(self):
		self.setTitle(_("XPower") + " " + version)

	def showMenu(self):
		menu_title_text = "%s" % (self.pcinfo['name']) + _(" - select action:")
		self.session.openWithCallback(self.subMenu, ChoiceBox, title = menu_title_text, list=self.menu, keys = [ "1", "2", "3", "4", "5", "8",])

	def subMenu(self, choice):
		if choice is None:
			return
		if choice[1] == "wakeup":
			self.wakeup()
		else:
			self.command = choice[1]
			self.sendCommand()

	def statusbarText(self):
		self.text = _("Shutdown")
		current = self["config"].getCurrent()
		if current:
			self.pcinfo = ixpowerUt.remotepc[current[1]]
			
			if self.pcinfo['system'] != OS_RPC:
				if self.pcinfo['bqdn'] == SUSPEND:
					self.text = _("Suspend")
				if self.pcinfo['bqdn'] == HIBERNATE:
					self.text = _("Hibernate")
		self["statusbar"].setText(_("BouqUp for %s, BouqDn for %s") % (_("WakeUp"), self.text))

	def bouqDown(self):
		if self.pcinfo['system'] == OS_RPC:
			self.shutdown()
		else:
			if self.pcinfo['bqdn'] == SUSPEND:
				self.suspend()
			elif self.pcinfo['bqdn'] == HIBERNATE:
				self.hibernate()
			else:
				self.shutdown()

	def getItemParams(self, pcinfo):
		ip = pcinfo['ip']
		user = pcinfo['user']
		passwd = pcinfo['passwd']
		os = pcinfo['system']
		mac = pcinfo['mac']
		return ( os, ip, user, passwd, mac )

	def xpnet(self):
		if self.pcinfo['system'] == OS_RPC:
			if os.system("net rpc | grep 'net rpc' > /dev/null 2>&1") != 0:
				self.message(_("Command \"net\" is not installed\noption \"XP NET RPC\" does not work..."), 10, "error")
				return False
		return True

	def isAlive(self):
		if self.alive():
			return True
		else:
			self.message(_("No response from %s.") % (self.pcinfo['name']), 5, "error")
			return False

	def shutdown(self):
		self.command = "shutdown"
		self.sendCommand()

	def abort(self):
		self.command = "abort"
		self.sendCommand()

	def reboot(self):
		self.command = "reboot"
		self.sendCommand()

	def suspend(self):
		self.command = "suspend"
		self.sendCommand()

	def hibernate(self):
		self.command = "hibernate"
		self.sendCommand()

	def sendCommand(self):
		if self.xpnet():
			if self.isAlive():
				self.session.openWithCallback(self.exitPlugin, MessageBox, _("Please wait, \"%s\" is sended to computer %s") % (self.command, self.pcinfo['name']), type = MessageBox.TYPE_INFO, timeout = 3)
				self.commandTimer.start(100, True)

	def exitPlugin(self, data):
		if data is not None and data:
			if config.plugins.xpower.close.value:
				self.close()

	def sendDelayed(self):
		self.commandTimer.stop()
		if self.command == "shutdown":
			self.shutdownIP(self.getItemParams(self.pcinfo))
		elif self.command == "abort":
			self.abortIP(self.getItemParams(self.pcinfo))
		elif self.command == "reboot":
			self.rebootIP(self.getItemParams(self.pcinfo))
		elif self.command == "suspend":
			self.suspendIP(self.getItemParams(self.pcinfo))
		elif self.command == "hibernate":
			self.hibernateIP(self.getItemParams(self.pcinfo))

	def wakeup(self):
		self.wakeupIP(self.getItemParams(self.pcinfo))

	def showPCsList(self):
		oldIndex = self["config"].getIndex()
		oldCount = self["config"].count()

		list = []
		remotepc, remotepc_order = ixpowerUt.getPCsList()
		for name in remotepc_order:
			list.append(self.buildPCViewItem(remotepc[name]))
		if config.plugins.xpower.sort.value:
			list.sort(key = lambda x: x[1])
		self["config"].setList(list)

		newCount = self["config"].count()
		newIndex = self["config"].getIndex()

		self.setListIndex(oldIndex, newIndex, oldCount, newCount)

	def setListIndex(self, oldIndex, newIndex, oldCount, newCount):
		if newIndex != None: 
			if oldIndex + 1 == oldCount: # last record 
				if oldCount < newCount:	# added
					self["config"].setIndex(oldIndex+1)
				elif oldCount > newCount: # removed
					self["config"].setIndex(oldIndex-1)
				else: # same status
					self["config"].setIndex(oldIndex)
			else:
				self["config"].setIndex(oldIndex)

	def buildPCViewItem(self, entry):
		pc = LoadPixmap(cached=True, path=resolveFilename(SCOPE_PLUGINS, self.ppath+"/img/host.png"))
		ip = "".join((self.ipStr, str(entry["ip"])))
		mac = "".join((self.macStr, str(entry["mac"])))
		system = entry["system"]
		if system == OS_WIN7:
			logo = LoadPixmap(cached=True, path=resolveFilename(SCOPE_PLUGINS, self.ppath+"/img/win.png"))
		elif system == OS_WIN8:
			logo = LoadPixmap(cached=True, path=resolveFilename(SCOPE_PLUGINS, self.ppath+"/img/win8.png"))
		elif system == OS_LINUX:
			logo = LoadPixmap(cached=True, path=resolveFilename(SCOPE_PLUGINS, self.ppath+"/img/lin.png"))
		elif system == OS_RPC:
			logo = LoadPixmap(cached=True, path=resolveFilename(SCOPE_PLUGINS, self.ppath+"/img/rpc.png"))
		else:
			logo = LoadPixmap(cached=True, path=resolveFilename(SCOPE_PLUGINS, self.ppath+"/img/xp.png"))
		# return displayed items
		return( pc, entry["name"], logo, ip, mac )

	def keyOK(self):
		self.session.openWithCallback(self.editClosed, xpowerEdit, self.pcinfo)

	def editClosed(self):
		if ixpowerUt.configActualized:
			self.showPCsList()

	def deleteItem(self):
		self.retValue=self.pcinfo['name']
		self.session.openWithCallback(self.removeData, MessageBox, _("Do You want remove PC: %s?") % (self.pcinfo['name']), type = MessageBox.TYPE_YESNO)

	def removeData(self, answer ):
		if answer is not None and answer:
			ixpowerUt.removePC(self.retValue)
			ixpowerUt.writePCsConfig()
			ixpowerUt.getRemotePCPoints()
			self.showPCsList()
			self.session.open(MessageBox, _("PC has been removed..."), type = MessageBox.TYPE_INFO, timeout = 2)

	def help(self):
		self.session.open(xpowerHelp, self.ppath)

	def message(self, string, delay, msg_type=""):
		msg = MessageBox.TYPE_INFO
		if msg_type=="error":
			msg = MessageBox.TYPE_ERROR
		self.session.open(MessageBox, string, type = msg, timeout = delay)

	def cancel(self):
		if self.changes:
			ixpowerUt.writePCsConfig(self["config"].list)
		self.close()

	def getHostname(self):
		hostname = "enigma2"
		if os_path.exists("/etc/hostname"):
			fp = open('/etc/hostname', 'r')
			if fp:
				hostname = fp.readline()[:-1]
				fp.close()
		return hostname

	def netRpc(self, command):
		os.system(command)

	def alive(self):
		if not os.system("ping -c 2 -W 1 %s >/dev/null 2>&1" % (self.pcinfo['ip'])):
			return True
		return False

	# p is ( system, ip, user, passw, mac )

	def GetIPsFromNetworkInterfaces(self):
		import socket, fcntl, struct, array, sys
		is_64bits = sys.maxsize > 2**32
		struct_size = 40 if is_64bits else 32
		s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
		max_possible = 8 # initial value
		while True:
			_bytes = max_possible * struct_size
			names = array.array('B')
			for i in range(0, _bytes):
				names.append(0)
			outbytes = struct.unpack('iL', fcntl.ioctl(
				s.fileno(),
				0x8912,  # SIOCGIFCONF
				struct.pack('iL', _bytes, names.buffer_info()[0])
			))[0]
			if outbytes == _bytes:
				max_possible *= 2
			else:
				break
		namestr = names.tobytes()
		ifaces = []
		for i in range(0, outbytes, struct_size):
			iface_name = namestr[i:i+16].decode().split('\0', 1)[0]
			if iface_name != 'lo':
				iface_addr = socket.inet_ntoa(namestr[i+20:i+24])
				ifaces.append((iface_name, iface_addr))
		return ifaces

	#wakeup
	def wakeupIP(self, p):
		ifaces_list = self.GetIPsFromNetworkInterfaces()
		text = _("The network interface is not configured!")
		if ifaces_list:
			text = _("Magic packet has been send to PC %s") % (self.pcinfo['name'])
			for iface in ifaces_list:
				os.system("ether-wake -i %s %s" % (iface[0], p[4]))
		self.session.openWithCallback(self.exitPlugin, MessageBox, text, type = MessageBox.TYPE_INFO, timeout = 3)

	#shutdown
	def shutdownIP(self, p):
		if p[0] == OS_WIN7:
			self.telnet(p, "shutdown /s /t 10")
		elif p[0] == OS_WIN8:
			self.telnet(p, "shutdown /s /f /t 10")
		elif p[0] == OS_LINUX:
			self.telnet(p, "sudo shutdown -P now")
		elif p[0] == OS_RPC:
			self.netRpc("net rpc shutdown -I %s -U %s%s%s -C %s > /dev/null 2>&1" % (p[1], p[2], "%", p[3], self.getHostname()+":shutdown"))
		else:
			self.telnet(p, "shutdown -s -t 10")

	#abort
	def abortIP(self, p):
		if p[0] == OS_WIN7:
			self.telnet(p, "shutdown /a")
		elif p[0] == OS_WIN8:
			self.telnet(p, "shutdown /a")
		elif p[0] == OS_LINUX:
			self.telnet(p, "sudo shutdown -c")
		elif p[0] == OS_RPC:
			self.netRpc("net rpc abortshutdown -I %s -U %s%s%s > /dev/null 2>&1" % (p[1], p[2], "%", p[3]))
		else:
			self.telnet(p, "shutdown -a")

	#reboot
	def rebootIP(self, p):
		if p[0] == OS_WIN7:
			self.telnet(p, "shutdown /r /t 10")
		elif p[0] == OS_WIN8:
			self.telnet(p, "shutdown /r /f /t 10")
		elif p[0] == OS_LINUX:
			self.telnet(p, "sudo shutdown -r now")
		elif p[0] == OS_RPC:
			self.netRpc("net rpc shutdown -r -I %s -U %s%s%s -C %s > /dev/null 2>&1" % (p[1], p[2], "%", p[3], self.getHostname()+":reboot"))
		else:
			self.telnet(p, "shutdown -r -t 10")

	#standby
	def suspendIP(self, p):
		if p[0] == OS_WIN7:
			self.telnet(p, "rundll32.exe PowrProf.dll,SetSuspendState", "powercfg -h off", "powercfg -h off")
		elif p[0] == OS_WIN8:
			self.telnet(p, "shutdown /h")
		elif p[0] == OS_LINUX:
			self.telnet(p, "sudo pm-suspend --quirk-s3-mode")
		elif p[0] == OS_RPC:
			self.netRpc("net rpc shutdown -I %s -U %s%s%s -C %s > /dev/null 2>&1" % (p[1], p[2], "%", p[3], self.getHostname()+":shutdown"))
		else:
			self.telnet(p, "rundll32.exe PowrProf.dll,SetSuspendState", "powercfg /h off", "powercfg /h off")

	#hibernate
	def hibernateIP(self, p):
		if p[0] == OS_WIN7:
			self.telnet(p, "rundll32.exe PowrProf.dll,SetSuspendState Hibernate", "powercfg -h on", "powercfg -h on")
		elif p[0] == OS_WIN8:
			self.telnet(p, "shutdown /h")
		elif p[0] == OS_LINUX:
			self.telnet(p, "sudo pm-hibernate")
		elif p[0] == OS_RPC:
			self.netRpc("net rpc shutdown -I %s -U %s%s%s -C %s > /dev/null 2>&1" % (p[1], p[2], "%", p[3], self.getHostname()+":shutdown"))
		else:
			self.telnet(p, "rundll32.exe PowrProf.dll,SetSuspendState Hibernate", "powercfg /h on", "powercfg /h on")

	def telnet(self, p, command, pre = "", post = "" ):
		ip = p[1]
		user = p[2]
		passwd = p[3]
#		print("[xpower plugin] command:", command)
		try:telnet = telnetlib.Telnet(ip)
		except Exception as e:
			self.message(_("Connection failed... %s" % (e)), 4)
			print("[XPower plugin] Error telnet:", e)
		else:
#			telnet.set_debuglevel(1)
			if p[0] == OS_LINUX:
				try: 
					telnet.read_until(b'ogin: ', 10)
					telnet.write((user + '\r').encode('utf-8'))
					telnet.read_until(b'assword: ', 10)
					telnet.write((passwd + '\r').encode('utf-8'))
					telnet.read_until(user.encode('utf-8'), 5)
					telnet.write((command + '\r').encode('utf-8'))
					telnet.read_until(b'assword', 5)
					telnet.write((passwd + '\r').encode('utf-8'))
				except EOFError as e:
					"[xpower plugin] Error telnet:", e
				self.closeLinTelnet(telnet)
			else:
				try:
					telnet.read_until(b'ogin: ', 5)
					telnet.write((user + '\r\n').encode('utf-8'))
					telnet.read_until(b'assword: ', 5)
					telnet.write((passwd + '\r\n').encode('utf-8'))
					telnet.read_until(b'>', 5)
					if pre != "":
						telnet.write(('%s\r\n' % pre).encode('utf-8'))
					telnet.write(('%s\r\n' % (command)).encode('utf-8'))
					telnet.read_until(b'\r\n', 5)
					if post != "":
						telnet.write(('%s\r\n' % (post)).encode('utf-8'))
					telnet.write(('exit\r\n').encode('utf-8'))
					telnet.read_until(b'', 1)
				except EOFError as e:
					"[xpower plugin] Error telnet:", e

				self.closeLinTelnet(telnet)

#	def closeWinTelnet(self, telnet):
#		close = True
		# finish telnet, but must wait, while starting power management
#		try:tmp = telnet.read_very_eager()
#		except EOFError as e:
#			self.message(_("Connection finished... %s" % (e)),3)
#			close = False
#		except Exception as e:
#			self.message(_("Finished... %s" % (e)),3)
#		if close:		
#			telnet.close()

	def closeLinTelnet(self, telnet):
		close = True
		# finish telnet, but must wait, while starting power management
		i = 0
		while self.alive():
			try:tmp = telnet.read_until(b'xyz', 1)
			except EOFError as e:
				#self.message(_("Connection finished... %s" % (e)),3)
				close = False
				break
			except Exception as e:
				#self.message(_("Finished... %s" % (e)),4)
				break
			if self.command == "abort":
				break;
			if i > 15: # max cca 30s
				break
			i += 1
			
		if close:		
			telnet.close()

