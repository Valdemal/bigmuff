from kernel.consts import BaseSet, Membership, Natural
from kernel.enums import MemberFuncType
from kernel.member_func.base import TMemberFunc
from kernel.base import GT, EQ, LS, GE
from kernel.node_value import TNodeValue


class TMemberFuncLinear(TMemberFunc):
    """
    Линейная функция принадлежности (треугольная, трапециевидная)
    """

    def __init__(self, *args, **kwargs):
        """
        Конструктор с поддержкой различных вариантов:
        1. TMemberFuncLinear(aInf, aSup) - пустая функция с границами
        2. TMemberFuncLinear(a, b, c, h, aInf, aSup) - треугольная
        3. TMemberFuncLinear(a, b, c, d, h, aInf, aSup) - трапециевидная
        4. TMemberFuncLinear(LeftShoulder, min, max, aInf, aSup) - краевая
        """
        # todo проблемный конструктор
        if len(args) == 2:
            # TMemberFuncLinear(aInf, aSup)
            a_inf, a_sup = args[0], args[1]
            super().__init__(a_inf, a_sup)
            self._type = MemberFuncType.mfLinear
            self.append_node(TNodeValue(a_inf, 0.0, self))
            self.append_node(TNodeValue(a_sup, 0.0, self))

        elif len(args) == 5 and isinstance(args[0], (int, float)):
            # Треугольная функция: TMemberFuncLinear(a, b, c, h, aInf, aSup)
            # Но здесь 5 аргументов, а должно быть 6? Проверим
            # На самом деле в C++ конструктор имеет 6 аргументов, но Python может принимать *args
            # Будем обрабатывать по количеству аргументов
            pass

        elif len(args) == 6 and isinstance(args[0], (int, float)):
            # Проверяем, какой это конструктор
            if len(args) == 6:
                # todo fix
                # Треугольная или трапециевидная?
                # a, b, c, d, h, aInf, aSup - будет 7 аргументов
                # Реализуем в другом месте
                raise Exception('fix later')

        elif len(args) == 4 and isinstance(args[0], bool):
            # Краевые значения: TMemberFuncLinear(LeftShoulder, min, max, aInf, aSup)
            left_shoulder, min_val, max_val, a_inf, a_sup = args[0], args[1], args[2], args[3], kwargs.get('aSup')
            super().__init__(a_inf, a_sup)
            self._type = MemberFuncType.mfLinear
            self.append_node(TNodeValue(min_val, 1.0 if left_shoulder else 0.0, self))
            self.append_node(TNodeValue(max_val, 0.0 if left_shoulder else 1.0, self))
            self.add_node(TNodeValue(a_inf if left_shoulder else a_sup, 1.0, self))
            self.add_node(TNodeValue(a_sup if left_shoulder else a_inf, 0.0, self))

    def triangular(self, a: BaseSet, b: BaseSet, c: BaseSet, h: Membership,
                   a_inf: BaseSet, a_sup: BaseSet) -> 'TMemberFuncLinear':
        """
        Создание треугольной функции принадлежности

        Args:
            a: левая точка основания
            b: вершина
            c: правая точка основания
            h: высота
            a_inf: нижняя граница
            a_sup: верхняя граница
        """
        result = TMemberFuncLinear.__new__(TMemberFuncLinear)
        super(TMemberFuncLinear, result).__init__(a_inf, a_sup)
        result._type = MemberFuncType.mfLinear
        result.append_node(TNodeValue(a_inf, 0.0, result))
        result.append_node(TNodeValue(a, 0.0, result))
        result.append_node(TNodeValue(b, h, result))
        result.append_node(TNodeValue(c, 0.0, result))
        result.append_node(TNodeValue(a_sup, 0.0, result))
        return result

    def trapezoidal(self, a: BaseSet, b: BaseSet, c: BaseSet, d: BaseSet,
                    h: Membership, a_inf: BaseSet, a_sup: BaseSet) -> 'TMemberFuncLinear':
        """
        Создание трапециевидной функции принадлежности

        Args:
            a: левая точка основания
            b: начало верхнего основания
            c: конец верхнего основания
            d: правая точка основания
            h: высота
            a_inf: нижняя граница
            a_sup: верхняя граница
        """
        result = TMemberFuncLinear(TMemberFuncLinear)
        super(TMemberFuncLinear, result).__init__(a_inf, a_sup)
        result._type = MemberFuncType.mfLinear
        result.append_node(TNodeValue(a_inf, 0.0, result))
        result.append_node(TNodeValue(a, 0.0, result))
        result.append_node(TNodeValue(b, h, result))
        result.append_node(TNodeValue(c, h, result))
        result.append_node(TNodeValue(d, 0.0, result))
        result.append_node(TNodeValue(a_sup, 0.0, result))
        return result

    def __copy__(self) -> 'TMemberFuncLinear':
        """Конструктор копирования"""
        result = TMemberFuncLinear(self._inf_base, self._sup_base)
        result._node = self._node.copy()
        result._type = self._type
        return result

    def __deepcopy__(self, memo) -> 'TMemberFuncLinear':
        """Глубокое копирование"""
        result = TMemberFuncLinear(self._inf_base, self._sup_base)
        result._node = [TNodeValue(n.x, n.dom, result) for n in self._node]
        result._type = self._type
        return result

    def is_nodes(self) -> bool:
        """Функция представлена опорными точками"""
        return True

    def is_vector(self) -> bool:
        """Функция представлена как массив"""
        return False

    def lm(self, points: Natural) -> BaseSet:
        """Левый максимум"""
        max_val = 0.0
        x_max = self._inf_base

        for n in self._node:
            if GT(n.dom, max_val):
                max_val = n.dom
                x_max = n.x

        return x_max

    def rm(self, points: Natural) -> BaseSet:
        """Правый максимум"""
        max_val = 0.0
        x_max = self._sup_base

        for n in reversed(self._node):
            if GT(n.dom, max_val):
                max_val = n.dom
                x_max = n.x

        return x_max

    def mom(self, points: Natural) -> BaseSet:
        """Среднее максимумов"""
        max_val = 0.0
        x_start = self._inf_base
        x_end = self._inf_base

        for n in self._node:
            if GT(n.dom, max_val):
                max_val = n.dom
                x_start = n.x
                x_end = n.x
            if EQ(n.dom, max_val):
                x_end = n.x

        return (x_end - x_start) / 2.0

    def _get_value(self, value: BaseSet) -> Membership:
        """Получить значение функции принадлежности (линейная интерполяция)"""
        last = len(self._node) - 1

        if LS(value, self._node[0].x) or GT(value, self._node[last].x):
            return 0.0

        i = 0
        while i <= last and GE(value, self._node[i].x):
            i += 1

        x1 = self._node[i-1].x
        x2 = self._node[i].x
        y1 = self._node[i-1].dom
        y2 = self._node[i].dom

        if EQ(value, x2):
            return y2

        return y1 + (y2 - y1) / (x2 - x1) * (value - x1)

