import sys
import time
import ask
import os

os.system('clear')
print('⚡' + '\033[92m' + '️Ask' + '\033[0m' + '-Watcher')
if len(sys.argv) >= 2:
	file_name = sys.argv[1]

	timeout = 5
	if len(sys.argv) >= 3:
		if sys.argv[2].isnumeric():
			timeout = int(sys.argv[2])

	previous = ''
	current = ''

	if os.path.isfile(os.getcwd() + '/' + file_name):
		print('\033[95m' +'Watching... (timeout ' + str(timeout) + ' seconds)' + '\033[0m')
		print('Press Ctrl+c to exit.\n')

		with open(file_name) as f:
			current = f.read()
			previous = current

		ask.startup(file_name)

		while True:
			with open(file_name) as f:
				current = f.read()
				if current != previous:
					ask.startup(file_name)
					previous = current

				time.sleep(5)
else:
	print('\033[91m' + 'Please provide a script file!' + '\033[0m')
