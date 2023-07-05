from rply import LexerGenerator
import re


RULES = {
    'FLOAT_LITERAL':(r'\d+\.\d+', None),
    'INTER_LITERAL':(r'\d+', None),
    'ASSIGN':(r'\bhsay\b', None),
    'PRINT': (r'\bhshow\b', None),
    'IDENTIFIER':(r'[_a-zA-Z][_a-zA-Z0-9]*', None),
    '(': (r'\(', None),
    ')': (r'\)', None),
    '=': (r'=', None),
    '+': (r'\+', None),
    '-': (r'-', None),
    '*': (r'\*', None),
    '%': (r'%', None),
    '/': (r'/', None),
    ';': (r';', None),
    'NEWLINE': (r'\n', None),
}

precedences = [
    ('nonassoc', ['(']),
    ('left', ['+', '-']),
    ('left', ['*', '/', '%']),
]


lg = LexerGenerator()

for token_id, (pattern, flags) in RULES.items():
    if flags is None:
        lg.add(token_id, pattern)
    else:
        lg.add(token_id, pattern, flags=flags)

# 注册一些忽视不处理的字符譬如空格等
# 忽略所有的换行符外空字符
lg.ignore(r'[ \t\r]+')
# 忽略空行
lg.ignore(r'\s+\n$')
# 忽略注释, 注释符号 //
lg.ignore('^#!.*')
lg.ignore(r'//[^\n]*')
# 忽略注释块 /*  */
lg.ignore(r'/\*.*?\*/', flags=(re.DOTALL))

lexer = lg.build()