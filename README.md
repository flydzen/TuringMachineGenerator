# TuringMachineGenerator
Упрощение разработки кода для машины Тьюринга в лабе по дм

* Удобнее писать на Python с подсказками среды разработки
* Синтаксический сахар
* Возможность запуска тестов + дебаг
* Использование силы питона для генерации кода

### Пример:
```
from generator import *

g = Generator()

even = g.new_state('start', started=True)
ac = g.new_state('accept', accepted=True)
rj = g.new_state('reject', rejected=True)
odd = g.new_state('odd')

even.add(' ', STOP, ac)\
    .add(0, RIGHT, odd, ' ')
odd.add(0, RIGHT, even, ' ')\
   .add(' ', RIGHT, rj)

g.run('0000', debug=True)
g.generate('zero.out')
```

### Че как писать?
###### Создать состояние:

* `generator: new_state(self, name, started=False, accepted=False, rejected=False):`
* По умолчанию создается просто состояние с именем, можно указать её статус.
* Также статус можно изменить у созданной вершины через `generator.accepted = состояние`

###### Добавить правило:

* У состояния вызвать `add(char, move: Move=STOP, to=None, new_char: str = None)`
* В качестве символа перехода можно указывать символ, число, а также массив символов перехода. Тогда для каждого символа будет построено отдельное правило
* Шаг: `LEFT`, `RIGHT`, `STOP`. Последний по умолчанию
* Состояние, в которое переходим. По умолчанию -- остаемся на месте.
* Новый символ. По умолчанию -- не изменять.
* `add` возвращает объект, на котором был вызван, поэтому можно применять переходы последовательно, или определять их сразу при создании состояния
* Пустой символ `' '` или `'_'`

###### Запуск:
У генератора вызвать `run('входная строка', debug=True/False)`
По умолчанию без дебага.

###### Примеры:
  
Идти вправо, пропуская 1,2,3,4, на пустом символе переместиться влево и вызвать action
* `r.add([0, 1, 2, 3], RIGHT).add(' ', LEFT, action)`

Перейти в отвергающее состояние, если пустой символ
* `b.add(' ', to=reject)`

#### Плюсы:
Проверка для скобочной последовательности пишется в 16 строчек

