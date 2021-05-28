# coding=utf-8
from typing import List

from ask_lang import cfg


# Prints out text colorized and (optionally) as bold.
def style_print(text, color: str = None, styles: List[str] = None, end: str = '\n'):
	if styles is None:
		styles = []

	prefix = '\033['
	suffix = prefix + '0m'

	available_styles = {
		'bold': '1m'
	}

	colors = {
		'red': '91m',
		'green': '92m',
		'blue': '94m',
		'gray': '90m',
		'yellow': '33m'
	}

	result = str(text)

	if color in colors:
		result = prefix + colors[color] + result + suffix

	for style in styles:
		result = prefix + available_styles[style] + result + suffix

	print(result, end=end)


def initial_print():
	style_print('🌳Ask', styles=['bold'], color='green', end=' ')
	print(f'{cfg.project_information["version"]}')


def transpilation_result(source_lines: str, time_result: float, for_error: bool = False):
	color = 'green' if not for_error else 'red'

	style_print('\t- Transpiled ', color, end='')
	print(f'{len(source_lines)} lines in ~', end='')
	style_print(time_result, color='blue', end='')
	print(' seconds.')
