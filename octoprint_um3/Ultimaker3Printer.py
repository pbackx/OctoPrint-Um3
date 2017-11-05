import json


class Ultimaker3Printer:
	def __init__(self, service_name, address, port, name):
		self.service_name = service_name
		self.address = address
		self.port = port
		self.name = name

	def webcam_url(self):
		return "http://{0.address}:8080/?action=stream".format(self)

	def toDict(self):
		return dict(
			service_name = self.service_name,
			address = self.address,
			port = self.port,
			name = self.name,
			webcam_url = self.webcam_url()
		)

	def __str__(self):
		return "UM3 {0.name} at {0.address}.".format(self)
