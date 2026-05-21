from collections import deque
from typing import TextIO, Iterable

from fcl.consts import FCLS_TOKENS
from fcl.enums import FCL_TOKENS_COUNT, FCLTokens
from fcl.structs import FCLElement

FCLProgram = deque[FCLElement]

def parse(filename: str) -> FCLProgram:
    tokens: FCLProgram = FCLProgram()
    with open(filename, 'r') as input_stream:
        str_pos = 0

        for line in input_stream.readlines():
            str_pos += 1
            for token in _parse_line(line, str_pos):
                tokens.append(token)

        return tokens


def _parse_line(line: str, strn: int) -> Iterable[FCLElement]:
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
            else:
                while end < lenght:
                    if line[end] in " ():;,=/*\\\"'\n":
                        break
                    end += 1

                idx = FCLTokens.numeric_literal.value
                value = value[:end]

        if idx == FCLTokens.end_comment.value:
            raise Exception()

        yield FCLElement(FCLTokens(idx), value, strn, beg + 1)
        beg = end