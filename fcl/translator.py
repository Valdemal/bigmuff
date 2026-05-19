from collections import deque
from typing import TextIO

from fcl.enums import FCLRules, FCLTokens, FCL_TOKENS_COUNT
from fcl.matrix import MATRIX
from fcl.structs import FCLElement, FCLMatrixSymbol
from kernel.block.function import TFunctionBlock
from kernel.exceptions import FCL_DONE

FCLProgram = deque[FCLElement]

class Translator:
    # todo разделить парсер и транслятор
    def __init__(self):
        self._stack = [
            FCLRules.emptystack, FCLRules.fb,
        ]
        self._current_rule = FCLRules.fb
        self._current_state = 0
        self._error_state = 0
        self._learning = False
        self._antecedent: list[int] = []
        self._cons_value: list[int] = []
        self._ant_comb: list[int] = []
        self._ant_value: list[list[int]] = []
        self._fcl_program: list[FCLElement] = []
        # todo !!!
        self._func_block: TFunctionBlock = None

    def translate(self, in_prog: FCLProgram):
        current_element = FCLElement(FCLTokens.endfcl, "", 0, 0)
        in_prog.append(current_element)

        flag = True
        while flag:
            current_element = in_prog[-1]
            current_token, current_rule = current_element.id, self._stack[-1]

            element = FCLMatrixSymbol(*MATRIX[current_rule][current_token])

            try:
                if element.action is not None:
                    element.action()

            except Exception:
                # self._error_state =
                # msg =
                pass

            if element.pop:
                self._stack.pop()

            if element.count:
                for i in reversed(range(element.count)):
                    # todo watafa
                    self._stack.append(element.to_stack[i])

            if element.next:
                in_prog.popleft()

            if element.nextstate != -1:
                self._current_state = element.nextstate

            flag = current_token != FCLTokens.endfcl and self._error_state == 0

    def _fcl_text_to_tokens(self, filename: str, input_stream: TextIO, tok: FCLProgram):
        # todo доделать позже
        tok.clear()
        strn = 0

        while True:
            strn += 1
            line = input_stream.readline()

            if not line:
                break

            strn += 1
            # Удаляем перевод строки в конце
            line = line.rstrip('\n\r')
            length = len(line)

            # Сохраняем оригинальную строку и её версию в верхнем регистре
            str_original = line
            str_upper = line.upper()

            beg = 0

            while beg < length:
                value = ""

                while beg < length and (line[beg] == ' ' or line[beg] == '\t' or line[beg] == '\r'):
                    beg += 1

                end = beg

                if beg >= length:
                    continue

                i = 0
                for i in range(FCL_TOKENS_COUNT):
                    pass

                if i == FCLTokens.str_comment:
                    break

                if i == FCLTokens.begin_comment:
                    str_beg = strn



                # i = FCLTokensCount

                # for idx, token in enumerate(FCLSTokens):
                #     if str_upper[beg:beg+len(token)] == token and str_upper.startswith(token, beg):
                #         end = beg + len(token)
                #
                #         # Парные кавычки обрабатываются отдельно
                #         if assign <= idx <= apostrophe:  # предполагаем, что assign/apostrophe определены
                #             i = idx
                #             break
                #
                #         # Проверка разделителей
                #         if end < length and line[end] in " ():;,=+-/*\\\"'.\r":
                #             i = idx
                #             break
                #
                #         # Комментарии не требуют разделителя
                #         if idx in (str_comment, begin_comment, end_comment):
                #             i = idx
                #             break

    def translate_file(self, filename: str) -> TFunctionBlock:
        tok: FCLProgram = FCLProgram()
        with open(filename, 'r') as f:
            self._fcl_text_to_tokens(filename, f, tok)
            self.translate(tok)
            return self._func_block
