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
    def new_state(self, name, started=False, accepted=False, rejected=False) -> State:
        for i in self._states:
            if i.name == name:
                raise Exception("Повтор состояния")
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
        def print_right(i):
            res = ''
            while line[i] != '_':
                res += line[i]
                i += 1
            return res

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
        res = print_right(index)
        print(res)
        if state == self.accepted:
            print('accepted')
            return True, res
        else:
            print('rejected')
            return False, res

    def turing_machine_io(self, inp=None):
        rules = ['input: ' + inp,
                 'start state: ' + self.started.name,
                 'blank: _',
                 'table:']
        for state in self._states:
            rules.append(' ' * 4 + state.name + ':')
            rules += list(map(lambda x: ' ' * 8 + x, state.tur_mach_rules))
        text = '\n'.join(rules)
        pyperclip.copy(text)
        print(text)


class MultiGenerator:
    def __init__(self, n):
        self.n = n
        self.rules = []

    def add(self, cur_state, moves, chars, next_state=None, new_chars=None):
        if type(chars) != list:
            chars = [chars] * self.n
        flag = False
        if next_state is None:
            next_state = cur_state
        for ind, el in enumerate(chars):
            if type(el) == list:
                flag = True
                for j in el:
                    self.add(cur_state, moves, chars[:ind] + [j] + chars[ind + 1:], next_state, new_chars)
                break
        if not flag:
            chars = list(map(lambda x: x if x != ' ' else '_', chars))
            if new_chars is None:
                new_chars = chars
            if type(new_chars) != list:
                new_chars = [new_chars] * self.n
            zip_chars_moves = None
            new_chars_temp = []
            for ind, el in enumerate(new_chars):
                if type(el) == str:
                    new_chars_temp.append(el)
                elif type(el) == int:
                    new_chars_temp.append(str(el))
                elif el is None:
                    new_chars_temp.append(str(chars[ind]))
                elif type(el).__name__ == 'function':
                    new_chars_temp.append(str(el(chars)))
            new_chars = list(map(lambda x: x if x != ' ' else '_', new_chars_temp))

            if type(moves) == Move:
                zip_chars_moves = map(lambda x: x + ' ' + moves.value, new_chars)
            elif type(moves) == list:
                zip_chars_moves = map(lambda x: x[0] + ' ' + x[1], zip(new_chars, moves))
            self.rules.append(r'{} {} -> {} {}'.format(cur_state, ' '.join(map(str, chars)), next_state,
                                                       ' '.join(list(zip_chars_moves))))

    def generate(self, file_name):
        with open(file_name, 'w') as w:
            print(self.n, file=w)
            for rule in self.rules:
                print(rule, file=w)
