#!/usr/bin/env python3
"""Dictionary Utilities
"""

import sys
import argparse
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from django.conf import settings

__version__ = "0.1"
__status__ = "TEST"

class DictionaryUtils():
    """Utility class for handling dictionaries."""

    @staticmethod
    def get_dictionary():
        import pdb; pdb.set_trace

    @staticmethod
    def list_functions(parser):
        """List available functions and their help descriptions."""
        print('Available functions:')
        for action in parser._actions:
            if isinstance(action, argparse._SubParsersAction):
                for choice, subparser in action.choices.items():
                    print(f"Function: '{choice}'")
                    print(subparser.format_help())
        print(parser.format_help())

    @staticmethod
    def usr_args():
        """Parse user supplied arguments."""
        parser = argparse.ArgumentParser(
            prog="data_converter",
            usage="%(prog)s [options]",
            description="Utility for handling dictionaries."
        )
        parser.add_argument('-v', '--version', action='version', version=f'%(prog)s {__version__}')

        subparsers = parser.add_subparsers(help='sub-command help')

        # Create the parser for the "functions" command
        parser_list_functions = subparsers.add_parser('functions', help='List all available functions')
        parser_list_functions.set_defaults(func=lambda args: DictionaryUtils.list_functions(parser))

        # Additional arguments can be added here
        parser.add_argument("-t", "--table", required=False, help="Table file to convert.")

        # Print usage message if no args are supplied.
        if len(sys.argv) == 1:
            parser.print_help(sys.stderr)
            sys.exit(1)

        options = parser.parse_args()
        return options

if __name__ == "__main__":
    options = DictionaryUtils.usr_args()
    if hasattr(options, 'func'):
        options.func(options)  # Here `options` will now properly pass `args`
    else:
        print("No function selected or invalid option.")
