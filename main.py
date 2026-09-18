"""Command line entry point for the Python-only SimpleLang interpreter.

Run: python main.py                 (built-in sample)
     python main.py example.sl      (source file)
     python main.py example.sl --ast
"""
import argparse
from pathlib import Path
from pprint import pprint

from errors import LangError
from interpreter import run


EXAMPLE = r'''
// SimpleLang sample: functions, conditions, and recursion
func factorial(n) {
  if (n <= 1) {
    return 1;
  }
  return n * factorial(n - 1);
}
print(factorial(5));
'''


def main():
    arg_parser = argparse.ArgumentParser(description='SimpleLang: Python-only interpreter')
    arg_parser.add_argument('file', nargs='?', help='path to a .sl source file')
    arg_parser.add_argument('--ast', action='store_true', help='display the abstract syntax tree')
    args = arg_parser.parse_args()

    try:
        source = Path(args.file).read_text(encoding='utf-8') if args.file else EXAMPLE
        result = run(source)
        if args.ast:
            print('AST:')
            pprint(result['ast'], width=90)
            print('\nOutput:')
        print(result['output'] or '(program completed with no output)')
    except (LangError, RecursionError, OSError) as error:
        arg_parser.exit(1, f'Error: {error}\n')


if __name__ == '__main__':
    main()
