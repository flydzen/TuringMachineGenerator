from enum import Enum


class Move(Enum):
    LEFT = '<'
    RIGHT = '>'
    STOP = '^'


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

    def add(self, char, move: Move = Move.STOP, to=None, new_char=None):
        if to is None:
            to = self
        if type(char) == list:
            for i in char:
                self.add(i, move, to, new_char)
        else:
            if char == ' ':
                char = '_'
            if new_char is None:
                new_char = char
            self.rules[str(char)] = Rule(self.name, str(char), move, to, str(new_char))
        return self


class Generator:
    def __init__(self):
        self.line_size = 10_000
        self._states = []
        self.started = None
        self.accepted = None
        self.rejected = None

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
        line = ['_']*self.line_size + list(input_line) + ['_']*self.line_size
        index = self.line_size
        state = self.started
        while state != self.rejected and state != self.accepted:
            char = line[index]
            if char not in state.rules:
                print('wrong move by {} from {}, rejected'.format(char, state.name))
                return
            rule = state.rules[char]
            if debug:
                print('state: {}->{}, char: {}->{}, move:{}'.format(state.name, rule.to.name,
                                                                    char, rule.new_char, rule.move.value))
            line[index] = rule.new_char
            index += get_diff(rule.move)
            state = rule.to
        if state == self.accepted:
            print('accepted')
        else:
            print('rejected')
        while line[index] != '_':
            print(line[index], end=' ')
            index += 1


LEFT = Move.LEFT
RIGHT = Move.RIGHT
STOP = Move.STOP
