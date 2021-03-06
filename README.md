# TuringMachineGenerator
Упрощение разработки кода для машины Тьюринга в лабе по дм (только одноленточная)

* Удобнее писать на Python с подсказками среды разработки
* Синтаксический сахар
* Возможность запуска тестов + дебаг
* Использование силы питона для генерации кода
* Вывод в синтаксисе лабы по дм
* Вывод в синтаксисе https://turingmachine.io.
* Тестирование
* Поддержка генерации (оч много фич) для многоленточной МТ

## Одноленточная машина
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

###### Вывод для https://turingmachine.io
Вызвать `turing_machine_io(входной текст)` и результат сам скопируется тебе в буфер обмена

###### Простые тесты
````
assert g.run('0<1')
assert g.run('101<1101')
assert not g.run('1<1')
assert g.run('1<10')
assert g.run('1010101010110<1010111010110')
assert g.run('101<110')
assert g.run('1011<1100')
assert g.run('1011111111111<1100000000000')
````

###### Примеры:
  
Идти вправо, пропуская 1,2,3,4, на пустом символе переместиться влево и вызвать action
* `r.add([0, 1, 2, 3], RIGHT).add(' ', LEFT, action)`

Перейти в отвергающее состояние, если пустой символ
* `b.add(' ', to=reject)`

#### Плюсы:
* Проверка для скобочной последовательности пишется в 16 строчек
* Быстрая разработка и дебаг
* Тесты
* Проверка типов

## Многоленточная машина
Класс `MultiGenerator(размерность)`

Функция `generate` аналогична одноленточной

Имеет функцию `add(cur_state, moves, chars, next_state=None, new_chars=None)`
1. Исходное состояние
2. Шаги перехода
3. Символы
4. Новое состояние
5. Новые символы

Все что логично задавать массивом (2,3,5), должно быть одного размера

##### ФИЧИ
* Если шаг для всех лент одинаков, можно указать не массив, а просто шаг.
* Для каждого символа в массиве символов можно задать массив символов, тогда для каждой комбинации добавится правило.
* Если для всех лент символ совпадает, можно указать не массив, а просто символ.
* Следующее состояние по умолчанию = текущее.
* Можно также указать только один новый символ, он будет применен для всех лент.
* Новые символы могут быть `Null`, тогда при переходе символ не изменится. Также это работает, если в `chars` для каждой ленты записано много символов.
* Можно указать символ `Null` только для одной ленты, тогда он не изменится.
* Можно передать вместо символа функцию! Принимает на вход список символов и возвращает символ.

##### Пример

Скопировать первую ленту во вторую
```
g = MultiGenerator(2)
add = g.add
add('copyLine', RIGHT, [[0, 1, '|'], [0, 1, '|', ' ']], new_chars=lambda x: x[0])
add('copyLine', LEFT, ' ', 'goLeft')
add('goLeft', LEFT, [[0, 1, '|']] * 2)
add('goLeft', RIGHT, ' ')
```
Будет сгенерирован следующий код:
```
2
copyLine 0 0 -> copyLine 0 > 0 >
copyLine 0 1 -> copyLine 0 > 0 >
copyLine 0 | -> copyLine 0 > 0 >
copyLine 0 _ -> copyLine 0 > 0 >
copyLine 1 0 -> copyLine 1 > 1 >
copyLine 1 1 -> copyLine 1 > 1 >
copyLine 1 | -> copyLine 1 > 1 >
copyLine 1 _ -> copyLine 1 > 1 >
copyLine | 0 -> copyLine | > | >
copyLine | 1 -> copyLine | > | >
copyLine | | -> copyLine | > | >
copyLine | _ -> copyLine | > | >
copyLine _ _ -> goLeft _ < _ <
goLeft 0 0 -> goLeft 0 < 0 <
goLeft 0 1 -> goLeft 0 < 1 <
goLeft 0 | -> goLeft 0 < | <
goLeft 1 0 -> goLeft 1 < 0 <
goLeft 1 1 -> goLeft 1 < 1 <
goLeft 1 | -> goLeft 1 < | <
goLeft | 0 -> goLeft | < 0 <
goLeft | 1 -> goLeft | < 1 <
goLeft | | -> goLeft | < | <
goLeft _ _ -> goLeft _ > _ >

```
