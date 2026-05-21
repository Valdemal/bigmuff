from collections import deque
from typing import TextIO

from fcl.enums import FCLRules, FCLTokens, FCL_TOKENS_COUNT
from fcl.matrix import MATRIX
from fcl.parser import FCLProgram
from fcl.structs import FCLElement, FCLMatrixSymbol
from kernel.block.function import TFunctionBlock
from kernel.exceptions import FCL_DONE



class Translator:
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

