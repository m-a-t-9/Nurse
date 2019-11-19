

class Nurse:

	def __init__(self, data):
		self.holidays = []
		self.dailyDuties = []
		self.nightlyDuties = []
		self.occupied = []
		self.availabilities = []
		self.extorsions = []
		
		self.name = data.split(",")[0]
		self.timejob = data.split(",")[1]
		if len(data.split(",")) >= 3:
			self.setAvailabilities(data.split(",")[2])
		if len(data.split(",")) >= 4:
			self.setHolidays(data.split(",")[3])
		self.printNurse()
		

	def setAvailabilities(self, data):
		if len(data) != 0:
			for day in data.split(";"):
				self.availabilities.append(day.rstrip())

	def setHolidays(self, data):
		if len(data) != 0:
			for day in data.split(";"):
				self.holidays.append(day.rstrip())

	def printNurse(self):
		print("KRANKENSCHWESTER: ")
		print("NAME: " + self.name)
		print("TIMEJOB: " + self.timejob)
		print("HOLIDAYS:")
		print(self.holidays)
		print("DAILY DUTIES: ")
		print(self.dailyDuties)
		print("NIGHTLY DUTIES: ")
		print(self.nightlyDuties)
		print("AVAILABLE AT: ")
		print(self.availabilities)

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
		if (len(self.dailyDuties) + len(self.nightlyDuties)) < 12 * float(self.timejob):
			return True
		return False

	def addDuty(self, day, type):
		if type == "d":
			self.dailyDuties.append(day)
		else:
			self.nightlyDuties.append(day)