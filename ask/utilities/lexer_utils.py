from ask import cfg


# Figures out if a given name should be lexed as a keyword or variable token.
from ask.utilities import translators


def lex_var_keyword(tokens, tmp):
	collect = False
	collect_ends = []
	include_collect_end = False

	if tmp:
		if tmp in cfg.keywords:
			tokens.append(['KEYWORD', translators.transpile_keyword(tmp)])
		elif tmp in cfg.special_keywords.keys():
			tokens.append([cfg.special_keywords[tmp]['type'], tmp])
			collect = cfg.special_keywords[tmp]['collect']
			collect_ends = cfg.special_keywords[tmp]['collect_ends']
			include_collect_end = cfg.special_keywords[tmp]['include_collect_end']
		else:
			tokens.append(['VAR', tmp])
		tmp = ''
	return tokens, tmp, collect, collect_ends, include_collect_end
