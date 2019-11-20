

class Nurse:

	def __init__(self, data, logger):
		self.logger = logger
		self.holidays = []
		self.dailyDuties = []
		self.nightlyDuties = []
		self.occupied = []
		self.availabilities = []
		self.extorsions = []
		
		self.name = data.split(",")[0]
		self.timejob = data.split(",")[1].rstrip()
		if len(data.split(",")) >= 3:
			self.setAvailabilities(data.split(",")[2])
		if len(data.split(",")) >= 4:
			self.setHolidays(data.split(",")[3])
		self.hours = 0
		self.logger.info("Nurse: created: " + self.name + " timejob: " + str(self.timejob))

	def setAvailabilities(self, data):
		if len(data) != 0:
			for day in data.split(";"):
				self.availabilities.append(day.rstrip())

	def setHolidays(self, data):
		if len(data) != 0:
			for day in data.split(";"):
				self.holidays.append(day.rstrip())

	def getHolidaysString(self):
		if len(self.holidays) == 0:
			return ""
		s = " "
		for day in self.holidays:
			s += str(day) + "   "
		return s

	def getAvailabilitiesString(self):
		if len(self.availabilities) == 0:
			return ""
		s = " "
		for day in self.availabilities:
			s += " " + str(day.replace("_","")) + "   "
		return s

	def printNurse(self):
		self.logger.info("NURSE: ")
		self.logger.info("NAME: " + self.name)
		self.logger.info("TIMEJOB: " + self.timejob)
		self.logger.info("HOLIDAYS:")
		self.logger.info(self.holidays)
		self.logger.info("DAILY DUTIES: ")
		self.logger.info(self.dailyDuties)
		self.logger.info("NIGHTLY DUTIES: ")
		self.logger.info(self.nightlyDuties)
		self.logger.info("AVAILABLE AT: ")
		self.logger.info(self.availabilities)

	def getPlannedHours(self):
		return (float(len(self.dailyDuties) + len(self.nightlyDuties)) * 12)

	def checkHoliday(self, day):
		if str(day) in self.holidays:
			return True
		return False

	def checkAvailability(self, day):
		if len(self.availabilities) == 0:
			return True
		if day in self.availabilities:
			return True
		return False

	def checkDuties(self):
		self.logger.info(self.name + " planned hours: " + str((float(len(self.dailyDuties) + len(self.nightlyDuties))) * 12))
		if (float(len(self.dailyDuties) + len(self.nightlyDuties)) + 1.0) * 12 < self.hours:
			return True
		return False
		

	def addDuty(self, day, type):
		if type == "D":
			self.dailyDuties.append(day)
		else:
			self.nightlyDuties.append(day)