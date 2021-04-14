from . import _

import os
import enigma
from Components.config import config, getConfigListEntry, ConfigSubsection, ConfigYesNo, ConfigSelection, NoSave, ConfigIP, ConfigPassword, ConfigText
from Screens.MessageBox import MessageBox
from Screens.Screen import Screen
from Components.ConfigList import ConfigListScreen
from Components.ActionMap import ActionMap, HelpableActionMap
from Screens.HelpMenu import HelpableScreen
from Components.Button import Button
from Components.Label import Label
from Components.Pixmap import Pixmap, MultiPixmap

from xpowerut import ixpowerUt, xpowerUt

# Configuration
config.plugins.xpower = ConfigSubsection()
config.plugins.xpower.name = NoSave(ConfigText(default=_("PC"), fixed_size=False))
config.plugins.xpower.ip = NoSave(ConfigIP(default=[192, 168, 1, 100]))
config.plugins.xpower.mac = NoSave(ConfigText(default="00:00:00:00:00:00"))
config.plugins.xpower.system = NoSave(ConfigSelection(default="0", choices=[("0", _("XP")), ("1", _("Win7")), ("3", _("Win8")), ("2", _("Linux")), ("5", _("XP NET RPC"))]))
config.plugins.xpower.user = NoSave(ConfigText(default="administrator", fixed_size=False))
config.plugins.xpower.passwd = NoSave(ConfigPassword(default="password", fixed_size=False))
config.plugins.xpower.bqdn = NoSave(ConfigSelection(default="0", choices=[("0", _("Shutdown")), ("1", _("Suspend")), ("2", _("Hybernate"))]))
config.plugins.xpower.close = ConfigYesNo(default=False)
config.plugins.xpower.sort = ConfigYesNo(default=True)
cfg = config.plugins.xpower

class xpowerEdit(Screen, ConfigListScreen, HelpableScreen):
	skin = """
	<screen position="center,center" size="560,275" title="XPower Configuration PC" >

		<ePixmap name="red"    position="0,0"   zPosition="2" size="140,40" pixmap="skin_default/buttons/red.png" transparent="1" alphatest="on" />
		<ePixmap name="green"  position="140,0" zPosition="2" size="140,40" pixmap="skin_default/buttons/green.png" transparent="1" alphatest="on" />
		<ePixmap name="yellow" position="280,0" zPosition="2" size="140,40" pixmap="skin_default/buttons/yellow.png" transparent="1" alphatest="on" /> 
		<ePixmap name="blue"   position="420,0" zPosition="2" size="140,40" pixmap="skin_default/buttons/blue.png" transparent="1" alphatest="on" /> 

		<widget name="key_red" position="0,0" size="140,40" valign="center" halign="center" zPosition="4"  foregroundColor="white" font="Regular;20" transparent="1" shadowColor="background" shadowOffset="-2,-2" /> 
		<widget name="key_green" position="140,0" size="140,40" valign="center" halign="center" zPosition="4"  foregroundColor="white" font="Regular;20" transparent="1" shadowColor="background" shadowOffset="-2,-2" /> 
		<widget name="key_yellow" position="280,0" size="140,40" valign="center" halign="center" zPosition="4"  foregroundColor="white" font="Regular;20" transparent="1" shadowColor="background" shadowOffset="-2,-2" />
		<widget name="key_blue" position="420,0" size="140,40" valign="center" halign="center" zPosition="4"  foregroundColor="white" font="Regular;20" transparent="1" shadowColor="background" shadowOffset="-2,-2" />

		<widget name="config" position="30,40" size="520,200" scrollbarMode="showOnDemand"/>

		<ePixmap pixmap="skin_default/div-h.png" position="0,251" zPosition="1" size="560,2" />
		<ePixmap alphatest="on" pixmap="skin_default/icons/clock.png" position="480,258" size="14,14" zPosition="3"/>
		<widget font="Regular;18" halign="left" position="505,255" render="Label" size="55,20" source="global.CurrentTime" transparent="1" valign="center" zPosition="3">
			<convert type="ClockToText">Default</convert>
		</widget>
		<widget name="statusbar" position="10,255" size="470,20" font="Regular;18" />
	
		<widget name="0" pixmaps="skin_default/buttons/button_green_off.png,skin_default/buttons/button_green.png" position="10,43" zPosition="10" size="15,16" transparent="1" alphatest="on"/>
		<!--widget name="2" pixmaps="skin_default/buttons/button_blue_off.png,skin_default/buttons/button_blue.png" position="10,93" zPosition="10" size="15,16" transparent="1" alphatest="on"/-->

	</screen>"""

	def __init__(self, session, pcinfo=None):
		self.skin = xpowerEdit.skin
		self.session = session
		self.pcinfo = pcinfo
		
		Screen.__init__(self, session)
		HelpableScreen.__init__(self)

		self.mac = getConfigListEntry(_("MAC"), cfg.mac)
		xpowerEditconfigList = []
		xpowerEditconfigList.append(getConfigListEntry(_("Name"), cfg.name))
		xpowerEditconfigList.append(getConfigListEntry(_("IP"), cfg.ip))
		xpowerEditconfigList.append(self.mac)
		xpowerEditconfigList.append(getConfigListEntry(_("System"), cfg.system))
		xpowerEditconfigList.append(getConfigListEntry(_("User"), cfg.user))
		xpowerEditconfigList.append(getConfigListEntry(_("Password"), cfg.passwd))
		xpowerEditconfigList.append(getConfigListEntry(_("BouqDown"), cfg.bqdn))
		xpowerEditconfigList.append(getConfigListEntry(_("Closing plugin"), cfg.close))
		xpowerEditconfigList.append(getConfigListEntry(_("Sort list"), cfg.sort))

		ConfigListScreen.__init__(self, xpowerEditconfigList, session=self.session, on_change=self.changedEntry)

		if self.pcinfo is None:
			self.pcinfo = {'name': False, 'ip': False, 'mac': False, 'system': False, 'user': False, 'passwd': False, 'bqdn': False}

		self["key_red"] = Button(_("Cancel"))
		self["key_green"] = Button(_("Ok"))
		self["key_yellow"] = Button()
		self["key_blue"] = Button(_("Get MAC"))

		self["statusbar"] = Label()
