from Nurse import *
from Duty import *
import time
nurses = []
month = []

def createNurses(filename):
	f = open(filename, "r")
	c = f.readlines()
	f.close()
	for i in range(len(c)):
		if i != 0:
			nurses.append(Nurse(c[i]))
			#nurses[-1].printNurse()
	#print("Created %d nurses", len(nurses))

def createMonth(numberOfDates):
	for i in range(2*numberOfDates):
		if i % 2 == 0:
			month.append(Duty((i+1), "d"))
		else:
			month.append(Duty((i+1), "n"))
	#print(month)

def schedule():
	j = 0
	end = []
	for i in range(len(month)):
		print("\nSchedulling day" + str(i/2) + " " + month[i].type)
		while len(month[i].nurses) < 3 and len(end) != len(nurses):
			if j < len(nurses):
				if nurses[j].checkDuties() and not nurses[j].checkHoliday(month[i].day):
					nurses[j].addDuty(month[i].day, month[i].type)
					month[i].nurses.append(nurses[j])
					#print("Selected Nurse: ")
					print(nurses[j].name)
					j += 1
				else:
					print("KRANKENSCHWESTER " + nurses[j].name + " already have 12 duties in this  month")
					if nurses[j].name not in end:
						end.append(nurses[j].name)
					j += 1
			else:
				j = 0
			time.sleep(0.1)	
		if len(end) == len(nurses):
			break
	print("Done :D\n\n\n")

	printSchedules()

def printSchedules():
	for nurse in nurses:
		print("^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^")
		print("Nurse: " + nurse.name)
		print("DailyDuties: ")
		print(nurse.dailyDuties)
		print("NightlyDuties: ")
		print(nurse.nightlyDuties)
		print("^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^")

def main():
	createNurses("nurses.nur")
	createMonth(30)
	schedule()

if __name__ == "__main__":
	main()