"""
Модуль с базовыми операциями над нечеткими множествами
"""

import math
from abc import ABC, abstractmethod
from typing import Optional

from .base import MIN, MAX, LE
from .consts import Natural, Membership


class TOperationBase(ABC):
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


class TMaxMin(TOperationBase):
    """
    Максиминный базис с композицией по минимуму
    """

    def __init__(self, points: Natural = 100):
        super().__init__(points)

    def t_norm(self, op1: Membership, op2: Membership) -> Membership:
        """Т-норма = минимум"""
        return MIN(op1, op2)

    def t_conorm(self, op1: Membership, op2: Membership) -> Membership:
        """Т-конорма = максимум"""
        return MAX(op1, op2)

    def not_op(self, op: Membership) -> Membership:
        """Отрицание = 1 - op"""
        return 1.0 - op

    def impl(self, op1: Membership, op2: Membership) -> Membership:
        """Импликация = минимум"""
        return MIN(op1, op2)

    def comp_and(self, op1: Membership, op2: Membership) -> Membership:
        """Композиция И = минимум"""
        return MIN(op1, op2)

    def comp_or(self, op1: Membership, op2: Membership) -> Membership:
        """Композиция ИЛИ = максимум"""
        return MAX(op1, op2)

    def rule_comp(self, op1: Membership, op2: Membership) -> Membership:
        """Композиция правил = максимум"""
        return MAX(op1, op2)

    @property
    def name(self) -> str:
        return "MAXMIN"


class TSumProd(TOperationBase):
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


class TLukasiewicz(TMaxMin):
    """
    Логическая система Лукасевича
    """

    def __init__(self, points: Natural = 100):
        super().__init__(points)

    def impl(self, op1: Membership, op2: Membership) -> Membership:
        """Импликация Лукасевича = min(1, 1 - op1 + op2)"""
        return MIN(1.0, 1.0 - op1 + op2)

    def comp_and(self, op1: Membership, op2: Membership) -> Membership:
        """Композиция И = максимум"""
        return MAX(op1, op2)

    def comp_or(self, op1: Membership, op2: Membership) -> Membership:
        """Композиция ИЛИ = минимум"""
        return MIN(op1, op2)

    def rule_comp(self, op1: Membership, op2: Membership) -> Membership:
        """Композиция правил = минимум"""
        return MIN(op1, op2)

    @property
    def name(self) -> str:
        return "LUKASIEWICZ"


class TKDLogic(TMaxMin):
    """
    KD - логика
    """

    def __init__(self, points: Natural = 100):
        super().__init__(points)

    def impl(self, op1: Membership, op2: Membership) -> Membership:
        """Импликация KD = max(1 - op1, op2)"""
        return MAX(1.0 - op1, op2)

    def comp_and(self, op1: Membership, op2: Membership) -> Membership:
        """Композиция И = максимум"""
        return MAX(op1, op2)

    def comp_or(self, op1: Membership, op2: Membership) -> Membership:
        """Композиция ИЛИ = минимум"""
        return MIN(op1, op2)

    def rule_comp(self, op1: Membership, op2: Membership) -> Membership:
        """Композиция правил = минимум"""
        return MIN(op1, op2)

    @property
    def name(self) -> str:
        return "KD_LOGIC"


class TZ2Logic(TMaxMin):
    """
    Z2 - логика
    """

    def __init__(self, points: Natural = 100):
        super().__init__(points)

    def impl(self, op1: Membership, op2: Membership) -> Membership:
        """Импликация Z2"""
        return 1.0 if LE(op1, op2) else MAX(1.0 - op1, op2)

    def comp_and(self, op1: Membership, op2: Membership) -> Membership:
        """Композиция И = максимум"""
        return MAX(op1, op2)

    def comp_or(self, op1: Membership, op2: Membership) -> Membership:
        """Композиция ИЛИ = минимум"""
        return MIN(op1, op2)

    def rule_comp(self, op1: Membership, op2: Membership) -> Membership:
        """Композиция правил = минимум"""
        return MIN(op1, op2)

    @property
    def name(self) -> str:
        return "Z2_LOGIC"


class TZ3Logic(TMaxMin):
    """
    Z3 - логика
    """

    def __init__(self, points: Natural = 100):
        super().__init__(points)

    def impl(self, op1: Membership, op2: Membership) -> Membership:
        """Импликация Z3"""
        if LE(op1, op2):
            return 1.0
        # Защита от деления на ноль
        denominator = 1.0 - op2 + op1
        if abs(denominator) < 1e-10:
            return 0.0
        return op2 / denominator

    def comp_and(self, op1: Membership, op2: Membership) -> Membership:
        """Композиция И = максимум"""
        return MAX(op1, op2)

    def comp_or(self, op1: Membership, op2: Membership) -> Membership:
        """Композиция ИЛИ = минимум"""
        return MIN(op1, op2)

    def rule_comp(self, op1: Membership, op2: Membership) -> Membership:
        """Композиция правил = минимум"""
        return MIN(op1, op2)

    @property
    def name(self) -> str:
        return "Z3_LOGIC"


# Создаем глобальные экземпляры для каждой логической системы
obMaxMin = TMaxMin()
obSumProd = TSumProd()
obLukasiewicz = TLukasiewicz()
obKDLogic = TKDLogic()
obZ2Logic = TZ2Logic()
obZ3Logic = TZ3Logic()


def get_operation_base_object(index: int) -> Optional[TOperationBase]:
    """
    Получить объект операций по индексу

    Args:
        index: индекс операции (0-5)

    Returns:
        объект операции или None если индекс неверный
    """
    operations = {
        0: obMaxMin,
        1: obSumProd,
        2: obLukasiewicz,
        3: obKDLogic,
        4: obZ2Logic,
        5: obZ3Logic
    }
    return operations.get(index)


def get_operation_base_index(obj: TOperationBase) -> int:
    """
    Получить индекс объекта операций

    Args:
        obj: объект операции

    Returns:
        индекс операции (0-5) или -1 если объект не найден
    """
    # Создаем словарь для сравнения по имени класса
    # Используем type(obj).__name__ для определения типа
    operation_classes = {
        "TMaxMin": 0,
        "TSumProd": 1,
        "TLukasiewicz": 2,
        "TKDLogic": 3,
        "TZ2Logic": 4,
        "TZ3Logic": 5
    }

    class_name = type(obj).__name__
    return operation_classes.get(class_name, -1)
