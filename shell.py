import os
import shlex
import sys

class Shell:
	def __init__(self):
		self.exit_status = False
		self.commands  = {}
		self.pids = []
		
		#built in commands
		self.commands["cd"] = self.cd
		self.commands["exit"] = self.exit

		self.main_loop()

	def tokenize(self, func):
		return shlex.split(func)

	def execute(self, tokens,bg):
		pid = os.fork()

		#child
		if pid == 0:
			os.execvp(tokens[0], tokens)
		
		#parent
		elif pid > 0:
			while True:
				#If background requested
				pid, status = os.waitpid(pid, 0)
				if bg:
					break
				#If not background
				else:
					pid = 0	
					if os.WIFEXITED(status) or os.WIFSIGNALED(status):
						break
		
		return pid

	def executeBuiltIn(self, tokens):
		name = tokens[0]
		args = tokens[1:]
		self.commands[name](args)
		return False

	def cd(self, args):
		os.chdir(args[0])
		return False

	def exit(self, args):
		self.exit_status = True
		return self.exit_status
			
	def main_loop(self):
		while self.exit_status == False:
			
			#check background child process
			for i in self.pids:
				result = os.waitpid(pid, os.WNOHANG)
				#has exited
				if result[0] != 0:
					print "Child " + result[0] + " has exited with status " + result[1]
					self.pids.remove(i)
			#display prompt
			sys.stdout.write('> ')
			sys.stdout.flush()
	
			#read prompt
			try:
				func = raw_input()
			except Exception as e:
				func = "exit"
				if e.__class__.__name__ == "EOFError":
					break	
			
			#check if bg requested
			if func[-1] == "&":
				bg = True
				func= func[:-1] #remove &
			else:
				bg = False


			#tokenize
			tokens = self.tokenize(func)

			#execute command
			if tokens[0] in self.commands:
				self.executeBuiltIn(tokens)
			else:
				pid = self.execute(tokens, bg)
				#add background pids
				if pid != 0:
					self.pids.append(pid)
s = Shell()

