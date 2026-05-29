import sys
from abc import abstractmethod, ABC
from typing import List

from kernel.base import TNeuroFuzzyBase, LS, GE, INRANGE, GT, EQ, ZR
from kernel.consts import BaseSet, Membership, Natural, MemberFuncTypeName
from kernel.enums import MemberFuncType
from kernel.exceptions import EMemberFunc, NFE_INVALID_BASE, NFE_INVALID_INDEX, NFE_OUT_OF_DOMAIN


class TMemberFunc(TNeuroFuzzyBase, ABC):
    """
    Виртуальный базовый класс функции принадлежности
    """

    def __init__(self, a_inf: BaseSet, a_sup: BaseSet):
        """
        Конструктор функции принадлежности

        Args:
            a_inf: нижняя граница базового множества
            a_sup: верхняя граница базового множества
        """
        super().__init__()

        if GE(a_inf, a_sup):
            raise EMemberFunc("", NFE_INVALID_BASE)

        self._inf_base = a_inf
        self._sup_base = a_sup
        self._type = MemberFuncType.mfNA
        self._nodes: List['TNodeValue'] = []
        self._data: List[Membership] = []

    @property
    def inf(self) -> BaseSet:
        """Получить нижнюю границу базового множества"""
        return self._inf_base

    @inf.setter
    def inf(self, value: BaseSet):
        """Установить нижнюю границу базового множества"""
        if LS(value, self._sup_base):
            self._inf_base = value
            self._adjust_nodes()
        else:
            raise EMemberFunc("", NFE_INVALID_BASE)

    @property
    def sup(self) -> BaseSet:
        """Получить верхнюю границу базового множества"""
        return self._sup_base

    @sup.setter
    def sup(self, value: BaseSet):
        """Установить верхнюю границу базового множества"""
        if LS(self._inf_base, value):
            self._sup_base = value
            self._adjust_nodes()
        else:
            raise EMemberFunc("", NFE_INVALID_BASE)

    @property
    def nodes(self):
        return self._nodes

    @property
    def data(self) -> List[Membership]:
        return self._data

    @property
    def type(self) -> MemberFuncType:
        """Получить тип функции принадлежности"""
        return self._type

    @classmethod
    def is_nodes(cls) -> bool:
        """
        Функция принадлежности представлена опорными точками

        Returns:
            True если представлена точками
        """
        return False

    @classmethod
    def is_vector(cls) -> bool:
        """
        Функция принадлежности представлена как массив

        Returns:
            True если представлена вектором
        """
        return False

    def __call__(self, value: BaseSet) -> Membership:
        """
        Получение значения функции принадлежности

        Args:
            value: значение базового множества

        Returns:
            степень принадлежности
        """
        if INRANGE(value, self._inf_base, self._sup_base):
            return self._get_value(value)
        else:
            raise EMemberFunc("", NFE_OUT_OF_DOMAIN)

    def add_node(self, value: 'TNodeValue'):
        """
        Добавить опорную точку с упорядочиванием

        Args:
            value: добавляемая точка
        """
        if INRANGE(value.x, self._inf_base, self._sup_base):
            last = len(self._nodes) - 1

            i = 0
            while i <= last and GT(value.x, self._nodes[i].x):
                i += 1

            if i > last:
                self._nodes.append(value)
            elif EQ(value.x, self._nodes[i].x):
                self._nodes[i].dom = value.dom
            else:
                self._nodes.insert(i, value)

            self._nodes[i].owner = self
        else:
            raise EMemberFunc("", NFE_OUT_OF_DOMAIN)

    def append_node(self, value: 'TNodeValue'):
        """
        Добавить точку без переупорядочивания

        Args:
            value: добавляемая точка
        """
        if INRANGE(value.x, self._inf_base, self._sup_base):
            self._nodes.append(value)
            self._nodes[-1].owner = self
        else:
            raise EMemberFunc("", NFE_OUT_OF_DOMAIN)

    def delete_node(self, index: Natural):
        """
        Удалить опорную точку

        Args:
            index: индекс удаляемой точки
        """
        if index < len(self._nodes):
            del self._nodes[index]
        else:
            raise EMemberFunc("", NFE_INVALID_INDEX)

    def _get_index(self, value: BaseSet) -> Natural:
        """
        Получение индекса элемента вектора

        Args:
            value: значение базового множества

        Returns:
            индекс в векторе
        """
        if len(self._data) <= 1:
            return 0
        return int((value - self._inf_base) * (len(self._data) - 1) / (self._sup_base - self._inf_base))

    def _adjust_nodes(self):
        """Привести узловые точки в соответствие с границами"""
        for i in range(len(self._nodes)):
            if GT(self._nodes[i].x, self._sup_base):
                self._nodes[i].x = self._sup_base
            elif LS(self._nodes[i].x, self._inf_base):
                self._nodes[i].x = self._inf_base

    @abstractmethod
    def _get_value(self, value: BaseSet) -> Membership:
        """
        Получение значения функции принадлежности (должен быть переопределен)

        Args:
            value: значение базового множества

        Returns:
            степень принадлежности
        """
        pass

    def cog(self, points: Natural) -> BaseSet:
        """
        Центр тяжести (Center of Gravity)

        Args:
            points: количество точек дискретизации

        Returns:
            четкое значение
        """
        x = self._inf_base
        step = (self._sup_base - self._inf_base) / (points - 1)
        sum_xm = 0.0
        sum_m = 0.0

        for _ in range(points):
            val = self(x)
            sum_xm += x * val
            sum_m += val
            x += step

        if ZR(sum_m):
            return (self._sup_base - self._inf_base) / 2.0
        else:
            return sum_xm / sum_m

    def coa(self, points: Natural) -> BaseSet:
        """
        Центр площади (Center of Area)

        Args:
            points: количество точек дискретизации

        Returns:
            четкое значение
        """
        x = self._inf_base
        step = (self._sup_base - self._inf_base) / (points - 1)
        total_sum = 0.0
        half_sum = 0.0

        for _ in range(points):
            total_sum += self(x)
            x += step

        total_sum /= 2.0
        x = self._inf_base
        i = 0

        while i < points and LS(half_sum, total_sum):
            half_sum += self(x)
            x += step
            i += 1

        if ZR(half_sum) or ZR(total_sum):
            return (self._sup_base - self._inf_base) / 2.0
        else:
            return x - step

    def lm(self, points: Natural) -> BaseSet:
        """
        Левый максимум (Left Most Maximum)

        Args:
            points: количество точек дискретизации

        Returns:
            четкое значение
        """
        x = self._inf_base
        step = (self._sup_base - self._inf_base) / (points - 1)
        max_val = 0.0
        x_max = self._inf_base

        for _ in range(points):
            mi = self(x)
            if GT(mi, max_val):
                max_val = mi
                x_max = x
            x += step

        return x_max

    def rm(self, points: Natural) -> BaseSet:
        """
        Правый максимум (Right Most Maximum)

        Args:
            points: количество точек дискретизации

        Returns:
            четкое значение
        """
        x = self._sup_base
        step = (self._sup_base - self._inf_base) / (points - 1)
        max_val = 0.0
        x_max = self._sup_base

        for _ in range(points):
            mi = self(x)
            if GT(mi, max_val):
                max_val = mi
                x_max = x
            x -= step

        return x_max

    def mom(self, points: Natural) -> BaseSet:
        """
        Среднее максимумов (Mean of Maximums)

        Args:
            points: количество точек дискретизации

        Returns:
            четкое значение
        """
        x = self._inf_base
        step = (self._sup_base - self._inf_base) / (points - 1)
        max_val = 0.0
        x_start = self._inf_base
        x_end = self._inf_base

        for _ in range(points):
            mi = self(x)
            if GT(mi, max_val):
                max_val = mi
                x_start = x
                x_end = x
            if EQ(mi, max_val):
                x_end = x
            x += step

        return (x_end + x_start) / 2.0

    def inverse(self):
        """
        Инвертирование функции принадлежности: m(x) = 1 - m(x)
        """
        if self.is_nodes():
            for i in range(len(self._nodes)):
                self._nodes[i].dom = 1.0 - self._nodes[i].dom
        elif self.is_vector():
            for i in range(len(self._data)):
                self._data[i] = 1.0 - self._data[i]
