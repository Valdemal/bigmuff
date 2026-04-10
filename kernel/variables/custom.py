import sys
from abc import ABC, abstractmethod
from typing import Optional, List

from kernel.enums import FuzzifyMethod, DefuzzifyMethod, ValueType, VariableType
from kernel.exceptions import EFuzzyVariable, NFE_INVALID_FUZZIFY_METHOD, NFE_INVALID_DEFUZZIFY_METHOD
from kernel.fuzzy_set import TFuzzySet
from kernel.base import TNeuroFuzzyBase
from kernel.operation import TOperationBase


class TCustomVariable(TNeuroFuzzyBase, ABC):
    """
    Базовый класс для нечеткой переменной
    """

    def __init__(self, a_name: str, a_fmethod: Optional[FuzzifyMethod] = None,
                 a_dfmethod: Optional[DefuzzifyMethod] = None):
        """
        Конструктор базового класса переменной

        Args:
            a_name: имя переменной
            a_fmethod: метод фаззификации
            a_dfmethod: метод дефаззификации
        """
        super().__init__()
        self._name = a_name
        self._value_type = ValueType.valNA
        self._type = VariableType.vtNA
        self._units = ""

        if a_fmethod is not None:
            self._fuzzify = a_fmethod
        else:
            self._fuzzify = FuzzifyMethod.fmNA

        if a_dfmethod is not None:
            self._defuzzify = a_dfmethod
        else:
            self._defuzzify = DefuzzifyMethod.dmNA

    @property
    def name(self) -> str:
        """Получить имя переменной"""
        return self._name

    def value(self, revform: List[int]) -> Optional[TFuzzySet]:
        pass

    @abstractmethod
    @property
    def ops(self) -> Optional[TOperationBase]:
        pass

    @abstractmethod
    @ops.setter
    def ops(self, value: TOperationBase):
        pass

    def is_value_exists(self, value: str) -> bool:
        return False

    def is_term_exists(self, term: str) -> int:
        return -1

    @property
    def value_type(self) -> ValueType:
        """Получить тип значения"""
        return self._value_type

    @value_type.setter
    def value_type(self, value: int):
        """Установить тип значения"""
        self._value_type = value

    @property
    def type(self) -> VariableType:
        """Получить тип переменной"""
        return self._type

    @type.setter
    def type(self, value: int):
        """Установить тип переменной"""
        self._type = value

    @property
    def fuzzify(self) -> FuzzifyMethod:
        """Получить метод фаззификации"""
        return self._fuzzify

    @property
    def defuzzify(self) -> DefuzzifyMethod:
        """Получить метод дефаззификации"""
        return self._defuzzify

    @property
    def units(self) -> str:
        """Получить единицы измерения"""
        return self._units

    @units.setter
    def units(self, value: str):
        """Установить единицы измерения"""
        self._units = value

    def fuzzificate(self, crisp: float) -> Optional['TFuzzySet']:
        """
        Процедура фаззификации

        Args:
            crisp: четкое значение

        Returns:
            нечеткое множество
        """
        if self._fuzzify == FuzzifyMethod.fmNA:
            raise EFuzzyVariable(self._name, NFE_INVALID_FUZZIFY_METHOD)
        return self._internal_fuzzificate(crisp)

    def defuzzificate(self, value: Optional['TFuzzySet']) -> float:
        """
        Процедура дефаззификации

        Args:
            value: нечеткое множество

        Returns:
            четкое значение
        """
        if self._defuzzify == DefuzzifyMethod.dmNA:
            raise EFuzzyVariable(self._name, NFE_INVALID_DEFUZZIFY_METHOD)
        return self._internal_defuzzificate(value)

    def _internal_fuzzificate(self, crisp: float) -> Optional['TFuzzySet']:
        """
        Внутренняя фаззификация (должен быть переопределен)

        Args:
            crisp: четкое значение

        Returns:
            нечеткое множество
        """
        return None

    def _internal_defuzzificate(self, value: Optional['TFuzzySet']) -> float:
        """
        Внутренняя дефаззификация (должен быть переопределен)

        Args:
            value: нечеткое множество

        Returns:
            четкое значение
        """
        if value is not None:
            return value.defuzzificate(self._defuzzify)

        return float('-inf')

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
    #         result += DeFuzzifyToken[1]
    #
    #     elif self._type == VariableType.vtIntermediate:
    #         result += f"{IntermediateToken[0]} {self._name}\n"
    #         result += f"{IdentToken}"
    #
    #         if self._units:
    #             result += f"{UnitsToken}: \"{self._units}\" ;\n{IdentToken}"
    #
    #         result += IntermediateToken[1]
    #
    #     return result

    def to_fcl(self, out=sys.stdout):
        """Выгрузка переменной в FCL файл"""
        out.write(str(self))

