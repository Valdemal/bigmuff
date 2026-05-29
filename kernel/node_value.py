"""
Модуль для работы с узловыми точками функции принадлежности
"""

from typing import Optional

from .base import TNeuroFuzzyBase, INRANGE, EPSILON
from .consts import BaseSet, Membership
from .exceptions import EMemberFunc, NFE_DOM_INVALID, NFE_OUT_OF_DOMAIN
from .member_func.base import TMemberFunc


class TNodeValue(TNeuroFuzzyBase):
    """
    Значение функции принадлежности в узловой точке
    """

    def __init__(self,
                 x_value: Optional[BaseSet] = 0,
                 y_value: Optional[Membership] = 0,
                 a_owner: Optional['TMemberFunc'] = None):
        """
        Конструктор узловой точки

        Args:
            x_value: значение базового множества (x координата)
            y_value: степень принадлежности (y координата)
            a_owner: владелец (функция принадлежности)
        """
        # todo проблемный конструктор
        super().__init__(a_owner)
        self._x_value = x_value
        self._y_value = y_value

        # Проверка значения степени принадлежности
        if self._y_value < 0.0 or self._y_value > 1.0:
            raise EMemberFunc("", NFE_DOM_INVALID)

        # Проверка нахождения в области определения (если есть владелец)
        if a_owner is not None:
            if not INRANGE(self._x_value, a_owner.inf, a_owner.sup):
                raise EMemberFunc("", NFE_OUT_OF_DOMAIN)

    @property
    def x(self) -> BaseSet:
        """Получить значение X (базовое множество)"""
        return self._x_value

    @x.setter
    def x(self, value: BaseSet):
        """Установить значение X"""
        # Проверка нахождения в области определения (если есть владелец)
        if self.owner is not None:
            # Импортируем TMemberFunc только при необходимости, чтобы избежать циклических импортов
            if not INRANGE(value, self.owner.inf, self.owner.sup):
                raise EMemberFunc("", NFE_OUT_OF_DOMAIN)
        self._x_value = value

    @property
    def dom(self) -> Membership:
        """Получить степень принадлежности"""
        return self._y_value

    @dom.setter
    def dom(self, value: Membership):
        """Установить степень принадлежности"""
        if value < 0.0 or value > 1.0:
            raise EMemberFunc("", NFE_DOM_INVALID)
        self._y_value = value

    def __eq__(self, other: object) -> bool:
        """Оператор сравнения на равенство"""
        if not isinstance(other, TNodeValue):
            return False
        return (abs(self._x_value - other._x_value) < EPSILON and
                abs(self._y_value - other._y_value) < EPSILON and
                self.owner == other.owner)

    def __str__(self) -> str:
        """Строковое представление в формате FCL"""
        return f"({self._x_value}, {self._y_value})"


# Вспомогательный класс для работы с точками
class TNodeValueList:
    """
    Список узловых точек с дополнительными методами
    """

    def __init__(self):
        self._points: list[TNodeValue] = []

    def add(self, x: BaseSet, y: Membership, owner: Optional['TMemberFunc'] = None) -> TNodeValue:
        """
        Добавить новую точку

        Args:
            x: значение X
            y: степень принадлежности
            owner: владелец

        Returns:
            созданная точка
        """
        point = TNodeValue(x, y, owner)
        self._points.append(point)
        return point

    def remove(self, index: int):
        """
        Удалить точку по индексу

        Args:
            index: индекс точки
        """
        if 0 <= index < len(self._points):
            del self._points[index]

    def get(self, index: int) -> TNodeValue:
        """
        Получить точку по индексу

        Args:
            index: индекс точки

        Returns:
            точка
        """
        return self._points[index]

    def __len__(self) -> int:
        return len(self._points)

    def __iter__(self):
        return iter(self._points)

    def __getitem__(self, index: int) -> TNodeValue:
        return self._points[index]

    def __setitem__(self, index: int, value: TNodeValue):
        self._points[index] = value

    def sort(self):
        """Сортировка точек по значению X"""
        self._points.sort(key=lambda p: p.x)

    def is_sorted(self) -> bool:
        """
        Проверка, упорядочены ли точки по X

        Returns:
            True если точки упорядочены по возрастанию X
        """
        for i in range(1, len(self._points)):
            if self._points[i].x < self._points[i-1].x:
                return False
        return True
