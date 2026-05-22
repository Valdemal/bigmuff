from builder import Builder
from fcl.enums import FCLRules, FCLTokens
from fcl.parser import FCLParser
from fcl.structs import FCLElement, FCLMatrixSymbol
from fcl.translator.matrix import MATRIX


class Translator:
    def __init__(self):
        self._stack: list[FCLTokens | FCLRules] = [
            FCLRules.emptystack, FCLRules.fb,
        ]
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

            if element.to_stack:
                for el in reversed(element.to_stack):
                    self._stack.append(el)

            if element.next:
                in_prog.popleft()

            flag = current_element.id != FCLTokens.endfcl and self._error_state == 0

