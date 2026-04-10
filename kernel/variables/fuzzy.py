"""
Модуль для работы с нечеткими переменными
"""

import sys
from typing import Optional, List

from .custom import TCustomVariable
from ..enums import FuzzifyMethod, DefuzzifyMethod, ValueType, OperationCode, VariableType
from ..exceptions import EFuzzyVariable, NFE_INVALID_EXPRESSION
from ..fuzzy_set import TFuzzySet
from ..base import RESULT_FUNC
from ..operation import TOperationBase


class TFuzzyVariable(TCustomVariable):
    """
    Нечеткая переменная (с одним нечетким множеством)
    """

    def __init__(self, a_name: str, a_fs: Optional[TFuzzySet] = None,
                 a_type: Optional[VariableType] = None,
                 a_fmethod: Optional[FuzzifyMethod] = None,
                 a_dfmethod: Optional[DefuzzifyMethod] = None):
        """
        Конструктор нечеткой переменной

        Args:
            a_name: имя переменной
            a_fs: нечеткое множество
            a_type: тип переменной
            a_fmethod: метод фаззификации
            a_dfmethod: метод дефаззификации
        """
        if a_fmethod is not None and a_dfmethod is not None:
            super().__init__(a_name, a_fmethod, a_dfmethod)
        else:
            super().__init__(a_name)

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
    def ops(self) -> Optional[TOperationBase]:
        """Получить набор операций"""
        if self._fs:
            return self._fs.ops
        return None

    @ops.setter
    def ops(self, value: TOperationBase):
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

    def _internal_fuzzificate(self, crisp: float) -> Optional[TFuzzySet]:
        """
        Внутренняя фаззификация

        Args:
            crisp: четкое значение

        Returns:
            нечеткое множество
        """
        if self._fs:
            return self._fs.fuzzificate(crisp, self._fuzzify)
        return None

    def _internal_defuzzificate(self, value: Optional[TFuzzySet]) -> float:
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

    def value(self, revform: List[int]) -> Optional[TFuzzySet]:
        """
        Получение композитного значения нечеткой переменной
        Выражение записывается в обратной польской записи

        Args:
            revform: выражение в обратной польской записи

        Returns:
            результат вычисления
        """
        res: List[TFuzzySet] = []

        try:
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
                        RESULT_FUNC(self._fs.func.inf, self._fs.func.sup, self._fs.ops.points),
                        self._fs.ops
                    ))

                elif opcode == OperationCode.ocNot:
                    if not res:
                        raise Exception("недостаточно операндов")
                    op = res.pop()
                    res.append(~op)

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

        except Exception as e:
            raise EFuzzyVariable(str(e), NFE_INVALID_EXPRESSION)

    def is_value_exists(self, value: str) -> bool:
        """
        Проверить существование значения

        Args:
            value: имя значения

        Returns:
            True если значение существует
        """
        return self._fs is not None and value == self._fs.name

    # def __str__(self) -> str:
    #     """
    #     Выгрузка переменной в FCL файл
    #
    #     Returns:
    #         строка в формате FCL
    #     """
    #     result = ""
    #
    #     if self._type == VariableType.vtInput:
    #         result += f"{FuzzifyToken[0]} {self._name}\n"
    #         result += f"{IdentToken}{MethodToken}: {FuzzifyMethodName.get(self._fuzzify, 'UNKNOWN')} ;\n"
    #         result += f"{IdentToken}"
    #
    #         if self._units:
    #             result += f"{UnitsToken}: \"{self._units}\" ;\n{IdentToken}"
    #
    #         if self._fs:
    #             result += f"{RangeToken} := ({self._fs.func.inf} .. {self._fs.func.sup}) ;\n{IdentToken}"
    #             result += str(self._fs)
    #
    #         result += FuzzifyToken[1]
    #
    #     elif self._type == VariableType.vtOutput:
    #         result += f"{DeFuzzifyToken[0]} {self._name}\n"
    #         result += f"{IdentToken}{MethodToken}: {DeFuzzifyMethodName.get(self._defuzzify, 'UNKNOWN')} ;\n"
    #         result += f"{IdentToken}"
    #
    #         if self._units:
    #             result += f"{UnitsToken}: \"{self._units}\" ;\n{IdentToken}"
    #
    #         if self._fs:
    #             result += f"{RangeToken} := ({self._fs.func.inf} .. {self._fs.func.sup}) ;\n{IdentToken}"
    #             result += str(self._fs)
    #
    #         result += DeFuzzifyToken[1]
    #
    #     elif self._type == VariableType.vtIntermediate:
    #         result += f"{IntermediateToken[0]} {self._name}\n"
    #         result += f"{IdentToken}"
    #
    #         if self._units:
    #             result += f"{UnitsToken}: \"{self._units}\" ;\n{IdentToken}"
    #
    #         if self._fs:
    #             result += f"{RangeToken} := ({self._fs.func.inf} .. {self._fs.func.sup}) ;\n{IdentToken}"
    #             result += str(self._fs)
    #
    #         result += IntermediateToken[1]
    #
    #     return result

    def to_fcl(self, out=sys.stdout):
        """Выгрузка переменной в FCL файл"""
        out.write(str(self))


# Для удобства создаем функции-фабрики
def create_fuzzy_input_variable(name: str, fs: TFuzzySet,
                                fuzzify: FuzzifyMethod) -> TFuzzyVariable:
    """
    Создание входной нечеткой переменной

    Args:
        name: имя переменной
        fs: нечеткое множество
        fuzzify: метод фаззификации

    Returns:
        нечеткая переменная
    """
    var = TFuzzyVariable(name, fs, VariableType.vtInput, fuzzify, DefuzzifyMethod.dmCOG)
    return var


def create_fuzzy_output_variable(name: str, fs: TFuzzySet,
                                 defuzzify: DefuzzifyMethod) -> TFuzzyVariable:
    """
    Создание выходной нечеткой переменной

    Args:
        name: имя переменной
        fs: нечеткое множество
        defuzzify: метод дефаззификации

    Returns:
        нечеткая переменная
    """
    var = TFuzzyVariable(name, fs, VariableType.vtOutput, FuzzifyMethod.fmTriangle, defuzzify)
    return var


def create_fuzzy_intermediate_variable(name: str, fs: TFuzzySet) -> TFuzzyVariable:
    """
    Создание промежуточной нечеткой переменной

    Args:
        name: имя переменной
        fs: нечеткое множество

    Returns:
        нечеткая переменная
    """
    var = TFuzzyVariable(name, fs, VariableType.vtIntermediate)
    return var
