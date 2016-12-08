import os
import shlex
import sys

class Shell:
	def __init__(self):
		self.exit_status = False
		self.builtIn  = {}
		self.pids = []
		
		#built in commands
		self.builtIn["cd"] = self.cd
		self.builtIn["exit"] = self.exit

		self.main_loop()

	def tokenize(self, func):
		return shlex.split(func)

	def execute(self, bg):
		pid = os.fork()

		#child
		if pid == 0:

			#if redirected
			if self.redirect == "out":
				fd = os.open(self.targets[0], os.O_RDWR)
				os.dup2(fd, 1)
				os.close(fd)
				os.execvp(self.commands[0], self.commands)
			if self.redirect == "in":
				fd = os.open(self.targets[0], os.O_RDWR)
				os.dup2(fd, 0)
				os.close(fd)
				os.execvp(self.commands[0], self.commands)
			if self.redirect == "pipe":
				r, w = os.pipe()	#create r and w fds
				pid2 = os.fork()
				if pid2 == 0:
					os.dup2(w, 1)		#redirect output to w fd
					os.close(w)		#close w fd
					os.execvp(self.commands[0], self.commands)	#execute first command
				else:
					os.dup2(r, 0)		#redirect input from r fd
					os.close(r)		#close read fd 
					os.execvp(self.targets[0], self.targets) #execute second function
					while True:
						pid2, status = os.waitpid(pid2, 0)
						if os.WIFEXITED(status) or os.WIFSIGNALED(status):
							break
				
			else:
				os.execvp(self.commands[0], self.commands)
		
		#parent
		elif pid > 0:
			while True:
				#If background requested
				if bg:
					break
				#If not background
				else:
					pid, status = os.waitpid(pid, 0)
					pid = 0	
					if os.WIFEXITED(status) or os.WIFSIGNALED(status):
						break
		
		return pid

	def executeBuiltIn(self):
		name = self.commands[0]
		args = self.commands[1:]
		self.builtIn[name](args)
		return False

	def cd(self, args):
		os.chdir(args[0])
		return False

	def exit(self, args):
		self.exit_status = True
		return self.exit_status
	
	def readPrompt(self):
		try:
			func = raw_input()
		except Exception as e:
			func = "exit"
			if e.__class__.__name__ == "EOFError":
				return "EOFError"
		return func


	def checkBG(self):	
		for i in self.pids:
			try:	
				result = os.waitpid(i, os.WNOHANG)
				#if it has exited
				if result[0] != 0:
					print "Child " +str(result[0]) + " has exited with status " + str(result[1])
					self.pids.remove(i)

			except:
				self.pids.remove(i)
	
	def checkRedirects(self, tokens):
		self.redirect = "none"
		changed = 0

		for i in range(0, len(tokens)):
			if tokens[i] == ">":	
				self.redirect = "out"
				changed = i
				break
			elif tokens[i] == "<":
				self.redirect = "in"
				changed = i
				break
			elif tokens[i] == "|":
				self.redirect = "pipe"
				changed = i
				break

		if self.redirect != "none":
			self.commands = tokens[:changed]
			self.targets = tokens[changed + 1:]

		else:
			self.commands = tokens
			self.targets = []

	def main_loop(self):
		while self.exit_status == False:
			
			self.checkBG()

			#display prompt
			sys.stdout.write('> ')
			sys.stdout.flush()
	
			#read prompt
			func = self.readPrompt()
			if func == "EOFError":
				break	
			
			#check if no input
			if func == "":
				continue

			#check if bg requested
			if func[-1] == "&":
				bg = True
				func= func[:-1] #remove &
			else:
				bg = False
			

			#tokenize
			tokens = self.tokenize(func)
			
			#check redirects
			self.checkRedirects(tokens)

			#execute command
			if self.commands[0] in self.builtIn:
				self.executeBuiltIn()
			else:
				pid = self.execute(bg)
				#add background pids
				if pid != 0:
					self.pids.append(pid)
s = Shell()

