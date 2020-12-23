import sys
import time
import ask
import os


os.system('clear')


ask.style_print('Ask', left_text='⚡', right_text=' Watcher', styles=['red'])
if len(sys.argv) >= 2:
	file_name = sys.argv[1]

	timeout = 5
	if len(sys.argv) >= 3 and sys.argv[2].isnumeric():
		timeout = int(sys.argv[2])

	previous = ''
	current = ''

	if os.path.isfile(os.getcwd() + '/' + file_name):

		ask.style_print('Watching... (timeout ' + str(timeout) + ' seconds)', styles=['pink'])
		ask.style_print('Press Ctrl+c to exit.', ends_with='\n\n')

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
	ask.style_print('Please provide a script file!', styles=['red'])
