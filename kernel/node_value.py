"""
Модуль для работы с узловыми точками функции принадлежности
"""

from typing import Optional

from .comparison import inrange, eq
from .consts import Crisp, Membership
from .exceptions import EMemberFunc, NFE_DOM_INVALID, NFE_OUT_OF_DOMAIN
from .member_func.base import TMemberFunc


class TNodeValue:
    """
    Значение функции принадлежности в узловой точке
    """

    def __init__(self, x: Optional[Crisp] = 0, y: Optional[Membership] = 0, owner: Optional['TMemberFunc'] = None):
        """
        Конструктор узловой точки

        Args:
            x: значение базового множества (x координата)
            y: степень принадлежности (y координата)
            owner: владелец (функция принадлежности)
        """
        super().__init__()
        self._owner = owner
        self._x = x
        self._y = y

        # Проверка значения степени принадлежности
        if not inrange(self._y, 0.0, 1.0):
            raise EMemberFunc("", NFE_DOM_INVALID)

        # Проверка нахождения в области определения (если есть владелец)
        if owner is not None and not inrange(self._x, owner.inf, owner.sup):
            raise EMemberFunc("", NFE_OUT_OF_DOMAIN)

    @property
    def x(self) -> Crisp:
        """Получить значение X (базовое множество)"""
        return self._x

    @x.setter
    def x(self, value: Crisp):
        """Установить значение X"""
        # Проверка нахождения в области определения (если есть владелец)
        if self._owner is not None and not inrange(value, self._owner.inf, self._owner.sup):
            raise EMemberFunc("", NFE_OUT_OF_DOMAIN)

        self._x = value

    @property
    def dom(self) -> Membership:
        """Получить степень принадлежности"""
        return self._y

    @dom.setter
    def dom(self, value: Membership):
        """Установить степень принадлежности"""
        if not inrange(value, 0.0, 1.0):
            raise EMemberFunc("", NFE_DOM_INVALID)
        self._y = value

    def __eq__(self, other: 'TNodeValue') -> bool:
        return eq(self._x, other._x) and eq(self._y, other._y) and self._owner == other._owner

    def __str__(self) -> str:
        """Строковое представление в формате FCL"""
        return f"({self._x}, {self._y})"
