import datetime

class Duty:

	def __init__(self, day, month, year, type):
		self.day = day
		self.month = month
		self.year = year
		self.type = type
		self.nurses = []
		self.createDate()
		self.setDayName()
		self.hours = {}

	def createDate(self):
		date_time_str = str(self.year) + "-" + str(self.month) + "-" + str(self.day)
		self.date = datetime.datetime.strptime(date_time_str, '%Y-%m-%d')

	def setDayName(self):
		self.dayName = self.date.strftime("%A")

	def getDayName(self):
		return self.dayName