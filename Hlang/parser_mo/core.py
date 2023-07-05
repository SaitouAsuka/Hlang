import ast
from rply import Token
from rply.token import SourcePosition
from rply.parsergenerator import ParserGenerator
from rply.errors import LexingError
from parser_mo.exceptions import HLangSyntaxError
from parser_mo.lexer import lexer, precedences, RULES
from parser_mo.lrparser import LRParser
from parser_mo.assistant import filter_anno_blankrow


class Parser:

    def __init__(self, lexer=lexer):
        self.lexer_ = lexer
        self.filename_ = ''
        self.anonfuncs_ = {}
        self.source_ = None


    def parse(self, source, filename=''):
        self.filename_ = filename
        source = filter_anno_blankrow(source)
        self.source_ = source.split("\n")
        try:
            tokens = self.lexer_.lex(source)
            nodes = self.parser_.parse(tokens, state=self)
        except LexingError as e:
            raise HLangSyntaxError(message='Unknown token is found', filename=self.filename_, lineno=e.getsourcepos().lineno, colno=e.getsourcepos().colno, source=self.source_)
        
        return nodes
    
    def getsourcepos(self, p):
        if isinstance(p, list):
            # 如果是多个token的list，返回第一个token
            if len(p) > 0:
                p = p[0]
        
        if isinstance(p, Token):
            if p.gettokentype() == '$end':
                # 如果p是结束位置，返回结束位置，否则返回当前位置
                return self.getendpos()
            return p.getsourcepos()
        
        if isinstance(p, ast.stmt) or isinstance(p, ast.expr):
            return SourcePosition(0, p.lineno, p.col_offset)
        
        return SourcePosition(0, 0, 0)

    def getendpos(self):
        idx = -1
        line = len(self.source_)
        column = len(self.source_[-1])
        return SourcePosition(idx, line, column)

    def getlineno(self, p):
        # 获取当前token的行数
        try:
            return self.getsourcepos(p).lineno
        except:
            return 0

    def getcolno(self, p):
        # 获取当前token的列数
        try:
            return self.getsourcepos(p).colno
        except:
            return 0

    def getpos(self, p):
        return {"lineno":self.getlineno(p), "col_offset":self.getcolno(p)}

    pg_ = ParserGenerator(RULES, precedence=precedences, cache_id='Hlang_grammar')

    # 定义BNF表达
    @pg_.production('start : stmt_list')
    def start(self, p):
        return ast.Module(body=p[0], type_ignores=[])
    

    @pg_.production('stmt_list : ')
    @pg_.production('stmt_list : stmt_list_')
    @pg_.production('stmt_list : stmt_list_ NEWLINE')
    @pg_.production('stmt_list : stmt_list_ ;')
    def stmt_list(self, p):
        if len(p) > 0:
            return p[0]
        
        return []
    

    @pg_.production('stmt_list_ : stmt')
    @pg_.production('stmt_list_ : stmt_list_ NEWLINE stmt')
    @pg_.production('stmt_list_ : stmt_list_ ; stmt')
    def stmt_list_(self, p):
        if len(p) == 1:
            return [p[0]]
        
        p[0].append(p[-1])
        return p[0]
    

    @pg_.production('stmt : expr_stmt')
    @pg_.production('stmt : assignment')
    @pg_.production('stmt : print_stmt')
    def common_stmt(self, p):
        return p[0]
    

    @pg_.production('print_stmt : PRINT ( expr )')
    def print_stmt(self, p):
        print_name_node = ast.Name('print', ctx=ast.Load(), **self.getpos(p))
        print_func_node = ast.Call(func=print_name_node, args=[p[2]], keywords=[], starargs=None, kwargs=None, **self.getpos(p))
        return ast.Expr(print_func_node, **self.getpos(p))


    @pg_.production('expr_stmt : bin_expr')
    def expr_stmt(self, p):
        return ast.Expr(p[0], **self.getpos(p))

    
    @pg_.production('assignment : ASSIGN name = expr')
    def assignment(self, p):
        p[1].ctx = ast.Store()
        return ast.Assign([p[1]], p[3], **self.getpos(p))
    

    @pg_.production('expr : bin_expr')
    @pg_.production('expr : name')
    @pg_.production('expr : number')
    def expr(self, p):
        return p[0]


    @pg_.production('expr : ( expr )')
    def expr(self, p):
        return p[1]

    @pg_.production('bin_expr : expr + expr')
    @pg_.production('bin_expr : expr - expr')
    @pg_.production('bin_expr : expr * expr')
    @pg_.production('bin_expr : expr / expr')
    @pg_.production('bin_expr : expr % expr')
    def bin_expr(self, p):
        mapper = {
            '+': ast.Add(),
            '-': ast.Sub(),
            '*': ast.Mult(),
            '/': ast.Div(),
            '%': ast.Mod(),
        }
        op = p[1].getstr()
        return ast.BinOp(p[0], mapper[op], p[2], **self.getpos(p))
    

    @pg_.production('name : IDENTIFIER')
    def name(self, p):
        id = p[0].getstr()
        name = ast.Name(id=id, ctx=ast.Load(), **self.getpos(p))
        return name
    

    @pg_.production('number : FLOAT_LITERAL')
    @pg_.production('number : INTER_LITERAL')
    def number(self, p):
        try:
            return ast.Num(int(p[0].getstr(), 0), **self.getpos(p))
        except ValueError:
            return ast.Num(float(p[0].getstr()), **self.getpos(p))


    parser_ = LRParser(pg_.build())
    if len(parser_.lr_tbl.rr_conflicts) > 0:
        print(parser_.lr_tbl.rr_conflicts)
    if len(parser_.lr_tbl.sr_conflicts) > 0:
        print(parser_.lr_tbl.sr_conflicts)