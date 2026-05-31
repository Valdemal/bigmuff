"""
Модуль с базовыми операциями над нечеткими множествами
"""

import math
from abc import ABC, abstractmethod
from typing import Optional

from .comparison import le
from .consts import Natural, Membership


class OperationBase(ABC):
    """
    Базовый класс для операций над нечеткими множествами.
    Реализует базис операций
    """

    def __init__(self, points: Natural = 100):
        """
        Конструктор базового класса операций

        Args:
            points: количество точек для дискретизации функции принадлежности
        """
        self._points = points

    @property
    def points(self):
        return self._points

    @points.setter
    def points(self, value: int):
        self._points = value

    @abstractmethod
    def t_norm(self, op1: Membership, op2: Membership) -> Membership:
        """
        Т-норма (как частный случай операция И)

        Args:
            op1: первый операнд (степень принадлежности)
            op2: второй операнд (степень принадлежности)

        Returns:
            результат применения Т-нормы
        """
        pass

    @abstractmethod
    def t_conorm(self, op1: Membership, op2: Membership) -> Membership:
        """
        Т-конорма (как частный случай операция ИЛИ)

        Args:
            op1: первый операнд (степень принадлежности)
            op2: второй операнд (степень принадлежности)

        Returns:
            результат применения Т-конормы
        """
        pass

    @abstractmethod
    def not_op(self, op: Membership) -> Membership:
        """
        Отрицание (операция НЕ)

        Args:
            op: операнд (степень принадлежности)

        Returns:
            результат отрицания
        """
        pass

    @abstractmethod
    def impl(self, op1: Membership, op2: Membership) -> Membership:
        """
        Импликация

        Args:
            op1: первый операнд (степень принадлежности)
            op2: второй операнд (степень принадлежности)

        Returns:
            результат импликации
        """
        pass

    @abstractmethod
    def comp_and(self, op1: Membership, op2: Membership) -> Membership:
        """
        Композиция в составном правиле (И)

        Args:
            op1: первый операнд
            op2: второй операнд

        Returns:
            результат композиции
        """
        pass

    @abstractmethod
    def comp_or(self, op1: Membership, op2: Membership) -> Membership:
        """
        Композиция в составном правиле (ИЛИ)

        Args:
            op1: первый операнд
            op2: второй операнд

        Returns:
            результат композиции
        """
        pass

    @abstractmethod
    def rule_comp(self, op1: Membership, op2: Membership) -> Membership:
        """
        Композиция результатов вывода двух правил

        Args:
            op1: первый операнд
            op2: второй операнд

        Returns:
            результат композиции правил
        """
        pass

    def pow(self, op: Membership, val: Membership) -> Membership:
        """
        Возведение в степень

        Args:
            op: основание
            val: показатель степени

        Returns:
            результат возведения в степень
        """
        return math.pow(op, val)

    @property
    @abstractmethod
    def name(self) -> str:
        """FCL Имя набора операций"""
        pass


class MaxMin(OperationBase):
    """
    Максиминный базис с композицией по минимуму
    """

    def __init__(self, points: Natural = 100):
        super().__init__(points)

    def t_norm(self, op1: Membership, op2: Membership) -> Membership:
        """Т-норма = минимум"""
        return min(op1, op2)

    def t_conorm(self, op1: Membership, op2: Membership) -> Membership:
        """Т-конорма = максимум"""
        return max(op1, op2)

    def not_op(self, op: Membership) -> Membership:
        """Отрицание = 1 - op"""
        return 1.0 - op

    def impl(self, op1: Membership, op2: Membership) -> Membership:
        """Импликация = минимум"""
        return min(op1, op2)

    def comp_and(self, op1: Membership, op2: Membership) -> Membership:
        """Композиция И = минимум"""
        return min(op1, op2)

    def comp_or(self, op1: Membership, op2: Membership) -> Membership:
        """Композиция ИЛИ = максимум"""
        return max(op1, op2)

    def rule_comp(self, op1: Membership, op2: Membership) -> Membership:
        """Композиция правил = максимум"""
        return max(op1, op2)

    @property
    def name(self) -> str:
        return "MAXMIN"


