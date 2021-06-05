from enum import Enum
from functools import wraps
import pyperclip


class Move(Enum):
    LEFT = '<'
    RIGHT = '>'
    STOP = '^'


LEFT = Move.LEFT
RIGHT = Move.RIGHT
STOP = Move.STOP


def type_checker(expected_types):
    def type_checker_dec(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            def type_to_str(x):
                return str(x) if type(x) == str else x.__name__

            if len(expected_types) > func.__code__.co_argcount:
                raise Exception("wrong types number")
            names = func.__code__.co_varnames
            for ind, expected in enumerate(expected_types):
                ind = ind + 1
                name = names[ind]
                if ind < len(args) and args[ind] is not None:
                    if not type(args[ind]).__name__ in map(type_to_str, expected):
                        raise Exception(r'expected ({}), got {}.'
                                        .format(', '.join(map(type_to_str, expected)), type_to_str(type(args[ind]))))
                elif name in kwargs:
                    if not type(kwargs[name]).__name__ in map(type_to_str, expected):
                        raise Exception(r'expected ({}), got {}.'
                                        .format(', '.join(map(type_to_str, expected)), type_to_str(type(kwargs[name]))))
            return func(*args, **kwargs)

        return wrapper

    return type_checker_dec


def get_diff(move: Move):
    if move == Move.LEFT:
        return -1
    if move == Move.STOP:
        return 0
    if move == Move.RIGHT:
        return 1


class Rule:
    def __init__(self, name, char, move, to, new_char):
        self.name = name
        self.char = char
        self.move = move
        self.to = to
        self.new_char = new_char

    def __str__(self):
        return r'{} {} -> {} {} {}'.format(self.name, self.char, self.to.name, self.new_char, self.move.value)


class State:
    def __init__(self, name):
        self.name = name
        self.rules = {}
        self.tur_mach_rules = []

    @type_checker([[str, int, list], [Move], ['State'], [str, int]])
    def add(self, char, move: Move = Move.RIGHT, to=None, new_char=None):
        def t_move():
            if move == LEFT:
                return 'L'
            elif move == RIGHT:
                return 'R'

        def ch_to_str(ch):
            if type(ch) == str:
                return '\'' + ch + '\''
            else:
                return ch

        if to is None:
            to = self
        if char == ' ':
            char = '_'
        if new_char == ' ':
            new_char = '_'
        if type(char) == list:
            char = list(map(lambda x: x if x != ' ' else '_', char))
        if new_char is None:
            self.tur_mach_rules.append(r'{} : {{{}: {}}}'.format(ch_to_str(char), t_move(), to.name))
        else:
            self.tur_mach_rules.append(r'{} : {{{}: {}, write: {}}}'
                                       .format(ch_to_str(char), t_move(), to.name, ch_to_str(new_char)))
        return self.add_(char, move, to, new_char)

    def add_(self, char, move, to, new_char):
        if type(char) == list:
            for i in char:
                self.add_(i, move, to, new_char)
        else:
            if new_char is None:
                new_char = char
            self.rules[str(char)] = Rule(self.name, str(char), move, to, str(new_char))
        return self


class Generator:
    def __init__(self):
        self.line_size = 10_000
        self.print_radius = 10
        self._states = []
        self.started = None
        self.accepted = None
        self.rejected = None
        self.tur_mach_io_rules = []

    @type_checker([[str]])
    def new_state(self, name, started=False, accepted=False, rejected=False):
        state = State(name)
        self._states.append(state)
        if started:
            self.started = state
        if accepted:
            self.accepted = state
        if rejected:
            self.rejected = state
        return state

    def generate(self, file_name=None):
        rules = ['start: ' + self.started.name,
                 'accept: ' + self.accepted.name,
                 'reject: ' + self.rejected.name,
                 'blank: _']
        for state in self._states:
            rules += list(map(str, state.rules.values()))
        result = '\n'.join(rules)
        if file_name:
            with open(file_name, 'w') as writer:
                writer.write(result)
        else:
            print(result)

    def run(self, input_line, debug=False):
        line = ['_'] * self.line_size + list(input_line) + ['_'] * self.line_size
        index = self.line_size
        state = self.started
        while state != self.rejected and state != self.accepted:
            char = line[index]
            if char not in state.rules:
                print('wrong move by {} from {}, rejected'.format(char, state.name))
                return
            rule = state.rules[char]
            if debug:
                print(' '.join(line[index - self.print_radius: index + self.print_radius]))
                print('↑'.rjust(self.print_radius * 2 + 1, ' '))
                print(rule)
            line[index] = rule.new_char
            index += get_diff(rule.move)
            state = rule.to
        if state == self.accepted:
            print('accepted')
            return True
        else:
            print('rejected')
            return False

    def turing_machine_io(self, inp=None):
        rules = ['input: ' + inp,
                 'start state: ' + self.started.name,
                 'blank: _',
                 'table:']
        for state in self._states:
            rules.append(' '*4 + state.name + ':')
            rules += list(map(lambda x: ' '*8 + x, state.tur_mach_rules))
        text = '\n'.join(rules)
        pyperclip.copy(text)
        print(text)
