# coding=utf-8
from __future__ import absolute_import

### (Don't forget to remove me)
# This is a basic skeleton for your plugin's __init__.py. You probably want to adjust the class name of your plugin
# as well as the plugin mixins it's subclassing from. This is really just a basic skeleton to get you started,
# defining your plugin as a template plugin, settings and asset plugin. Feel free to add or remove mixins
# as necessary.
#
# Take a look at the documentation on what other plugin mixins are available.
import json
import logging
import socket

import octoprint.plugin
from zeroconf import ZeroconfServiceTypes, Zeroconf, ServiceBrowser, ServiceStateChange, BadTypeInNameException

from octoprint_um3.Ultimaker3Printer import Ultimaker3Printer


class Um3Plugin(octoprint.plugin.SettingsPlugin,
                octoprint.plugin.AssetPlugin,
                octoprint.plugin.TemplatePlugin,
				octoprint.plugin.StartupPlugin,
				octoprint.plugin.SimpleApiPlugin):

	def __init__(self):
		self._logger = logging.getLogger("octoprint.plugins.um3")
		self.zeroconf = Zeroconf()
		self.service_type = "_ultimaker._tcp.local."
		self.browser = ServiceBrowser(self.zeroconf, self.service_type, handlers=[self.on_service_state_change])
		self.printers = []
		self.selected_printer = None

	# StartupPlugin

	def on_after_startup(self):
		printer_setting = self._settings.get(["printer"])
		if printer_setting:
			printer = self.read_printer_info(printer_setting)
			if printer :
				self._logger.info("Printer found in config: " + printer.__str__())
				self.selected_printer = printer
			else :
				self._logger.info("Unable to find printer " + printer_setting)

	##~~ SettingsPlugin mixin

	def get_settings_defaults(self):
		return dict(
			printer = ""
		)

	##~~ AssetPlugin mixin

	def get_assets(self):
		# Define your plugin's asset files to automatically include in the
		# core UI here.
		return dict(
			js=["js/um3.js"],
			css=["css/um3.css"],
			less=["less/um3.less"]
		)

	##~~ Softwareupdate hook

	def get_update_information(self):
		# Define the configuration for your plugin to use with the Software Update
		# Plugin here. See https://github.com/foosel/OctoPrint/wiki/Plugin:-Software-Update
		# for details.
		return dict(
			um3=dict(
				displayName="Ultimaker3 Plugin",
				displayVersion=self._plugin_version,

				# version check: github repository
				type="github_release",
				user="pbackx",
				repo="OctoPrint-Um3",
				current=self._plugin_version,

				# update method: pip
				pip="https://github.com/pbackx/OctoPrint-Um3/archive/{target_version}.zip"
			)
		)

	# octoprint.plugin.SimpleApiPlugin

	def on_api_get(self, request):
		return json.dumps([printer.toDict() for printer in self.printers])

	# internal methods

	def on_service_state_change(self, zeroconf, service_type, name, state_change):
		self._logger.info("Printer %s state changed: %s" % (name, state_change))

		if state_change is ServiceStateChange.Added:
			printer = self.read_printer_info(name)
			if printer :
				self.printers.append(printer)
				self._logger.info("Found " + printer.__str__())
				if name == self._settings.get(["printer"]):
					self.selected_printer = printer
		if state_change is ServiceStateChange.Removed:
			pass #TODO

		self._plugin_manager.send_plugin_message(self._identifier, [printer.toDict() for printer in self.printers])

	def read_printer_info(self, service_name):
		try:
			info = self.zeroconf.get_service_info(self.service_type, service_name)
			if info:
				address = socket.inet_ntoa(info.address)
				port = info.port
				name = "N/A"
				if info.properties:
					name = info.properties['name']
				else:
					self._logger.info("No properties found")
				return Ultimaker3Printer(service_name, address, port, name)
			else:
				self._logger.info("Could not fetch printer info")
				return None
		except BadTypeInNameException:
			self._logger.info("BadTypeInNameException while trying to load the printer info for " + service_name)
			return None


# If you want your plugin to be registered within OctoPrint under a different name than what you defined in setup.py
# ("OctoPrint-PluginSkeleton"), you may define that here. Same goes for the other metadata derived from setup.py that
# can be overwritten via __plugin_xyz__ control properties. See the documentation for that.
__plugin_name__ = "Ultimaker3 Plugin"

def __plugin_load__():
	global __plugin_implementation__
	__plugin_implementation__ = Um3Plugin()

	global __plugin_hooks__
	__plugin_hooks__ = {
		"octoprint.plugin.softwareupdate.check_config": __plugin_implementation__.get_update_information
	}

