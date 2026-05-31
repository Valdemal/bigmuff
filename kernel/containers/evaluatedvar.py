from typing import List

from kernel.enums import OperationCode
from kernel.fuzzy_set import TFuzzySet
from kernel.variables.custom import TCustomVariable


class EvaluatedVar:
    def __init__(self, var: TCustomVariable, value: List[int]):
        """
        Args:
            var: переменная
            value: выражение переменной
        """
        self._var = var
        self._fuzzy = var.value(value)
        self._fuzzy.name = f"{var.name} IS {self._fuzzy.name}"
        self._value = value

    @property
    def fuzzy(self) -> TFuzzySet:
        return self._fuzzy

    @property
    def var(self) -> TCustomVariable:
        return self._var

    @property
    def value(self) -> List[int]:
        return self._value

    @value.setter
    def value(self, value: List[int]):
        self._fuzzy = self._var.value(value)
        self._fuzzy.name = f"{self._var.name} IS {self._fuzzy.name}"
        self._value = value.copy()

    def is_term_used(self, index: int) -> bool:
        """
        Проверка, используется ли терм переменной

        Args:
            index: индекс терма

        Returns:
            True если используется
        """
        for i in range(len(self.value) - 1):
            if self.value[i] == OperationCode.ocValue and self._value[i + 1] == index:
                return True

        return False
