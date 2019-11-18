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
		for i in range(2*numberOfDates):
			if i % 2 == 0:
				self.month.append(Duty((i+1), "d"))
			else:
				self.month.append(Duty((i+1), "n"))
		print(self.month)
		
	def schedule(self):
		j = 0
		end = []
		for i in range(len(self.month)):
			print("\nSchedulling day" + str(i/2) + " " + self.month[i].type)
			while len(self.month[i].nurses) < 3 and len(end) != len(self.nurses):
				if j < len(self.nurses):
					if self.nurses[j].checkDuties() and not self.nurses[j].checkHoliday(self.month[i].day):
						self.nurses[j].addDuty(self.month[i].day, self.month[i].type)
						self.month[i].nurses.append(self.nurses[j])
						#print("Selected Nurse: ")
						print(self.nurses[j].name)
						j += 1
					else:
						print("KRANKENSCHWESTER " + self.nurses[j].name + " already have 12 duties in this  month")
						if self.nurses[j].name not in end:
							end.append(self.nurses[j].name)
						j += 1
				else:
					j = 0
			if len(end) == len(self.nurses):
				break
		print("Done :D\n\n\n")

		self.printSchedules()
	
	def getNumberOfNurse(self):
		return len(self.nurses)


	def printSchedules(self):
		for nurse in self.nurses:
			print("^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^")
			print("Nurse: " + nurse.name)
			print("DailyDuties: ")
			print(nurse.dailyDuties)
			print("NightlyDuties: ")
			print(nurse.nightlyDuties)
			print("^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^")