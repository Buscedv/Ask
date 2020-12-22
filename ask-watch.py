import sys
import time
import ask
import os


os.system('clear')


def style_string(text,color='', bold=False):

	ret = text
	if color == 'red':
		ret = '\033[91m' + ret + '\033[0m'

	if color == 'green':
		ret = '\033[92m' + ret + '\033[0m'

	if color == 'yellow':
		ret = '\033[93m' + ret + '\033[0m'

	if color == 'blue':
		ret = '\033[94m' + ret + '\033[0m'

	if color == 'pink':
		ret = '\033[95m' + ret + '\033[0m'

	if bold:
		ret = '\033[1m'  + ret + '\033[0m'

	return ret


print('⚡' + style_string('Ask', color='red') + ' Watcher')
if len(sys.argv) >= 2:
	file_name = sys.argv[1]

	timeout = 5
	if len(sys.argv) >= 3 and sys.argv[2].isnumeric():
		timeout = int(sys.argv[2])

	previous = ''
	current = ''

	if os.path.isfile(os.getcwd() + '/' + file_name):
		print(style_string('Watching... (timeout ' + str(timeout) + ' seconds)', color='pink'))
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
	print(style_string('Please provide a script file!', color='red'))
