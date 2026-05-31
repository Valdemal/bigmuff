from typing import Optional

from kernel.comparison import eq
from kernel.consts import Crisp, Natural, Membership
from kernel.enums import MemberFuncType
from kernel.member_func.base import TMemberFunc

class TMemberFuncLnVect(TMemberFunc):
    """
    Функция принадлежности, заданная вектором значений
    """

    def __init__(self, func: TMemberFunc, data_count: Natural):
        super().__init__(func.inf, func.sup)
        self._type = MemberFuncType.mfLnVector
        self._data = [0.0] * data_count
        x, step = func.inf, (func.sup - func.inf) / (data_count - 1)

        for i in range(data_count):
            self._data[i] = func(x)
            x += step


    def is_nodes(self) -> bool:
        """Функция представлена опорными точками"""
        return False

    def is_vector(self) -> bool:
        """Функция представлена как массив"""
        return True

    def __setitem__(self, index: Natural, value: Membership):
        """Установить значение вектора"""
        self._data[index] = value

    def __getitem__(self, index: Natural) -> Membership:
        """Получить значение вектора"""
        return self._data[index]

    def _get_value(self, value: Crisp) -> Membership:
        """Получить значение функции принадлежности (линейная интерполяция)"""
        i = self._get_index(value)


        step = (self._sup_base - self._inf_base) / (len(self._data) - 1)
        x1 = self._inf_base + i * step
        x2 = self._inf_base + (i + 1) * step

        y1 = self._data[i]
        if eq(value, x1):
            return y1

        y2 = self._data[i + 1]
        if eq(value, x2):
            return y2

        return y1 + (y2 - y1) / (x2 - x1) * (value - x1)