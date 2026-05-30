import sys
from abc import ABC, abstractmethod
from typing import Optional, List

from kernel.enums import FuzzifyMethod, DefuzzifyMethod, ValueType, VariableType
from kernel.exceptions import EFuzzyVariable, NFE_INVALID_FUZZIFY_METHOD, NFE_INVALID_DEFUZZIFY_METHOD
from kernel.fuzzy_set import TFuzzySet
from kernel.base import TNeuroFuzzyBase, Named
from kernel.operation import TOperationBase


class TCustomVariable(Named, TNeuroFuzzyBase, ABC):
    """
    Базовый класс для нечеткой переменной
    """

    def __init__(self, name: str, a_fmethod: Optional[FuzzifyMethod] = None,
                 a_dfmethod: Optional[DefuzzifyMethod] = None):
        """
        Конструктор базового класса переменной

        Args:
            name: имя переменной
            a_fmethod: метод фаззификации
            a_dfmethod: метод дефаззификации
        """
        super().__init__(name=name)
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

    @abstractmethod
    def value(self, revform: List[int]) -> TFuzzySet:
        pass

    @property
    def ops(self) -> Optional[TOperationBase]:
        pass

    @ops.setter
    def ops(self, value: TOperationBase):
        pass

    @abstractmethod
    def is_value_exists(self, value: str) -> bool:
        pass

    @abstractmethod
    def is_term_exists(self, term: str) -> int:
        pass

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

    @fuzzify.setter
    def fuzzify(self, value: FuzzifyMethod):
        self._fuzzify = value

    @property
    def defuzzify(self) -> DefuzzifyMethod:
        """Получить метод дефаззификации"""
        return self._defuzzify

    @defuzzify.setter
    def defuzzify(self, value: DefuzzifyMethod):
        self._defuzzify = value

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

    @abstractmethod
    def _internal_fuzzificate(self, crisp: float) -> Optional['TFuzzySet']:
        """
        Внутренняя фаззификация (должен быть переопределен)

        Args:
            crisp: четкое значение

        Returns:
            нечеткое множество
        """
        pass

    @abstractmethod
    def _internal_defuzzificate(self, value: Optional['TFuzzySet']) -> float:
        """
        Внутренняя дефаззификация (должен быть переопределен)

        Args:
            value: нечеткое множество

        Returns:
            четкое значение
        """
        pass
