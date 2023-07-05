import ast
from parser_mo.core import Parser
import mushroom

def main(input_file):
    """
    
    """
    with open(input_file) as f:
        source = f.read()

    grammar_parser = Parser()
    nodes = grammar_parser.parse(source, input_file)
    code = compile(nodes, input_file, 'exec')

    exec(code)


if __name__ == "__main__":
    mushroom.Mushroom(main)