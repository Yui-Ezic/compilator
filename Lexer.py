import re


def char_type(char):
    """
    Вычесляет тип символа
    :rtype: str
    """
    res = ""
    if char in '.':
        res = "Dot"
    elif re.match(r'^[a-zA-Z]$', char):
        res = "Letter"
    elif re.match(r'^[0-9]$', char):
        res = "Digit"
    elif char in " \t":
        res = "WhiteSpace"
    elif char in "\n":
        res = "NewLine"
    elif char in "+-*/":
        res = "ArithmeticOperator"
    elif char == "=":
        res = "Equals"
    elif char in "=(){}:":
        res = "SpecialChar"
    elif char == ';':
        res = "Semicolon"
    elif char == '>':
        res = "Greater"
    elif char == '<':
        res = "Less"
    elif char == '!':
        res = "Exclamation"
    elif char == '"':
        res = "QuotationMark"
    else:
        return None
    return res


class Lexer(object):
    def __init__(self, source_code):
        self.keywords = [
            "DeclareList",
            "integer",
            "real",
            "Program",
            'if',
            'while',
            'read',
            'write',
            'else'
        ]
        self.separators = [
            ';', ':', ' ', '=',
            '-', '+', '*', '/',
            '(', ')', '{', '}'
        ]
        self.source_code = source_code
        self.code_length = len(source_code)
        self.line = 1

        self.tokens = []
        self.consts = []
        self.identifiers = []
        self.identifier_index = 0
        self.const_index = 0

        self.error = None

        self.char_index = -1
        self.char = None
        self.char_type = None

    def is_error(self):
        return False if self.error is None else True

    def tokenize(self):
        self.next_char()
        while self.char_index < self.code_length:
            start_index = self.char_index
            start_line = self.line

            # Пропускаем пробелы
            if self.char_type == "WhiteSpace" or self.char_type == "NewLine":
                self.next_char()
                continue

            # Проверяем ключевые слова
            if self.is_keyword():
                continue
            else:
                self.next_char(start_index)
                self.line = start_line

            # Проверяем или это число
            if self.is_number():
                continue
            else:
                self.next_char(start_index)
                self.line = start_line

            # Проверяем или это арифметический оператор
            if self.is_arithmetic_operator():
                continue

            # Проверяем или это оператор сравнения "равно" ==
            if self.is_equals_operator():
                continue
            else:
                self.next_char(start_index)
                self.line = start_line

            # Проверяем или это оператор сравнения "не равно" !=
            if self.is_not_equals_operator():
                continue
            else:
                self.next_char(start_index)
                self.line = start_line

            # Проверяем или это опретор присваивания
            if self.is_assigment_operator():
                continue

            # Проверяем или это специальный символ
            if self.is_special_char():
                continue

            # Проверяем или это простой оператор сравнения (Больше или меньше)
            if self.is_simple_comparision_operator():
                continue

            # Проверяем или это идентификатор
            if self.is_identifier():
                continue
            else:
                self.next_char(start_index)
                self.line = start_line

            # Провераяем или это строка
            if self.is_sting():
                continue
            else:
                self.next_char(start_index)
                self.line = start_line

            # Не найдено никаких совпадений
            self.error = "Unknown char `" + self.char + "` in line " + str(self.line)
            return False

        return True

    def next_char(self, index=None):
        """
        Переход к следующему символу
        :param index: integer or None индекс символа к которому надо перейти
        :return: boolean True если переход совершился и False в случае ошибки
        """
        self.char_index = index if index is not None else (self.char_index + 1)
        if self.char_index >= self.code_length:
            return False

        self.char = str(self.source_code[self.char_index])
        self.char_type = char_type(self.char)
        if self.char_type is None:
            self.error = "Unknown type of char `" + self.char + "`"
            return False

        if self.char_type == "NewLine":
            self.line += 1

        return True

    def add_const(self, const):
        self.const_index += 1
        self.consts.append([const, self.const_index])

    def add_identifier(self, name):
        """
        Добавляет переменную без копий
        :param name: Имя переменной
        :return: Индекс переменной
        """
        for identifier in self.identifiers:
            if name == identifier[0]:
                index = identifier[1]
                return index
        self.identifier_index += 1
        # Имя, индекс, тип
        self.identifiers.append([name, self.identifier_index, None])
        return self.identifier_index

    def add_token(self, string, token, index=None):
        self.tokens.append([self.line, string, token, index])

    def is_keyword(self):
        """
        Ищет совпадения с ключевым словом
        :return: boolean
        """
        # Проверяем есть ли совпадения с первой буквой из списка ключевых слов
        is_find = False
        for keyword in self.keywords:
            if keyword[0] == self.char:
                is_find = True
        if not is_find:
            return False

        # Пытаемся считать слово
        word = ""
        while self.char not in self.separators:
            word += self.char
            if not self.next_char():
                break

        # Проверяем совпадения слова со списком ключевых слов
        if word in self.keywords:
            self.add_token(word, 'keyword')
            return True

        return False

    def is_number(self):
        """
        Проверяет или следующая поледовательность символов это число
        :return: boolean
        """
        if self.char_type != "Digit":
            return False

        number = ""
        meet_dot = False
        number_type = "integer"
        while self.char_type == "Digit" or self.char_type == "Dot":
            if self.char_type == "Dot":
                if meet_dot:
                    return False
                meet_dot = True
                number_type = "float"
            number += self.char
            if not self.next_char():
                break

        self.add_const(number)
        self.add_token(number, number_type, self.const_index)
        return True

    def is_arithmetic_operator(self):
        if self.char_type != "ArithmeticOperator":
            return False

        self.add_token(self.char, "ArithmeticOperator")
        self.next_char()
        return True

    def is_equals_operator(self):
        """
        Проверяет или последовательность символов это оператор сравнения "равно" '=='
        :return: boolean
        """
        if self.char_type != "Equals":
            return False

        if not self.next_char():
            return False

        if self.char_type != "Equals":
            return False

        if self.next_char() and self.char not in self.separators:
            return False

        self.add_token("==", "ComparisionOperator")
        return True

    def is_not_equals_operator(self):
        """
        Проверяет или последовательность символов это оператор сравнения "не равно" '!='
        :return: boolean
        """
        if self.char_type != "Exclamation":
            return False

        if not self.next_char():
            return False

        if self.char_type != "Equals":
            return False

        if self.next_char() and self.char not in self.separators:
            return False

        self.add_token("==", "ComparisionOperator")
        return True

    def is_simple_comparision_operator(self):
        if self.char not in "><":
            return False

        self.add_token(self.char, "ComparisionOperator")
        self.next_char()
        return True

    def is_assigment_operator(self):
        if self.char_type != "Equals":
            return False

        self.add_token(self.char, "AssigmentOperator")
        self.next_char()
        return True

    def is_special_char(self):
        if self.char_type != "SpecialChar" and self.char_type != "Semicolon":
            return False

        self.add_token(self.char, self.char_type)
        self.next_char()
        return True

    def is_identifier(self):
        if self.char_type != "Letter":
            return False

        name = ""
        while self.char_type in ['Letter', 'Digit']:
            name += self.char
            if not self.next_char():
                break

        index = self.add_identifier(name)
        self.add_token(name, "identifier", index)
        return True

    def is_sting(self):
        if self.char != "\"":
            return False

        if not self.next_char():
            return False

        string = ""
        while self.char != "\"":
            string += self.char
            if not self.next_char():
                return False

        self.add_token(string, "string")
        self.next_char()
        return True
