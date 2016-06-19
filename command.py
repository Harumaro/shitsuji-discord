import sys
import types
import cmds.ping
import cmds.hentaibingo
import cmds.gayfinder
import cmds.changestatus
import cmds.sndcloud


class Command:

    def __init__(self, name):
        command = list(
            filter(lambda command: name.startswith(command.name), Command.list()))

        if command:
            command = command[0]

            self.name = command.name
            self.description = command.description
            self.parameters = command.parameters
            self.permissions = command.permissions
            self.handler = command.handler
        else:
            self.name = None

    @staticmethod
    def list():
        for mod in dir(list(Command.imports())[0]):
            if not mod.startswith('__'):
                yield sys.modules['cmds.' + mod]

    @staticmethod
    def imports():
        for name, val in globals().items():
            if name not in ['builtins', 'types', 'sys'] and isinstance(val, types.ModuleType):
                yield val
