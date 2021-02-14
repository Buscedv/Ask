import sys

from ask import cfg


# Prints out text colorized and (optionally) as bold.
def style_print(text, color=None, styles=[], end='\n'):
	prefix = '\033['
	suffix = prefix + '0m'

	available_styles = {
		'bold': '1m'
	}

	colors = {
		'red': '91m',
		'green': '92m',
		'blue': '94m',
		'gray': '90m'
	}

	result = str(text)

	if color in colors:
		result = prefix + colors[color] + result + suffix

	for style in styles:
		result = prefix + available_styles[style] + result + suffix

	print(result, end=end)


def initial_print():
	print('🌳', end='')
	style_print('Ask', color='green')


def print_transpilation_result(source_lines, time_result, for_error=False):
	color = 'green' if not for_error else 'red'

	style_print('\t- Transpiled ', color, end='')
	print(f'{len(source_lines)} lines in ~', end='')
	style_print(time_result, color='blue', end='')
	print(' seconds.')


def set_dev_status():
	if len(sys.argv) > 2:
		flag = sys.argv[2]
		if flag == '-d':
			cfg.is_dev = True
