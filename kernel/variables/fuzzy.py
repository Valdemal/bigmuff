"""
Модуль для работы с нечеткими переменными
"""

from typing import Optional, List

from .custom import CustomVariable
from ..enums import FuzzifyMethod, DefuzzifyMethod, ValueType, OperationCode, VariableType
from ..fuzzy_set import TFuzzySet
from ..member_func import RESULT_FUNC
from ..operation import OperationBase


class FuzzyVariable(CustomVariable):
    """
    Нечеткая переменная (с одним нечетким множеством)
    """

    def __init__(self, name: str, a_fs: Optional[TFuzzySet] = None,
                 a_type: Optional[VariableType] = None,
                 a_fmethod: Optional[FuzzifyMethod] = None,
                 a_dfmethod: Optional[DefuzzifyMethod] = None):
        """
        Конструктор нечеткой переменной

        Args:
            name: имя переменной
            a_fs: нечеткое множество
            a_type: тип переменной
            a_fmethod: метод фаззификации
            a_dfmethod: метод дефаззификации
        """
        if a_fmethod is not None and a_dfmethod is not None:
            super().__init__(name, a_fmethod, a_dfmethod)
        else:
            super().__init__(name)

        self._fs = a_fs

        if self._fs:
            self._fs.name = "Value"

        self._value_type = ValueType.valFuzzy

        if a_type is not None:
            self._type = a_type

        if a_fmethod is not None:
            self._fuzzify = a_fmethod

        if a_dfmethod is not None:
            self._defuzzify = a_dfmethod

    @property
    def ops(self) -> Optional[OperationBase]:
        """Получить набор операций"""
        if self._fs:
            return self._fs.ops
        return None

    @ops.setter
    def ops(self, value: OperationBase):
        """Установить набор операций"""
        if self._fs:
            self._fs.ops = value

    @property
    def fuzzy_set(self) -> Optional[TFuzzySet]:
        """Получить нечеткое множество"""
        return self._fs

    @fuzzy_set.setter
    def fuzzy_set(self, new_fs: TFuzzySet):
        """Установить нечеткое множество"""
        self._fs = new_fs
        if self._fs:
            self._fs.name = "Value"

    def fuzzificate(self, crisp: float) -> Optional[TFuzzySet]:
        """
        Внутренняя фаззификация

        Args:
            crisp: четкое значение

        Returns:
            нечеткое множество
        """
        return self._fs.fuzzificate(crisp, self._fuzzify)

    def defuzzificate(self, value: Optional[TFuzzySet]) -> float:
        """
        Внутренняя дефаззификация

        Args:
            value: нечеткое множество

        Returns:
            четкое значение
        """
        if value is not None:
            return value.defuzzificate(self._defuzzify)
        elif self._fs:
            return self._fs.defuzzificate(self._defuzzify)
        return float('-inf')

    def value(self, revform: List[int]) -> TFuzzySet:
        """
        Получение композитного значения нечеткой переменной
        Выражение записывается в обратной польской записи

        Args:
            revform: выражение в обратной польской записи

        Returns:
            результат вычисления
        """
        res: List[TFuzzySet] = []

        i = 0
        while i < len(revform):
            opcode = revform[i]
            i += 1

            if opcode == OperationCode.ocValue:
                val = revform[i]
                i += 1

                if val != 0:
                    raise Exception("в нечеткой переменной только 1 терм")

                res.append(TFuzzySet(
                    "Value",
                    RESULT_FUNC(self._fs.func, self._fs.ops.points),
                    self._fs.ops
                ))

            elif opcode == OperationCode.ocNot:
                if not res:
                    raise Exception("недостаточно операндов")

                res.append(~res.pop())

            elif opcode == OperationCode.ocVery:
                if not res:
                    raise Exception("недостаточно операндов")
                op = res.pop()
                res.append(op.con())

            elif opcode == OperationCode.ocAverage:
                if not res:
                    raise Exception("недостаточно операндов")
                op = res.pop()
                res.append(op.dil())

            else:
                raise Exception(f"неверный оператор: {opcode}")

        if len(res) != 1:
            raise Exception("неполное выражение")

        return res[0]

    def is_value_exists(self, value: str) -> bool:
        """
        Проверить существование значения

        Args:
            value: имя значения

        Returns:
            True если значение существует
        """
        return self._fs is not None and value == self._fs.name

    def is_term_exists(self, term: str) -> int:
        return 0 if term == self.name else -1

