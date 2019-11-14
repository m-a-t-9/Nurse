from Nurse import *

class Scheduler:

	def __init__(self):
		self.nurses = []

	def loadNurses(self, f):
		c = f.readlines()
		f.close()
		for i in range(len(c)):
			if i != 0:
				self.nurses.append(Nurse(c[i]))