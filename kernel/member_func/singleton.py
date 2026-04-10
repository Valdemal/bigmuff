from typing import Optional

from .base import TMemberFunc, EQ
from ..consts import BaseSet, Membership, Natural
from ..enums import MemberFuncType
from ..node_value import TNodeValue


class TMemberFuncSingle(TMemberFunc):
    """
    Синглетон - функция принадлежности в виде одной точки
    """

    def __init__(self, val: Optional[BaseSet] = None, h: Membership = 1.0,
                 inf: BaseSet = 0.0, sup: BaseSet = 0.0):
        """
        Args:
            val: значение точки
            h: высота (степень принадлежности)
            inf: нижняя граница
            sup: верхняя граница
        """
        super().__init__(inf, sup)

        if val is not None:
            self.append_node(TNodeValue(val, h, self))

        self._type = MemberFuncType.mfSingleton

    def is_nodes(self) -> bool:
        """Функция представлена опорными точками"""
        return True

    def is_vector(self) -> bool:
        """Функция представлена как массив"""
        return False

    def cog(self, points: Natural) -> BaseSet:
        """Центр тяжести"""
        return self._node[0].x

    def coa(self, points: Natural) -> BaseSet:
        """Центр площади"""
        return self._node[0].x

    def lm(self, points: Natural) -> BaseSet:
        """Левый максимум"""
        return self._node[0].x

    def rm(self, points: Natural) -> BaseSet:
        """Правый максимум"""
        return self._node[0].x

    def mom(self, points: Natural) -> BaseSet:
        """Среднее максимумов"""
        return self._node[0].x

    def _get_value(self, value: BaseSet) -> Membership:
        """Получить значение функции принадлежности"""
        return self._node[0].dom if EQ(value, self._node[0].x) else 0.0

