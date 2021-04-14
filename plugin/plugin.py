# for localized messages  	 
from . import _

from Plugins.Plugin import PluginDescriptor


def xpowerMain(session, **kwargs):
	import ui
	session.open(ui.xpower, plugin_path)


def Plugins(path, **kwargs):
	global plugin_path
	plugin_path = path
	result = [PluginDescriptor(name="XPower", description=_("Power management for Win/Linux PC's"), where=[PluginDescriptor.WHERE_EXTENSIONSMENU, PluginDescriptor.WHERE_PLUGINMENU], icon='plugin.png', fnc=xpowerMain)]
	return result