class SumProd(OperationBase):
    """
    Гладкий базис сумма-умножение с композицией по минимуму
    """

    def __init__(self, points: Natural = 100):
        super().__init__(points)

    def t_norm(self, op1: Membership, op2: Membership) -> Membership:
        """Т-норма = произведение"""
        return op1 * op2

    def t_conorm(self, op1: Membership, op2: Membership) -> Membership:
        """Т-конорма = op1 + op2 - op1 * op2"""
        return op1 + op2 - op1 * op2

    def not_op(self, op: Membership) -> Membership:
        """Отрицание = 1 - op"""
        return 1.0 - op

    def impl(self, op1: Membership, op2: Membership) -> Membership:
        """Импликация = произведение"""
        return op1 * op2

    def comp_and(self, op1: Membership, op2: Membership) -> Membership:
        """Композиция И = произведение"""
        return op1 * op2

    def comp_or(self, op1: Membership, op2: Membership) -> Membership:
        """Композиция ИЛИ = op1 + op2 - op1 * op2"""
        return op1 + op2 - op1 * op2

    def rule_comp(self, op1: Membership, op2: Membership) -> Membership:
        """Композиция правил = op1 + op2 - op1 * op2"""
        return op1 + op2 - op1 * op2

    @property
    def name(self) -> str:
        return "SUMPROD"


class TLukasiewicz(MaxMin):
    """
    Логическая система Лукасевича
    """

    def __init__(self, points: Natural = 100):
        super().__init__(points)

    def impl(self, op1: Membership, op2: Membership) -> Membership:
        """Импликация Лукасевича = min(1, 1 - op1 + op2)"""
        return min(1.0, 1.0 - op1 + op2)

    def comp_and(self, op1: Membership, op2: Membership) -> Membership:
        """Композиция И = максимум"""
        return max(op1, op2)

    def comp_or(self, op1: Membership, op2: Membership) -> Membership:
        """Композиция ИЛИ = минимум"""
        return min(op1, op2)

    def rule_comp(self, op1: Membership, op2: Membership) -> Membership:
        """Композиция правил = минимум"""
        return min(op1, op2)

    @property
    def name(self) -> str:
        return "LUKASIEWICZ"


class TKDLogic(MaxMin):
    """
    KD - логика
    """

    def __init__(self, points: Natural = 100):
        super().__init__(points)

    def impl(self, op1: Membership, op2: Membership) -> Membership:
        """Импликация KD = max(1 - op1, op2)"""
        return max(1.0 - op1, op2)

    def comp_and(self, op1: Membership, op2: Membership) -> Membership:
        """Композиция И = максимум"""
        return max(op1, op2)

    def comp_or(self, op1: Membership, op2: Membership) -> Membership:
        """Композиция ИЛИ = минимум"""
        return min(op1, op2)

    def rule_comp(self, op1: Membership, op2: Membership) -> Membership:
        """Композиция правил = минимум"""
        return min(op1, op2)

    @property
    def name(self) -> str:
        return "KD_LOGIC"


class TZ2Logic(MaxMin):
    """
    Z2 - логика
    """

    def __init__(self, points: Natural = 100):
        super().__init__(points)

    def impl(self, op1: Membership, op2: Membership) -> Membership:
        """Импликация Z2"""
        return 1.0 if le(op1, op2) else max(1.0 - op1, op2)

    def comp_and(self, op1: Membership, op2: Membership) -> Membership:
        """Композиция И = максимум"""
        return max(op1, op2)

    def comp_or(self, op1: Membership, op2: Membership) -> Membership:
        """Композиция ИЛИ = минимум"""
        return min(op1, op2)

    def rule_comp(self, op1: Membership, op2: Membership) -> Membership:
        """Композиция правил = минимум"""
        return min(op1, op2)

    @property
    def name(self) -> str:
        return "Z2_LOGIC"


class TZ3Logic(MaxMin):
    """
    Z3 - логика
    """

    def __init__(self, points: Natural = 100):
        super().__init__(points)

    def impl(self, op1: Membership, op2: Membership) -> Membership:
        """Импликация Z3"""
        if le(op1, op2):
            return 1.0
        # Защита от деления на ноль
        denominator = 1.0 - op2 + op1
        if abs(denominator) < 1e-10:
            return 0.0
        return op2 / denominator

    def comp_and(self, op1: Membership, op2: Membership) -> Membership:
        """Композиция И = максимум"""
        return max(op1, op2)

    def comp_or(self, op1: Membership, op2: Membership) -> Membership:
        """Композиция ИЛИ = минимум"""
        return min(op1, op2)

    def rule_comp(self, op1: Membership, op2: Membership) -> Membership:
        """Композиция правил = минимум"""
        return min(op1, op2)

    @property
    def name(self) -> str:
        return "Z3_LOGIC"


# Создаем глобальные экземпляры для каждой логической системы
obMaxMin = MaxMin()
obSumProd = SumProd()
obLukasiewicz = TLukasiewicz()
obKDLogic = TKDLogic()
obZ2Logic = TZ2Logic()
obZ3Logic = TZ3Logic()

