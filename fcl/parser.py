from collections import deque
from typing import TextIO, Iterable

from fcl.consts import FCLS_TOKENS
from fcl.enums import FCL_TOKENS_COUNT, FCLTokens
from fcl.structs import FCLElement

FCLProgram = deque[FCLElement]


class FCLParser:
    def __init__(self, filename: str):
        self._filename = filename
        self._str_pos = 0
        self._input_stream = open(filename, 'r')

    def parse(self) -> FCLProgram:
        tokens = FCLProgram()
        while line := self._input_stream.readline():
            self._str_pos += 1
            for token in self._parse_line(line):
                tokens.append(token)

        tokens.append(FCLElement(FCLTokens.endfcl, "", 0, 0))
        self._input_stream.close()
        return tokens

    def _parse_line(self, line: str) -> Iterable[FCLElement]:
        beg, lenght = 0, len(line)

        while beg < lenght:
            while (beg < lenght) and line[beg] in " \r\t\n":
                beg += 1

            end = beg

            if beg == lenght:
                continue

            value = ""
            idx = 0
            for idx, token in enumerate(FCLS_TOKENS):
                if line[beg:].startswith(token):
                    end = beg + len(token)

                    # Обрабатываем парные кавычки
                    if FCLTokens.assign.value <= idx <= FCLTokens.apostrophe.value:
                        break

                    # Обрабатываем разделители
                    if line[end] in " ():;,=+-/*\\\"'.\r\n":
                        break

                    if (idx == FCLTokens.str_comment.value or idx == FCLTokens.begin_comment.value or
                            idx == FCLTokens.end_comment.value):
                        break

            if idx == FCLTokens.str_comment.value:
                break

            if idx == FCLTokens.begin_comment.value:
                # todo тут упадет (переделать)
                raise Exception()
            # Пытаемся считать строковый литерал
            elif idx == FCLTokens.quote.value:
                end_str = line[pos] if (pos := line.find(FCLS_TOKENS[FCLTokens.quote.value], end)) != -1 else None

                if end_str:
                    while end_str != line[end]:
                        value += line[end]
                        end += 1

                    end += len(FCLS_TOKENS[FCLTokens.quote.value])
                    idx = FCLTokens.string_literal.value
                else:
                    raise Exception()
            # Токен не распознан корректно
            elif idx == FCL_TOKENS_COUNT - 1:
                # Пытаемся считать неизвестный элемент как идентификатор
                end = beg
                if line[end].isalpha() or line[end] == '_':
                    while line[end].isalnum() or line[end] == '_':
                        value += line[end]
                        end += 1
                    idx = FCLTokens.identifier.value

                # Пытаемся считать как число
                else:
                    while end < lenght:
                        if line[end] in " ():;,=/*\\\"'\n":
                            break
                        value += line[end]
                        end += 1

                    idx = FCLTokens.numeric_literal.value

            if idx == FCLTokens.end_comment.value:
                raise Exception()

            yield FCLElement(FCLTokens(idx), value, self._str_pos, beg + 1)
            beg = end

    def __del__(self):
        if not self._input_stream.closed:
            self._input_stream.close()
