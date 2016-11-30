class Shell:
	def __init__(self):
		self.exit_status = False
		
		self.main_loop()
	
	def main_loop(self):
		while self.exit_status == False:
			func = raw_input()	#read function name
			try:
				getattr(self, func)() 	#call function
			except EOFError:
				self.exit()
			except:
				print "Not a Valid Function"
	def exit(self):
		self.exit_status = True


s = Shell()