#		self["statusbar"].setText(_("BouqUp for WakeUp"))

		self["0"] = MultiPixmap()

		self.remotepc = {}
		self.remotepc_order = []

		self["XPowerActions"] = HelpableActionMap(self, "XPowerActions",
			{
			"ok": self.ok,
			"cancel": self.cancel,
			"red": self.cancel,
			"green": self.ok,
			"blue": (self.getPcMAC, _("get MAC of running PC")),
#			"wakeup": (self.wakeup, _("wakeup PC")),
			}, -1)
		self.setup_title = _("XPower: %s" % (self.pcinfo['name']))
		self.onChangedEntry = []
		(self.remotepc, self.remotepc_order) = ixpowerUt.getPCsList()
		self.fillCfg()
		self.old = self.getBackupCfg()
		self.onShown.append(self.setWindowTitle)
		self.onLayoutFinish.append(self.isAlive)


	# for summary
	def changedEntry(self):
		for x in self.onChangedEntry:
			x()
	def getCurrentEntry(self):
		return self["config"].getCurrent()[0]
	def getCurrentValue(self):
		return str(self["config"].getCurrent()[1].getText())
	def createSummary(self):
		from Screens.Setup import SetupSummary
		return SetupSummary
	###

	def setWindowTitle(self):
		self.setTitle(_("XPower PC configuration:") + " " + "%s" % (self.pcinfo['name']))

