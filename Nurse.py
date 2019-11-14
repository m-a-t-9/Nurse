

class Nurse:

	def __init__(self, data):
		self.name = data.split(",")[0]
		self.timejob = data.split(",")[1]
		self.holidays = []
		self.dailyDuties = []
		self.nightlyDuties = []

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

	def checkHoliday(self, day):
		if day in self.holidays:
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