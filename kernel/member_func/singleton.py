from typing import Optional

from .base import TMemberFunc
from ..comparison import eq
from ..consts import Crisp, Membership, Natural
from ..enums import MemberFuncType
from ..node_value import TNodeValue


class TMemberFuncSingle(TMemberFunc):
    """
    Синглетон - функция принадлежности в виде одной точки
    """

    def __init__(self, val: Optional[Crisp] = None, h: Membership = 1.0,
                 inf: Crisp = 0.0, sup: Crisp = 0.0):
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

    def cog(self, points: Natural) -> Crisp:
        """Центр тяжести"""
        return self._nodes[0].x

    def coa(self, points: Natural) -> Crisp:
        """Центр площади"""
        return self._nodes[0].x

    def lm(self, points: Natural) -> Crisp:
        """Левый максимум"""
        return self._nodes[0].x

    def rm(self, points: Natural) -> Crisp:
        """Правый максимум"""
        return self._nodes[0].x

    def mom(self, points: Natural) -> Crisp:
        """Среднее максимумов"""
        return self._nodes[0].x

    def _get_value(self, value: Crisp) -> Membership:
        """Получить значение функции принадлежности"""
        return self._nodes[0].dom if eq(value, self._nodes[0].x) else 0.0