#	def wakeup(self):
#		ip = "%s.%s.%s.%s" % (tuple(cfg.ip.value))
#		os.system("ether-wake %s" % (ip))
#		self.session.open(MessageBox,_("Magic packet has been send to PC %s") % (self.pcinfo['name']),type = MessageBox.TYPE_INFO, timeout = 3)
		#from ui import xpower
		#self.session.open(xpower,xpower.wakeup)

	def getPcMAC(self):						
		ip = "%s.%s.%s.%s" % (tuple(cfg.ip.value))
		self.readAlive(ip)
		pcMAC = self.readMac(ip)
		if pcMAC is not None:
			cfg.mac.value = pcMAC
			self["config"].invalidate(self.mac)
		else:
			res = os.system("ping -c 2 -W 1 %s >/dev/null 2>&1" % (ip))
			if not res:
				pcMAC = self.readMac(ip)
				if pcMAC is not None:
					cfg.mac.value = pcMAC
					self["config"].invalidate(self.mac)

	def readMac(self, ip):
		pcMAC = None
		file = open("/proc/net/arp", "r")
		while True:
			entry = file.readline().strip()
			if entry == "":
				break
			if entry.find(ip) == 0:
				p = entry.find(':')
				pcMAC = entry[p - 2:p + 15]
				if pcMAC != "00:00:00:00:00:00":
					file.close()
					return pcMAC
		file.close()
		return None

	def isAlive(self):
		ip = "%s.%s.%s.%s" % (tuple(cfg.ip.value))
		self.readAlive(ip)

	def readAlive(self, ip):
		res = os.system("ping -c 1 -W 1 %s >/dev/null 2>&1" % (ip))
		if not res:
			self["0"].setPixmapNum(1)
			return True
		else:
			self["0"].setPixmapNum(0)
		return False		

	def fillCfg(self):
		if self.pcinfo.has_key('name'):
			cfg.name.value = self.pcinfo['name']
		if self.pcinfo.has_key('ip'):
			cfg.ip.value = self.convertIP(self.pcinfo['ip'])
		if self.pcinfo.has_key('mac'):
			cfg.mac.value = self.pcinfo['mac']
		if self.pcinfo.has_key('system'):
			cfg.system.value = self.pcinfo['system']
		if self.pcinfo.has_key('user'):
			cfg.user.value = self.pcinfo['user']
		if self.pcinfo.has_key('passwd'):
			cfg.passwd.value = self.pcinfo['passwd']
		if self.pcinfo.has_key('bqdn'):
			cfg.bqdn.value = self.pcinfo['bqdn']

	# convert ip from a string to a list of int
	def convertIP(self, ip):
		strIP = ip.split('.')
		ip = []
		for x in strIP:
			ip.append(int(x))
		return ip

	def getBackupCfg(self):
		return [cfg.name.value, cfg.ip.value[:], cfg.mac.value, cfg.system.value, cfg.user.value, cfg.passwd.value, cfg.bqdn.value]

	def isChanges(self, old, new):
		for i in range(0, len(old)):
			if old[i] != new[i]:
				return True
		return False

	def ok(self):
#		current = self["config"].getCurrent()
		name = cfg.name.value
		if not self.isChanges(self.old, self.getBackupCfg()): # no changes in item pars, save cfg item only
			cfg.close.save()
			cfg.sort.save()
			ixpowerUt.configActualized = True
			self.close()
		elif self.remotepc.has_key(name) is True:
			self.session.openWithCallback(self.updateConfig, MessageBox, (_("A PC entry with this name already exists!\nUpdate existing entry and continue?")))
		else:
			self.session.openWithCallback(self.applyConfig, MessageBox, (_("Are you sure you want to add this PC?\n")))

	def updateConfig(self, ret=False): # update record
		if (ret == True):
			ixpowerUt.setRemotePCAttribute(cfg.name.value, "name", cfg.name.value)
			ixpowerUt.setRemotePCAttribute(cfg.name.value, "ip", cfg.ip.getText())
			ixpowerUt.setRemotePCAttribute(cfg.name.value, "mac", cfg.mac.value)
			ixpowerUt.setRemotePCAttribute(cfg.name.value, "system", cfg.system.value)
			ixpowerUt.setRemotePCAttribute(cfg.name.value, "user", cfg.user.value)
			ixpowerUt.setRemotePCAttribute(cfg.name.value, "passwd", cfg.passwd.value)
			ixpowerUt.setRemotePCAttribute(cfg.name.value, "bqdn", cfg.bqdn.value)

			self.session.openWithCallback(self.updateFinished, MessageBox, _("Your PC has been updated..."), type=MessageBox.TYPE_INFO, timeout=2)
			ixpowerUt.writePCsConfig()
			cfg.close.save()
			cfg.sort.save()
			ixpowerUt.configActualized = True
		else:
			self.close()

	def updateFinished(self, data):
		if data is not None and data is True:
			self.close()

	def applyConfig(self, ret=False): # new record
		if (ret == True):
			data = {'name': False, 'ip': False, 'mac': False, 'system': False, 'username': False, 'password': False, 'bqdn': False}
			data['name'] = cfg.name.value
			data['ip'] = cfg.ip.getText()
			data['mac'] = cfg.mac.value
			data['system'] = cfg.system.value
			data['user'] = cfg.user.value
			data['passwd'] = cfg.passwd.value
			data['bqdn'] = cfg.bqdn.value

			self.session.openWithCallback(self.applyFinished, MessageBox, _("Your new PC has been added."), type=MessageBox.TYPE_INFO, timeout=2)
			ixpowerUt.remotepc[cfg.name.value] = data
			ixpowerUt.remotepc_order.append(cfg.name.value)
			ixpowerUt.writePCsConfig()
			ixpowerUt.configActualized = True
		else:
			self.close()

	def applyFinished(self, data):
		if data is not None and data is True:
			self.close()

	def cancel(self):
		self.close()
