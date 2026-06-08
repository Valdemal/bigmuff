from abc import abstractmethod, ABC
from typing import List

from kernel.comparison import inrange, gt, eq, ls
from kernel.consts import Crisp, Membership, Natural
from kernel.enums import MemberFuncType
from kernel.exceptions import EMemberFunc, NFE_INVALID_INDEX, NFE_OUT_OF_DOMAIN
from kernel.mixins import RangeDefined


class TMemberFunc(ABC, RangeDefined):
    """
    Виртуальный базовый класс функции принадлежности
    """

    def __init__(self, a_inf: Crisp, a_sup: Crisp):
        """
        Конструктор функции принадлежности

        Args:
            a_inf: нижняя граница базового множества
            a_sup: верхняя граница базового множества
        """
        RangeDefined.__init__(self, a_inf, a_sup)
        self._type = MemberFuncType.mfNA
        self._nodes: List['TNodeValue'] = []
        self._data: List[Membership] = []

    def _set_inf(self, value):
        super()._set_inf(value)
        self._adjust_nodes()

    def _set_sup(self, value):
        super()._set_sup(value)
        self._adjust_nodes()

    @property
    def nodes(self):
        return self._nodes

    @property
    def data(self) -> List[Membership]:
        return self._data

    def __setitem__(self, index: Natural, value: Membership):
        """Установить значение вектора"""
        if self.is_nodes():
            self._nodes[index].dom = value
        elif self.is_vector():
            self._data[index] = value

    def __getitem__(self, index: Natural) -> Membership:
        """Получить значение вектора"""
        if self.is_nodes():
            return self._nodes[index].dom
        elif self.is_vector():
            return self._data[index]

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

    def __call__(self, value: Crisp) -> Membership:
        """
        Получение значения функции принадлежности

        Args:
            value: значение базового множества

        Returns:
            степень принадлежности
        """
        if not inrange(value, self.inf, self.sup):
            raise EMemberFunc("", NFE_OUT_OF_DOMAIN)

        return self._get_value(value)

    def add_node(self, value: 'TNodeValue'):
        """
        Добавить опорную точку с упорядочиванием

        Args:
            value: добавляемая точка
        """
        if not inrange(value.x, self.inf, self.sup):
            raise EMemberFunc("", NFE_OUT_OF_DOMAIN)

        last = len(self._nodes) - 1

        i = 0
        while i <= last and gt(value.x, self._nodes[i].x):
            i += 1

        if i > last:
            self._nodes.append(value)
        elif eq(value.x, self._nodes[i].x):
            self._nodes[i].dom = value.dom
        else:
            self._nodes.insert(i, value)

        self._nodes[i].owner = self

    def append_node(self, value: 'TNodeValue'):
        """
        Добавить точку без переупорядочивания

        Args:
            value: добавляемая точка
        """
        if not inrange(value.x, self.inf, self.sup):
            raise EMemberFunc("", NFE_OUT_OF_DOMAIN)

        self._nodes.append(value)
        self._nodes[-1].owner = self

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

    def _get_index(self, value: Crisp) -> Natural:
        """
        Получение индекса элемента вектора

        Args:
            value: значение базового множества

        Returns:
            индекс в векторе
        """
        return int(
            (value - self.inf) * (len(self._data) - 1) / (self.sup - self.inf)
        )

    def _adjust_nodes(self):
        """Привести узловые точки в соответствие с границами"""
        for i in range(len(self._nodes)):
            if gt(self._nodes[i].x, self.sup):
                self._nodes[i].x = self.sup
            elif ls(self._nodes[i].x, self.inf):
                self._nodes[i].x = self.inf

    @abstractmethod
    def _get_value(self, value: Crisp) -> Membership:
        """
        Получение значения функции принадлежности (должен быть переопределен)

        Args:
            value: значение базового множества

        Returns:
            степень принадлежности
        """
        pass

    def cog(self, points: Natural) -> Crisp:
        """
        Центр тяжести (Center of Gravity)

        Args:
            points: количество точек дискретизации

        Returns:
            четкое значение
        """
        x = self.inf
        step = (self.sup - self.inf) / (points - 1)
        sum_xm = 0.0
        sum_m = 0.0

        for _ in range(points):
            val = self(x)
            sum_xm += x * val
            sum_m += val
            x += step

        if eq(sum_m, 0):
            return (self.sup - self.inf) / 2.0
        else:
            return sum_xm / sum_m

    def coa(self, points: Natural) -> Crisp:
        """
        Центр площади (Center of Area)

        Args:
            points: количество точек дискретизации

        Returns:
            четкое значение
        """
        x = self.inf
        step = (self.sup - self.inf) / (points - 1)
        total_sum = 0.0
        half_sum = 0.0

        for _ in range(points):
            total_sum += self(x)
            x += step

        total_sum /= 2.0
        x = self.inf
        i = 0

        while i < points and ls(half_sum, total_sum):
            half_sum += self(x)
            x += step
            i += 1

        if eq(half_sum, 0) or eq(total_sum, 0):
            return (self.sup - self.inf) / 2.0
        else:
            return x - step

    def lm(self, points: Natural) -> Crisp:
        """
        Левый максимум (Left Most Maximum)

        Args:
            points: количество точек дискретизации

        Returns:
            четкое значение
        """
        x = self.inf
        step = (self.sup - self.inf) / (points - 1)
        max_val = 0.0
        x_max = self.inf

        for _ in range(points):
            mi = self(x)
            if gt(mi, max_val):
                max_val = mi
                x_max = x
            x += step

        return x_max

    def rm(self, points: Natural) -> Crisp:
        """
        Правый максимум (Right Most Maximum)

        Args:
            points: количество точек дискретизации

        Returns:
            четкое значение
        """
        x = self.sup
        step = (self.sup - self.inf) / (points - 1)
        max_val = 0.0
        x_max = self.sup

        for _ in range(points):
            mi = self(x)
            if gt(mi, max_val):
                max_val = mi
                x_max = x
            x -= step

        return x_max

    def mom(self, points: Natural) -> Crisp:
        """
        Среднее максимумов (Mean of Maximums)

        Args:
            points: количество точек дискретизации

        Returns:
            четкое значение
        """
        x = self.inf
        step = (self.sup - self.inf) / (points - 1)
        max_val = 0.0
        x_start = self.inf
        x_end = self.inf

        for _ in range(points):
            mi = self(x)
            if gt(mi, max_val):
                max_val = mi
                x_start = x
                x_end = x
            if eq(mi, max_val):
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
