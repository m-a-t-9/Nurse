from Nurse import *
from Duty import *
import calendar
from datetime import datetime



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
				

	def createMonth(self, numberOfDates, month):
		self.monthId = month
		self.numberOfDates = numberOfDates
		for i in range(numberOfDates):
			self.month.append(Duty((i+1), "D"))
			self.month.append(Duty((i+1), "N"))
		
	def schedule(self):
		self.calculateHours()
		self.setContractors()
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
						print("Nurse " + self.nurses[j].name + " already have all duties in this  month")
						if self.nurses[j].name not in end:
							end.append(self.nurses[j].name)
					j += 1
				else:
					j = 0
			if len(end) == len(self.nurses):
				print("There is not enough nurses in this month to schedule work")
				break
		print("Done :D\n\n\n")

		#self.printSchedules()
	
	def setContractors(self):
		for nurse in self.nurses:
			if float(nurse.timejob) == 0.0:
				for duty in nurse.availabilities:
					day = int(duty.split("_")[0])
					t = duty.split("_")[1]
					duty = self.getDuty(day, t)
					print(duty)
					if duty != None:
						print("SetContractors: adding duty: " + str(duty.day) + " to nurse " + nurse.name)
						nurse.addDuty(day, t)
						duty.nurses.append(nurse)
		#self.printSchedules()
					
	def getDuty(self, day, type):
		#print( "getDuty looking for : " + str(day) + " " + str(type))
		for duty in self.month:
			#print("Current loop duty: " + str(duty.day) + " " + str(duty.type))
			if int(duty.day) == int(day) and str(duty.type) == str(type):
				return duty
	
	def getNumberOfNurse(self):
		return len(self.nurses)

	def getNurse(self, name):
		for nurse in self.nurses:
			if nurse.name == name:
				return nurse

	def validateSchedule(self):
		self.validateNurses()
		self.validateDuties()
		
	def validateNurses(self):
		for nurse in self.nurses:
			nurse.checkWeeklyLimit()
	
	def calculateHours(self):
		year = int(datetime.now().strftime('%Y'))
		matrix = calendar.monthcalendar(year,self.monthId)
		num_sun = sum(1 for x in matrix if x[calendar.SUNDAY] != 0)
		num_sat = sum(1 for x in matrix if x[calendar.SATURDAY] != 0)
		print("SUNDAYS: " + str(num_sun))
		print("SATURDAYS: " + str(num_sat))
		self.workingDays = self.numberOfDates - num_sat - num_sun
		print("WORKING DAYS: " + str(self.workingDays))
		for nurse in self.nurses:
			print("Nurse timejob is " + str(nurse.timejob))
			if float(nurse.timejob) == 1.0 or float(nurse.timejob) == 0.5:
				
				nurse.hours = float(self.workingDays) * float(nurse.timejob) * 7.58
				print("Nurse: " + nurse.name + " should work in this month for " + str(nurse.hours))
		
	
	def validateDuties(self):
		pass

	def printSchedules(self):
		for nurse in self.nurses:
			print("^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^")
			print("Nurse: " + nurse.name)
			print("DailyDuties: ")
			print(nurse.dailyDuties)
			print("NightlyDuties: ")
			print(nurse.nightlyDuties)
			print("^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^")