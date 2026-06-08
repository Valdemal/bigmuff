from abc import ABC, abstractmethod
from typing import Optional, List

from kernel.consts import Crisp
from kernel.enums import DefuzzifyMethod, ValueType, VariableType
from kernel.fuzzification import FuzzificationMethod
from kernel.fuzzy_set import TFuzzySet
from kernel.mixins import Named, OperationBased, RangeDefined


class CustomVariable(Named, OperationBased, RangeDefined, ABC):
    """
    Базовый класс для нечеткой переменной
    """

    def __init__(self, name: str, inf: Crisp, sup: Crisp,a_fmethod: Optional[FuzzificationMethod] = None,
                 a_dfmethod: Optional[DefuzzifyMethod] = DefuzzifyMethod.dmNA):
        """
        Конструктор базового класса переменной

        Args:
            name: имя переменной
            a_fmethod: метод фаззификации
            a_dfmethod: метод дефаззификации
        """
        super().__init__(name=name)
        RangeDefined.__init__(self, inf, sup)
        self._value_type = ValueType.valNA
        self._type = VariableType.vtNA
        self._units = ""
        self._fuzzify = a_fmethod
        self._defuzzify = a_dfmethod

    @abstractmethod
    def value(self, revform: List[int]) -> TFuzzySet:
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
    def fuzzify(self) -> FuzzificationMethod:
        """Получить метод фаззификации"""
        return self._fuzzify

    @fuzzify.setter
    def fuzzify(self, value: FuzzificationMethod):
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

    def fuzzificate(self, crisp: Crisp) -> TFuzzySet:
        """
        Процедура фаззификации

        Args:
            crisp: четкое значение

        Returns:
            нечеткое множество
        """
        if self._fuzzify is None:
            raise Exception()

        return TFuzzySet(f"Fuzzy {crisp}", self._fuzzify(crisp, self), ops=self.ops)

    @abstractmethod
    def defuzzificate(self, value: TFuzzySet) -> Crisp:
        """
        Процедура дефаззификации

        Args:
            value: нечеткое множество

        Returns:
            четкое значение
        """
        pass