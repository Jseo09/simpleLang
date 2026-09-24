"""Command line entry point for the Python-only SimpleLang interpreter.

Run: python main.py                 (built-in sample)
     python main.py example.sl      (source file)
     python main.py example.sl --ast
"""
import argparse         # library to handle command line args
from pathlib import Path    # library to work with system paths
from pprint import pprint   # pretty-print library to improve readibility of nested functions

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
    arg_parser = argparse.ArgumentParser(description='SimpleLang: Python-based interpreter')        # creates parser object
    arg_parser.add_argument('file', nargs='?', help='path to a .sl source file')                    # optinal filename
    arg_parser.add_argument('--ast', action='store_true', help='display the abstract syntax tree')  # optinal flag
    args = arg_parser.parse_args()      # read user input

    try:
        source = Path(args.file).read_text(encoding='utf-8') if args.file else EXAMPLE      # read the file's text, otherwise, show above example
        result = run(source)        # reference run from interpreter.py    
        if args.ast:
            print('AST:')       
            pprint(result['ast'], width=90)     # print out ast, limit width 90 char
            print('\nOutput:')
        print(result['output'] or '(program completed with no output)')     # empty fallback output
    except (LangError, RecursionError, OSError) as error:       # RecursionError, OSError are python built-in exceptions
        arg_parser.exit(1, f'Error: {error}\n')                 # RecursionError triggered when call stack is too deep
                                                                # OSError relates to OS failure

if __name__ == '__main__':      # run when file executed, not imported
    main()
