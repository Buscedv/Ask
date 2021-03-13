# coding=utf-8
from typing import Any, List

from ask_lang import cfg
from ask_lang.utilities import files


def load():
	cfg.ask_config = files.get_ask_config(files.get_root_from_file_path(files.output_file_path()))


def get(key_tree: List[str], not_found) -> Any:
	try:
		current_position = cfg.ask_config[key_tree[0]]

		if len(key_tree) > 1:
			for key in key_tree[1:]:
				current_position = current_position[key]

		return current_position
	except Exception:
		return not_found
