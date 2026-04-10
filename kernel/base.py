"""
Модуль с базовыми определениями для нейро-нечеткой системы
"""

from typing import Optional

from kernel.consts import EPSILON
from kernel.member_func.vector import TMemberFuncLnVect


# Константы для сравнения чисел с плавающей точкой


def EQ(x: float, y: float) -> bool:
    """Приблизительное равенство"""
    return abs(x - y) < EPSILON

def LS(x: float, y: float) -> bool:
    """Строго меньше (с учетом погрешности)"""
    return x - y < -EPSILON

def GT(x: float, y: float) -> bool:
    """Строго больше (с учетом погрешности)"""
    return x - y > EPSILON

def LE(x: float, y: float) -> bool:
    """Меньше или равно (с учетом погрешности)"""
    return x - y < EPSILON

def GE(x: float, y: float) -> bool:
    """Больше или равно (с учетом погрешности)"""
    return x - y > -EPSILON

def ZR(x: float) -> bool:
    """Приблизительно равно нулю"""
    return abs(x) < EPSILON

def MIN(a: float, b: float) -> float:
    """Минимум с учетом погрешности"""
    return a if LE(a, b) else b

def MAX(a: float, b: float) -> float:
    """Максимум с учетом погрешности"""
    return a if GT(a, b) else b

def INRANGE(x: float, a: float, b: float) -> bool:
    """Проверка нахождения в диапазоне [a, b]"""
    return GE(x, a) and LE(x, b)



class TNeuroFuzzyBase:
    """Базовый класс для нейро-нечеткой системы"""

    def __init__(self, owner: Optional['TNeuroFuzzyBase'] = None):
        """
        Конструктор класса

        Args:
            owner: владелец объекта (родительский объект)
        """
        self._owner = owner

    @property
    def owner(self) -> Optional['TNeuroFuzzyBase']:
        """Получить владельца объекта"""
        return self._owner

    @owner.setter
    def owner(self, value: Optional['TNeuroFuzzyBase']):
        """Установить владельца объекта"""
        self._owner = value

RESULT_FUNC = TMemberFuncLnVect