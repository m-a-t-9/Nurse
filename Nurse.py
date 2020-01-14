

class Nurse:

	def __init__(self, data, logger):
		self.logger = logger
		self.holidays = []
		self.dailyDuties = []
		self.nightlyDuties = []
		self.shortDuties = []
		self.occupied = []
		self.availabilities = []
		self.extorsions = []
		self.sundays = 0
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

	def getUnplannedHours(self):
		return self.hours - self.getPlannedHours()

	def getPlannedHours(self):
		return (float(len(self.dailyDuties) + len(self.nightlyDuties)) * 12)

	def checkHoliday(self, duty):
		if str(duty.day) + "." + self.monthFix(duty.month) in self.holidays:
			self.logger.info("Nurse " + self.name + " is on a holiday at day " + str(duty.day) + "." + self.monthFix(duty.month))
			return True
		if duty.type == "N":
			if str(duty.day + 1) in self.holidays:
				self.logger.info("Nurse " + self.name + " is on a holiday next day. Nightly duty cannot be assigned at " + str(duty.day))
				return True
		if duty.dayName == 'sobota' or duty.dayName == 'niedziela':
			return self.checkIsNextWeekOff([duty.dayName, duty.day]) 

	def monthFix(self, month):
		if len(str(month)) == 1:
			return "0" + str(month)
		else:
			return str(month)

	def checkPreviousDay(self, consideredDay):
		self.logger.info("Nurse: checkPreviousDay: nurse " + self.name + " consideredDay: " + consideredDay[0] + " " + str(consideredDay[1]))
		if consideredDay[0] == "N":
			if (consideredDay[1]) in self.dailyDuties:
				self.logger.info("Nurse: checkPreviousDay: nurse " + self.name + " has a dailyDuty in this day " + str(consideredDay[1]))
				return True
			elif (consideredDay[1] + 1) in self.dailyDuties:
				self.logger.info("Nurse: checkPreviousDay: nurse " + self.name + " has a dailyDuty next day " + str(consideredDay[1]))
				return True
			elif (consideredDay[1] - 1) in self.nightlyDuties:# and str(consideredDay[1] - 2) in self.nightlyDuties:
				self.logger.info("Nurse: checkPreviousDay: nurse " + self.name + " more than 2 nightly duties in series " + str(consideredDay[1]))
				return True
			elif (consideredDay[1] + 1) in self.nightlyDuties:# and str(consideredDay[1] + 2) in self.nightlyDuties:
				self.logger.info("Nurse: checkPreviousDay: nurse " + self.name + " more than 2 nightly duties in series " + str(consideredDay[1]))
				return True
		elif consideredDay[0] == "D":
			if (consideredDay[1]) in self.nightlyDuties:
				self.logger.info("Nurse: checkPreviousDay: nurse " + self.name + " has a nigthly duty in this day " + str(consideredDay[1]))
				return True
			elif (consideredDay[1] - 1) in self.nightlyDuties:
				self.logger.info("Nurse: checkPreviousDay: nurse " + self.name + " has a nigthly duty in this day " + str(consideredDay[1]))
				return True
			elif (consideredDay[1] - 1) in self.dailyDuties:# and str(consideredDay[1] - 2) in self.dailyDuties:
				self.logger.info("Nurse: checkPreviousDay: nurse " + self.name + " more than 2 daily duties in series " + str(consideredDay[1]))
				return True
			elif (consideredDay[1] + 1) in self.dailyDuties:# and str(consideredDay[1] + 2) in self.dailyDuties:
				self.logger.info("Nurse: checkPreviousDay: nurse " + self.name + " more than 2 daily duties in series " + str(consideredDay[1]))
				return True
		self.logger.info("Nurse: checkPreviousDay: nurse " + self.name + " has not a nigthly duty in this day " + str(consideredDay[1]))
		return False

	def checkSundays(self):
		return self.sundays

	def checkIsNextWeekOff(self, consideredDay):
		daysRange = []
		if consideredDay[0] == 'sobota':
			daysRange = [consideredDay[1] + 2, consideredDay[1] + 6]
			self.logger.info("Nurse: checkIsNextWeekOff: considering saturday")
		elif consideredDay[0] == 'niedziela':
			daysRange = [consideredDay[1] + 1, consideredDay[1] + 6]
			self.logger.info("Nurse: checkIsNextWeekOff: considering sunday")
		for i in range(daysRange[0], daysRange[1]):
			if str(i) not in self.holidays:
				self.logger.info("Nurse: checkIsNextWeekOff: False")
				return False
		self.logger.info("Nurse: checkIsNextWeekOff: True")
		return True

	def checkAvailability(self, day):
		if len(self.availabilities) == 0:
			return True
		if day in self.availabilities:
			return True
		self.logger.info("Nurse is not available")
		return False

	def checkDuties(self):
		self.logger.info(self.name + " planned hours: " + str((float(len(self.dailyDuties) + len(self.nightlyDuties))) * 12))
		if (float(len(self.dailyDuties) + len(self.nightlyDuties)) + 1.0) * 12 < self.hours:
			return True
		return False
		
	def checkWeek(self, week):
		dutyCounter = 0
		for i in range(week[0], week[1] + 1):
			if self.checkIsAlreadyPlanned(i):
				dutyCounter += 1
		self.logger.debug("Nurse: dutyCounter: " + str(dutyCounter))
		if dutyCounter == 3:
			self.logger.info("Nurse " + self.name + " has already planned 4 duties in this week")
			return True
		else:
			return False

	def checkIsAlreadyPlanned(self, day):
		self.logger.debug("Nurse: checkIsAlreadyPlanned " + str(day))
		if day in self.dailyDuties or day in self.nightlyDuties:
			self.logger.debug("Return True")
			return True
		else:
			return False

	def addDuty(self, day, type, dayName):
		if type == "D":
			self.dailyDuties.append(day)
		else:
			self.nightlyDuties.append(day)
		if dayName == "niedziela":
			self.sundays += 1