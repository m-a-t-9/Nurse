from Nurse import *
from Duty import *
class Scheduler:

	def __init__(self):
		self.nurses = []
		self.month = []

	def loadNurses(self, f):
		c = f.readlines()
		f.close()
		for i in range(len(c)):
			if i != 0:
				self.nurses.append(Nurse(c[i]))
				

	def createMonth(self, numberOfDates):
		for i in range(numberOfDates):
			self.month.append(Duty((i+1), "d"))
			self.month.append(Duty((i+1), "n"))
		for duty in self.month:
			print("Day: " + str(duty.day))
		
	def schedule(self):
		j = 0
		end = []
		for i in range(len(self.month)):
			print("\nSchedulling day " + str(self.month[i].day) + " " + self.month[i].type)
			while len(self.month[i].nurses) < 3 and len(end) != len(self.nurses):
				if j < len(self.nurses):
					if self.nurses[j].checkDuties():
						if not self.nurses[j].checkHoliday(self.month[i].day) and self.nurses[j].checkAvailability(self.month[i].day):
							self.nurses[j].addDuty(self.month[i].day, self.month[i].type)
							self.month[i].nurses.append(self.nurses[j])
							print(self.nurses[j].name + " assigned to duty in " + str(self.month[i].day))
						else:
							print("Nurse " + self.nurses[j].name + " is not available in this day " + str(self.month[i].day))
					else:
						print("Nurse " + self.nurses[j].name + " already have 12 duties in this  month")
						if self.nurses[j].name not in end:
							end.append(self.nurses[j].name)
					j += 1
				else:
					j = 0
			if len(end) == len(self.nurses):
				print("There is not enough nurses in this month to schedule work")
				break
		print("Done :D\n\n\n")

		self.printSchedules()
	
	def getNumberOfNurse(self):
		return len(self.nurses)

	def getNurse(self, name):
		for nurse in self.nurses:
			if nurse.name == name:
				return nurse

	def printSchedules(self):
		for nurse in self.nurses:
			print("^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^")
			print("Nurse: " + nurse.name)
			print("DailyDuties: ")
			print(nurse.dailyDuties)
			print("NightlyDuties: ")
			print(nurse.nightlyDuties)
			print("^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^")