from typing import Optional

from kernel.consts import BaseSet, Natural, Membership
from kernel.enums import MemberFuncType
from kernel.member_func.base import TMemberFunc
from kernel.base import EQ


class TMemberFuncLnVect(TMemberFunc):
    """
    Функция принадлежности, заданная вектором значений
    """

    def __init__(self, a_inf: BaseSet, a_sup: BaseSet, data_count: Optional[Natural] = None,
                 source_mf: Optional[TMemberFunc] = None):
        """
        Args:
            a_inf: нижняя граница
            a_sup: верхняя граница
            data_count: количество точек в векторе
            source_mf: исходная функция принадлежности для векторизации
        """
        super().__init__(a_inf, a_sup)
        self._type = MemberFuncType.mfLnVector

        if source_mf is not None and data_count is not None:
            # Векторизация существующей функции
            self._data = [0.0] * data_count
            x = source_mf.inf
            step = (source_mf.sup - source_mf.inf) / (data_count - 1)

            for i in range(data_count):
                self._data[i] = source_mf(x)
                x += step

        elif data_count is not None:
            # Пустой вектор
            self._data = [0.0] * data_count

        else:
            # Пустой конструктор
            self._data = []

    def is_nodes(self) -> bool:
        """Функция представлена опорными точками"""
        return False

    def is_vector(self) -> bool:
        """Функция представлена как массив"""
        return True

    def __setitem__(self, index: Natural, value: Membership):
        """Установить значение вектора"""
        if 0 <= index < len(self._data):
            self._data[index] = value

    def __getitem__(self, index: Natural) -> Membership:
        """Получить значение вектора"""
        return self._data[index]

    def _get_value(self, value: BaseSet) -> Membership:
        """Получить значение функции принадлежности (линейная интерполяция)"""
        if len(self._data) <= 1:
            return self._data[0] if self._data else 0.0

        i = self._get_index(value)

        if i < 0:
            i = 0
        if i >= len(self._data) - 1:
            i = len(self._data) - 2

        step = (self._sup_base - self._inf_base) / (len(self._data) - 1)
        x1 = self._inf_base + i * step
        x2 = self._inf_base + (i + 1) * step

        y1 = self._data[i]
        y2 = self._data[i + 1]

        if EQ(value, x1):
            return y1
        if EQ(value, x2):
            return y2

        return y1 + (y2 - y1) / (x2 - x1) * (value - x1)