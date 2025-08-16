from abc import ABC
from argparse import ArgumentParser, Namespace
from cmd.base.abc_command import AbstractCommand
from typing import List

from core.cmd_parser import Parser


class BaseCommand(AbstractCommand, ABC):
    args: Namespace = None
    help: str = None

    def __init__(self, args: List[str], parser: ArgumentParser):
        self.parser = parser
        self.add_arguments()
        self.set_arguments()
        self.args = self.parser.parse_args(args)

    def set_arguments(self):
        self.parser.add_help = self.help
        parser = Parser()
        parser.remove_argument("mode")
