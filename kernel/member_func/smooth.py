from kernel.comparison import gt, eq, ls
from kernel.consts import Crisp, Membership, Natural
from kernel.enums import MemberFuncType
from kernel.member_func.base import TMemberFunc
from kernel.node_value import TNodeValue


class TMemberFuncSmooth(TMemberFunc):
    """
    Гладкая функция принадлежности (колоколообразная, сглаженная трапеция)
    """

    def __init__(self, *args, **kwargs):
        """
        Конструктор с поддержкой различных вариантов
        """
        # todo проблемный конструктор
        if len(args) == 2:
            a_inf, a_sup = args[0], args[1]
            super().__init__(a_inf, a_sup)
            self._type = MemberFuncType.mfSmooth
            self.append_node(TNodeValue(a_inf, 0.0, self))
            self.append_node(TNodeValue(a_sup, 0.0, self))

    def bell(self, a: Crisp, b: Crisp, c: Crisp, h: Membership,
             a_inf: Crisp, a_sup: Crisp) -> 'TMemberFuncSmooth':
        """Колоколообразная функция"""
        result = TMemberFuncSmooth.__new__(TMemberFuncSmooth)
        super(TMemberFuncSmooth, result).__init__(a_inf, a_sup)
        result._type = MemberFuncType.mfSmooth
        result.append_node(TNodeValue(a_inf, 0.0, result))
        result.append_node(TNodeValue(a, 0.0, result))
        result.append_node(TNodeValue(b, h, result))
        result.append_node(TNodeValue(c, 0.0, result))
        result.append_node(TNodeValue(a_sup, 0.0, result))
        return result

    def gaussian(self, mean: Crisp, deriv: Crisp, h: Membership,
                 a_inf: Crisp, a_sup: Crisp) -> 'TMemberFuncSmooth':
        """Гауссоподобная функция"""
        result = TMemberFuncSmooth.__new__(TMemberFuncSmooth)
        super(TMemberFuncSmooth, result).__init__(a_inf, a_sup)
        result._type = MemberFuncType.mfSmooth
        result.append_node(TNodeValue(a_inf, 0.0, result))
        result.append_node(TNodeValue(mean + deriv / 2.0, 0.0, result))
        result.append_node(TNodeValue(mean, h, result))
        result.append_node(TNodeValue(mean - deriv / 2.0, 0.0, result))
        result.append_node(TNodeValue(a_sup, 0.0, result))
        return result

    def smooth_trapezoid(self, a: Crisp, b: Crisp, c: Crisp, d: Crisp,
                         h: Membership, a_inf: Crisp, a_sup: Crisp) -> 'TMemberFuncSmooth':
        """Сглаженная трапеция"""
        result = TMemberFuncSmooth.__new__(TMemberFuncSmooth)
        super(TMemberFuncSmooth, result).__init__(a_inf, a_sup)
        result._type = MemberFuncType.mfSmooth
        result.append_node(TNodeValue(a_inf, 0.0, result))
        result.append_node(TNodeValue(a, 0.0, result))
        result.append_node(TNodeValue(b, h, result))
        result.append_node(TNodeValue(c, h, result))
        result.append_node(TNodeValue(d, 0.0, result))
        result.append_node(TNodeValue(a_sup, 0.0, result))
        return result

    def shoulder(self, left_shoulder: bool, min_val: Crisp, max_val: Crisp,
                 a_inf: Crisp, a_sup: Crisp) -> 'TMemberFuncSmooth':
        """Сглаженные краевые значения"""
        result = TMemberFuncSmooth.__new__(TMemberFuncSmooth)
        super(TMemberFuncSmooth, result).__init__(a_inf, a_sup)
        result._type = MemberFuncType.mfSmooth
        result.append_node(TNodeValue(min_val, 1.0 if left_shoulder else 0.0, result))
        result.append_node(TNodeValue(max_val, 0.0 if left_shoulder else 1.0, result))
        result.add_node(TNodeValue(a_inf if left_shoulder else a_sup, 1.0, result))
        result.add_node(TNodeValue(a_sup if left_shoulder else a_inf, 0.0, result))
        return result

    def is_nodes(self) -> bool:
        """Функция представлена опорными точками"""
        return True

    def is_vector(self) -> bool:
        """Функция представлена как массив"""
        return False

    def lm(self, points: Natural) -> Crisp:
        """Левый максимум"""
        max_val = 0.0
        x_max = self._inf_base

        for n in self._nodes:
            if gt(n.dom, max_val):
                max_val = n.dom
                x_max = n.x

        return x_max

    def rm(self, points: Natural) -> Crisp:
        """Правый максимум"""
        max_val = 0.0
        x_max = self._sup_base

        for n in reversed(self._nodes):
            if gt(n.dom, max_val):
                max_val = n.dom
                x_max = n.x

        return x_max

    def mom(self, points: Natural) -> Crisp:
        """Среднее максимумов"""
        max_val = 0.0
        x_start = self._inf_base
        x_end = self._inf_base

        for n in self._nodes:
            if gt(n.dom, max_val):
                max_val = n.dom
                x_start = n.x
                x_end = n.x

            if eq(n.dom, max_val):
                x_end = n.x

        return (x_end - x_start) / 2.0

    def _get_value(self, value: Crisp) -> Membership:
        """
        Получить значение функции принадлежности (гладкая интерполяция)
        Используется S-образная интерполяция
        """
        last = len(self._nodes) - 1

        if ls(value, self._nodes[0].x) or gt(value, self._nodes[last].x):
            return 0.0

        i = 0
        while i <= last and gt(value, self._nodes[i].x):
            i += 1

        x1 = self._nodes[i - 1].x
        x2 = self._nodes[i].x
        y1 = self._nodes[i - 1].dom
        y2 = self._nodes[i].dom

        if eq(value, x2):
            return y2

        # S-образная интерполяция
        mid = (x1 + x2) / 2.0
        t = (value - x1) / (x2 - x1)

        if ls(value, mid):
            # Первая половина: квадратичная интерполяция от y1 к y2
            return y1 + 2 * (y2 - y1) * t * t
        else:
            # Вторая половина: квадратичная интерполяция с затуханием
            return y1 + (y2 - y1) * (1 - 2 * (1 - t) * (1 - t))
