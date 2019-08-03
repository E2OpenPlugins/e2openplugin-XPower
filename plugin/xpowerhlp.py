from . import _

from Screens.Screen import Screen
from Components.ActionMap import ActionMap
from Components.ScrollLabel import ScrollLabel
from Components.Button import Button
from Components.Label import Label
from Components.Pixmap import Pixmap

import ui
		
l1  = "\n"
l2 = "\n" * 2
l3 = "\n" * 3
s6  = " " * 6
s8  = " " * 8


class xpowerHelp(Screen):
	skin = """
	<screen position="center,center" size="560,420" title="XPower Help" >

		<ePixmap name="red"    position="0,0"   zPosition="2" size="140,40" pixmap="buttons/red.png" transparent="1" alphatest="on" />
		<ePixmap name="green"  position="140,0" zPosition="2" size="140,40" pixmap="buttons/green.png" transparent="1" alphatest="on" />
		<ePixmap name="yellow" position="280,0" zPosition="2" size="140,40" pixmap="buttons/yellow.png" transparent="1" alphatest="on" /> 
		<ePixmap name="blue"   position="420,0" zPosition="2" size="140,40" pixmap="buttons/blue.png" transparent="1" alphatest="on" /> 

		<widget name="key_red" position="0,0" size="140,40" valign="center" halign="center" zPosition="4"  foregroundColor="white" font="Regular;20" transparent="1" shadowColor="background" shadowOffset="-2,-2" /> 
		<widget name="key_green" position="140,0" size="140,40" valign="center" halign="center" zPosition="4"  foregroundColor="white" font="Regular;20" transparent="1" shadowColor="background" shadowOffset="-2,-2" /> 
		<widget name="key_yellow" position="280,0" size="140,40" valign="center" halign="center" zPosition="4"  foregroundColor="white" font="Regular;20" transparent="1" shadowColor="background" shadowOffset="-2,-2" />
		<widget name="key_blue" position="420,0" size="140,40" valign="center" halign="center" zPosition="4"  foregroundColor="white" font="Regular;20" transparent="1" shadowColor="background" shadowOffset="-2,-2" />

		<widget name="HelpScrollLabel" position="20,50" size="520,300" font="Regular;20" scrollbarMode="showOnDemand"/>

		<ePixmap pixmap="~/img/author.png" position="20,360" zPosition="2" size="25,25" />
		<widget name="version" position="50,365" size="100,20" zPosition="2" foregroundColor="white" font="Regular;16" /> 

		<ePixmap pixmap="div-h.png" position="0,396" zPosition="1" size="560,2" />
		<ePixmap alphatest="on" pixmap="icons/clock.png" position="480,403" size="14,14" zPosition="3"/>
		<widget font="Regular;18" halign="left" position="505,400" render="Label" size="55,20" source="global.CurrentTime" transparent="1" valign="center" zPosition="3">
			<convert type="ClockToText">Default</convert>
		</widget>

		<widget name="statusbar" position="10,400" size="470,20" font="Regular;18" />

	</screen>"""

	def __init__(self, session, plugin_path):
		self.skin_path = plugin_path
		Screen.__init__(self, session)

		self["key_red"] = Button(_("Close"))
		self["key_green"] = Button(_("All"))
		self["key_yellow"] = Button(_("Setup"))
		self["key_blue"] = Button(_("Hotkeys"))

		self["version"] = Label()
		self["statusbar"] = Label()
		self["HelpScrollLabel"] = ScrollLabel()

		self["XPowerActions"] = ActionMap(["XPowerActions"],
			{
				"cancel": self.close,
				"red": self.close,
				"green": self.whole,
				"yellow": self.setup,
				"blue": self.hotkeys,
				"ok": self.close,
				"up": self["HelpScrollLabel"].pageUp,
				"down": self["HelpScrollLabel"].pageDown,
			}, -1)

		self.setTitle(_("XPower Help"))
		self["version"].setText(_("Version") + ": %s" % (ui.version))
		self.whole()

	def hotkeys(self):
		self["HelpScrollLabel"].setText(self.hotkeysTxt())

	def setup(self):
		self["HelpScrollLabel"].setText(self.installTxt())

	def whole(self):
		self["HelpScrollLabel"].setText(self.hlpTxt() + self.hotkeysTxt() + self.installTxt())

	def hlpTxt(self):
		text  = l1 + s8 
		text += _("Welcome in plugin XPower for remote power management PC's. This plugin knows sending Magic Packet and control power status of PC.") + l1
		text += l1 + s8 
		text += _("Each operation system using its own comunication and own power managenent. There in settings of each PC item must be set true value.") + l1
		text += l1 + s8 
		text += _("If are on PC installed more OS, then create more PC's items. Priority key is name of PC.") + l1
		text += _("Dont forget, that not all mode must be supported by Your hardware!") + l2
		text += _("XPower plugin knows:") + l2 
		text += s6
		text += _("WakeUp") + l1
		text += s6
		text += _("Shutdown") + ", " + _("Reboot") + ", " + _("Abort shutdown / reboot") + l1
		text += s6
		text += _("Suspend") + ", " + _("Hibernate") + l2
		text += _("Do not forget, that Suspend and Hibernate are hardware, BIOS and drivers dependents.") + l2
		return text

	def installTxt(self):
		text =  "\t" + _("Setup") + ":" + l1
		text += _("Linux") + l2
		text += _("- install telnetd with:") + "  " + ("sudo apt-get install telnetd") + l2
		text += _("Windows 7/8") + l2
		text += _("- enable the Telnet Server") + l1
		text += _("- set Telnet server service to Automatic and run it") + l1
		text += _("- for Win8 enable ping (Firewall-Adwanced settings-Inbound Rules ... File and Printer Sharing (Echo Request - ICMPv4/6-In) to Yes") + l2
		text += _("Windows XP") + l2
		text += _("- set Telnet in Services to Automatic and run it") + l1 
		text += _("- there in Firewall add tcp port 23 for telnet") + l2
		text += _("Windows XP via net rpc") + l2
		text += _("- must be installed actual compiled \"net\" command. Problem is, that size of this file is over 8MB and some box have not enought memory for it") + l1
		text += _("- this way knows Shutdown, Reboot and Abort only!") + l3
		text += _("Note:\n telnet is easy way, but it is not safe protocol! Disable telnet port 23 on Your router, if it is possible!") + l3
		return text

	def hotkeysTxt(self):
		text = "\t" + _("Hotkeys") + ":" + l2
		text += "BouqUp\t" + _("WakeUp") + l1
		text += "BouqDown\t" + _("User defined...") + l1
		text += "1\t" + _("WakeUp") + l1
		text += "2\t" + _("Suspend") + l1
		text += "3\t" + _("Shutdown") + l1
		text += "5\t" + _("Hibernate") + l1 
		text += "6\t" + _("Reboot") + l1
		text += "0\t" + _("Abort shutdown / reboot") + l1
		text += "Menu\t" + _("Select action") + l2
		return text

