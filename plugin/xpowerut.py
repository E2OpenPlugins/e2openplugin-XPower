from Screens.Screen import Screen
from Components.ConfigList import ConfigListScreen
from Components.Button import Button
from Components.Label import Label
import os
from os import path as os_path

from xml.etree.cElementTree import parse as cet_parse


XML_PCTAB = "/etc/enigma2/xpower.xml"

class xpowerUt(Screen):

	def __init__(self):
		self.remotepc = {}
		self.configActualized = False

	def getRemotePCPoints(self):
		self.remotepc = {}

		if not os_path.exists(XML_PCTAB):
			self.setDummyRecord()
			self.writePCsConfig()

		tree = cet_parse(XML_PCTAB).getroot()

		def getValue(definitions, default):
			ret = ""
			# How many definitions are present
			Len = len(definitions)
			return Len > 0 and definitions[Len-1].text or default
		# Config is stored in "host" element, read out PC
		for pc in tree.findall("host"):
			data = { 'name': False, 'ip': False, 'mac': False, 'system': False, 'user': False, 'passwd': False, 'bqdn': False }
			try:
				data['name'] = getValue(pc.findall("name"), _("PC")).encode("UTF-8")
				data['ip'] = getValue(pc.findall("ip"), "192.168.1.0").encode("UTF-8")
				data['mac'] = getValue(pc.findall("mac"), "00:00:00:00:00:00").encode("UTF-8")
				data['system'] = getValue(pc.findall("system"), "0").encode("UTF-8")
				data['user'] = getValue(pc.findall("user"), "administrator").encode("UTF-8")
				data['passwd'] = getValue(pc.findall("passwd"), "password").encode("UTF-8")
				data['bqdn'] = getValue(pc.findall("bqdn"), "0").encode("UTF-8")
				self.remotepc[data['name']] = data
			except Exception, e:
				print "[xpower] Error reading remotepc:", e

		self.checkList = self.remotepc.keys()
		if not self.checkList: 
		# exists empty file => create dummy record
			self.setDummyRecord()
		
		self.checkList = self.remotepc.keys()
		if not self.checkList:
			print "\n[XPower.py] self.remotepc without remotepc", self.remotepc
		else:
			self.checkList.pop()

	def setDummyRecord(self):
		data = { 'name': False, 'ip': False, 'mac': False, 'system': False, 'user': False, 'passwd': False, 'bqdn': False }
		data['name'] = _("PC")
		data['ip'] = "192.168.1.100"
		data['mac'] = "00:00:00:00:00:00"
		data['system'] = "0"
		data['user'] = "administrator"
		data['passwd'] = "password"
		data['bqdn'] = "0"
		self.remotepc[data['name']] = data

	def setRemotePCAttribute(self, pcpoint, attribute, value):
		print "setting for pcpoint", pcpoint, "attribute", attribute, " to value", value
		if self.remotepc.has_key(pcpoint):
			self.remotepc[pcpoint][attribute] = value

	def getPCsList(self):
		self.getRemotePCPoints()
		return self.remotepc

	def writePCsConfig(self):
		# Generate List in RAM
		list = ['<?xml version="1.0" ?>\n<xpower>\n']

		for name, data in self.remotepc.items():
			list.append(' <host>\n')
			list.append(''.join(["  <name>", data['name'], "</name>\n"]))
			list.append(''.join(["  <ip>", data['ip'], "</ip>\n"]))
			list.append(''.join(["  <mac>", data['mac'], "</mac>\n"]))
			list.append(''.join(["  <system>", data['system'], "</system>\n"]))
			list.append(''.join(["  <user>", data['user'], "</user>\n"]))
			list.append(''.join(["  <passwd>", data['passwd'], "</passwd>\n"]))
			list.append(''.join(["  <bqdn>", data['bqdn'], "</bqdn>\n"]))
			list.append(' </host>\n')

		list.append('</xpower>\n')

		file = None
		try:
			file = open(XML_PCTAB, "w")
			file.writelines(list)
		except Exception, e:
			print "[xpower plugin] Error Saving PC List:", e
		finally:
			if file is not None:
				file.close()

	def removePC(self, pcpoint):
		self.newremotepc = {}
		for name, data in self.remotepc.items():
			if name.strip() != pcpoint.strip():
				self.newremotepc[name] = data
		self.remotepc.clear()
		self.remotepc = self.newremotepc

ixpowerUt = xpowerUt()
