from kernel.comparison import gt, eq, ls, ge
from kernel.consts import Crisp, Membership, Natural
from kernel.enums import MemberFuncType
from kernel.member_func.base import TMemberFunc
from kernel.node_value import TNodeValue


class TMemberFuncLinearBase(TMemberFunc):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._type = MemberFuncType.mfLinear


    def is_nodes(self) -> bool:
        """Функция представлена опорными точками"""
        return True

    def is_vector(self) -> bool:
        """Функция представлена как массив"""
        return False

    def lm(self, points: Natural) -> Crisp:
        """Левый максимум"""
        max_val = 0.0
        x_max = self.inf

        for n in self._nodes:
            if gt(n.dom, max_val):
                max_val = n.dom
                x_max = n.x

        return x_max

    def rm(self, points: Natural) -> Crisp:
        """Правый максимум"""
        max_val = 0.0
        x_max = self.sup

        for n in reversed(self._nodes):
            if gt(n.dom, max_val):
                max_val = n.dom
                x_max = n.x

        return x_max

    def mom(self, points: Natural) -> Crisp:
        """Среднее максимумов"""
        max_val = 0.0
        x_start = self.inf
        x_end = self.inf

        for n in self._nodes:
            if gt(n.dom, max_val):
                max_val = n.dom
                x_start = n.x
                x_end = n.x
            if eq(n.dom, max_val):
                x_end = n.x

        return (x_end - x_start) / 2.0

    def _get_value(self, value: Crisp) -> Membership:
        """Получить значение функции принадлежности (линейная интерполяция)"""
        last = len(self._nodes) - 1

        if ls(value, self._nodes[0].x) or ge(value, self._nodes[last].x):
            return 0.0

        i = 0
        while i < last and ge(value, self._nodes[i].x):
            i += 1

        x1, x2 = self._nodes[i - 1].x, self._nodes[i].x
        y1, y2 = self._nodes[i - 1].dom, self._nodes[i].dom

        if eq(value, x2):
            return y2

        return y1 + (y2 - y1) / (x2 - x1) * (value - x1)


class TMemberFuncLinear(TMemberFuncLinearBase):
    """
    Линейная функция принадлежности (треугольная, трапециевидная)
    """

    def __init__(self, a_inf, a_sup):
        super().__init__(a_inf, a_sup)
        self.append_node(TNodeValue(a_inf, 0.0, self))
        self.append_node(TNodeValue(a_sup, 0.0, self))

class TMemberFuncTriangular(TMemberFuncLinearBase):
    def __init__(self, a: Crisp, b: Crisp, c: Crisp, h: Membership,
                 a_inf: Crisp, a_sup: Crisp):
        super().__init__(a_inf, a_sup)
        self.append_node(TNodeValue(a_inf, 0.0, self))
        self.append_node(TNodeValue(a, 0.0, self))
        self.append_node(TNodeValue(b, h, self))
        self.append_node(TNodeValue(c, 0.0, self))
        self.append_node(TNodeValue(a_sup, 0.0, self))

class TMemberFuncTrapezoidal(TMemberFuncLinearBase):
    def __init__(self, a: Crisp, b: Crisp, c: Crisp, d: Crisp, h: Membership, a_inf: Crisp, a_sup: Crisp):
        super().__init__(a_inf, a_sup)
        self.append_node(TNodeValue(a_inf, 0.0, self))
        self.append_node(TNodeValue(a, 0.0, self))
        self.append_node(TNodeValue(b, h, self))
        self.append_node(TNodeValue(c, h, self))
        self.append_node(TNodeValue(d, 0.0, self))
        self.append_node(TNodeValue(a_sup, 0.0, self))

class TMemberFuncBoundary(TMemberFuncLinearBase):
    def __init__(self, left_shoulder: bool, min_val: Crisp, max_val: Crisp, a_inf: Crisp, a_sup: Crisp):
        super().__init__(a_inf, a_sup)
        self.append_node(TNodeValue(min_val, 1.0 if left_shoulder else 0.0, self))
        self.append_node(TNodeValue(max_val, 0.0 if left_shoulder else 1.0, self))
        self.add_node(TNodeValue(a_inf if left_shoulder else a_sup, 1.0, self))
        self.add_node(TNodeValue(a_sup if left_shoulder else a_inf, 0.0, self))
