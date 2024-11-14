from tree_sitter import  Language, Parser
import tree_sitter_python as tspython
from tree_sitter_languages import get_parser

code = """
def main():
    print("Hello from fastdaimacodeassist!")


if __name__ == "__main__":
    main()
"""

print(bytes(code, 'utf-8'))

lang = Language(tspython.language())

print(lang)

parser = Parser(language=lang)

data = parser.parse(bytes(code, 'utf-8')) 
print(data)

