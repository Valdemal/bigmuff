from builder import Builder
from fcl.enums import FCLRules, FCLTokens
from fcl.parser import FCLParser
from fcl.structs import FCLElement, FCLMatrixSymbol
from fcl.translator.matrix import MATRIX


class Translator:
    def __init__(self):
        self._stack: list[FCLRules] = [
            FCLRules.emptystack, FCLRules.fb,
        ]
        self._current_state = 0
        self._error_state = 0

    def translate(self, parser: FCLParser, builder: Builder):
        in_prog = parser.parse()
        flag = True
        while flag:
            current_element: FCLElement = in_prog[0]
            element = FCLMatrixSymbol(*MATRIX[self._stack[-1].value][current_element.id.value])

            if element.action is not None:
                element.action(current_element, builder)

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

            flag = current_element.id != FCLTokens.endfcl and self._error_state == 0

