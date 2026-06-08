"""
Модуль для работы с нечеткими множествами (термами)
"""
from typing import Optional

from kernel.consts import DELTA_AMOUNT, CRISP_AMOUNT
from kernel.enums import DefuzzifyMethod, FuzzifyMethod
from kernel.exceptions import EFuzzySet, NFE_INVALID_BASE_SET
from kernel.member_func import TMemberFunc, RESULT_FUNC, TMemberFuncSingle
from kernel.member_func.linear import TMemberFuncTriangular, TMemberFuncTrapezoidal
from kernel.mixins import Named, OperationBased, Learnable
from kernel.operation import OperationBase, MaxMin


class TFuzzySet(Named, OperationBased, Learnable):
    """
    Именованное нечеткое множество (терм лингвистической переменной)
    Используется для хранения термов лингвистических переменных
    """

    def __init__(self, name: str, mf: Optional[TMemberFunc], ops: OperationBase = MaxMin()):
        """
        Конструктор нечеткого множества

        Args:
            name: имя нечеткого множества
            mf: функция принадлежности
            ops: набор базовых операций
        """
        Named.__init__(self, name)
        OperationBased.__init__(self, ops)
        Learnable.__init__(self, False)
        self._fn = mf

    @property
    def func(self) -> Optional[TMemberFunc]:
        """Получить функцию принадлежности"""
        return self._fn

    @func.setter
    def func(self, new_mf: TMemberFunc):
        """Установить функцию принадлежности"""
        self._fn = new_mf

    def __invert__(self) -> 'TFuzzySet':
        """Операция отрицания (~)"""
        # Создаем новый объект с измененным именем
        out = TFuzzySet(
            f"not {self._name}",
            RESULT_FUNC(self._fn, self._ops.points),
            self._ops
        )

        val = self._fn.inf
        step = (self._fn.sup - self._fn.inf) / (self._ops.points - 1)

        for i in range(self._ops.points):
            out.func[i] = self._ops.not_op(self._fn(val))
            val += step

        return out

    def __or__(self, other: 'TFuzzySet') -> 'TFuzzySet':
        """Операция ИЛИ (|)"""
        if (other.func.inf != self._fn.inf) or (other.func.sup != self._fn.sup):
            raise EFuzzySet("", NFE_INVALID_BASE_SET)

        out = TFuzzySet(
            f"({self._name} or {other.name})",
            RESULT_FUNC(self._fn, self._ops.points),
            self._ops
        )

        val = self._fn.inf
        step = (self._fn.sup - self._fn.inf) / (self._ops.points - 1)

        for i in range(self._ops.points):
            out.func[i] = self._ops.t_conorm(self._fn(val), other.func(val))
            val += step

        return out

    def __add__(self, other: 'TFuzzySet') -> 'TFuzzySet':
        """Композиция по ИЛИ"""

        if (other.func.inf != self._fn.inf) or (other.func.sup != self._fn.sup):
            raise EFuzzySet("", NFE_INVALID_BASE_SET)

        out = TFuzzySet(
            f"({self._name} l_or {other.name})",
            RESULT_FUNC(self._fn, self._ops.points),
            self._ops
        )

        val = self._fn.inf
        step = (self._fn.sup - self._fn.inf) / (self._ops.points - 1)

        for i in range(self._ops.points):
            out.func[i] = self._ops.comp_or(self._fn(val), other.func(val))
            val += step

        return out

    def __and__(self, other: 'TFuzzySet') -> 'TFuzzySet':
        """Операция И (&)"""

        if (other.func.inf != self._fn.inf) or (other.func.sup != self._fn.sup):
            raise EFuzzySet("", NFE_INVALID_BASE_SET)

        out = TFuzzySet(
            f"({self._name} and {other.name})",
            RESULT_FUNC(self._fn, self._ops.points),
            self._ops
        )

        val = self._fn.inf
        step = (self._fn.sup - self._fn.inf) / (self._ops.points - 1)

        for i in range(self._ops.points):
            out.func[i] = self._ops.t_norm(self._fn(val), other.func(val))
            val += step

        return out

    def __mul__(self, other: 'TFuzzySet') -> 'TFuzzySet':
        """Композиция по И"""

        if (other.func.inf != self._fn.inf) or (other.func.sup != self._fn.sup):
            raise EFuzzySet("", NFE_INVALID_BASE_SET)

        out = TFuzzySet(
            f"({self._name} l_and {other.name})",
            RESULT_FUNC(self._fn, self._ops.points),
            self._ops
        )

        val = self._fn.inf
        step = (self._fn.sup - self._fn.inf) / (self._ops.points - 1)

        for i in range(self._ops.points):
            out.func[i] = self._ops.comp_and(self._fn(val), other.func(val))
            val += step

        return out

    def __ior__(self, other: 'TFuzzySet') -> 'TFuzzySet':
        """Операция ИЛИ с присваиванием (|=)"""

        if (other.func.inf != self._fn.inf) or (other.func.sup != self._fn.sup):
            raise EFuzzySet("", NFE_INVALID_BASE_SET)

        out_func = RESULT_FUNC(self._fn, self._ops.points)
        self._name = f"({self._name} or {other.name})"

        val = self._fn.inf
        step = (self._fn.sup - self._fn.inf) / (self._ops.points - 1)

        for i in range(self._ops.points):
            out_func[i] = self._ops.t_conorm(self._fn(val), other.func(val))
            val += step

        self._fn = out_func
        return self

    def __iand__(self, other: 'TFuzzySet') -> 'TFuzzySet':
        """Операция И с присваиванием (&=)"""

        if (other.func.inf != self._fn.inf) or (other.func.sup != self._fn.sup):
            raise EFuzzySet("", NFE_INVALID_BASE_SET)

        out_func = RESULT_FUNC(self._fn, self._ops.points)
        self._name = f"({self._name} and {other.name})"

        val = self._fn.inf
        step = (self._fn.sup - self._fn.inf) / (self._ops.points - 1)

        for i in range(self._ops.points):
            out_func[i] = self._ops.t_norm(self._fn(val), other.func(val))
            val += step

        self._fn = out_func
        return self

    def con(self) -> 'TFuzzySet':
        """
        Концентрация (операция CON)
        Возводит степени принадлежности в квадрат
        """
        out = TFuzzySet(
            f"con {self._name}",
            RESULT_FUNC(self._fn, self._ops.points),
            self._ops
        )

        val = self._fn.inf
        step = (self._fn.sup - self._fn.inf) / (self._ops.points - 1)

        for i in range(self._ops.points):
            out.func[i] = self._ops.pow(self._fn(val), 2.0)
            val += step

        return out

    def dil(self) -> 'TFuzzySet':
        """
        Размытие (операция DIL)
        Возводит степени принадлежности в степень 0.5
        """
        out = TFuzzySet(
            f"dil {self._name}",
            RESULT_FUNC(self._fn, self._ops.points),
            self._ops
        )

        val = self._fn.inf
        step = (self._fn.sup - self._fn.inf) / (self._ops.points - 1)

        for i in range(self._ops.points):
            out.func[i] = self._ops.pow(self._fn(val), 0.5)
            val += step

        return out

    def fuzzificate(self, crisp: float, fuzzify: FuzzifyMethod) -> 'TFuzzySet':
        """
        Фаззификация - преобразование четкого значения в нечеткое

        Args:
            crisp: четкое значение
            fuzzify: метод фаззификации

        Returns:
            новое нечеткое множество
        """
        # todo выделить метод фаззификации в отдельный класс
        delta = (self.func.sup - self.func.inf) * DELTA_AMOUNT / 2.0
        crdel = (self.func.sup - self.func.inf) * CRISP_AMOUNT / 2.0

        if fuzzify == FuzzifyMethod.fmTriangle:
            p1 = max(self.func.inf, crisp - delta)
            p2 = min(self.func.sup, crisp + delta)
            result = TMemberFuncTriangular(p1, crisp, p2, 1.0, self.func.inf, self.func.sup)

        elif fuzzify == FuzzifyMethod.fmTrapezoid:
            p1 = max(self.func.inf, crisp - delta - crdel)
            p2 = max(self.func.inf, crisp - crdel)
            p3 = min(self.func.sup, crisp + crdel)
            p4 = min(self.func.sup, crisp + crdel + delta)
            result = TMemberFuncTrapezoidal(p1, p2, p3, p4, 1.0, self.func.inf, self.func.sup)

        elif fuzzify == FuzzifyMethod.fmSingleton:
            result = TMemberFuncSingle(crisp, 1.0, self.func.inf, self.func.sup)

        # elif fuzzify == FuzzifyMethod.fmSmoothTri:
        #     p1 = max(self._fn.inf, crisp - delta)
        #     p2 = min(self._fn.sup, crisp + delta)
        #     result = TMemberFuncSmoothBase(p1, crisp, p2, 1.0, self._fn.inf, self._fn.sup)
        #
        # elif fuzzify == FuzzifyMethod.fmSmoothTrap:
        #     p1 = max(self._fn.inf, crisp - delta - crdel)
        #     p2 = max(self._fn.inf, crisp - crdel)
        #     p3 = min(self._fn.sup, crisp + crdel)
        #     p4 = min(self._fn.sup, crisp + crdel + delta)
        #     result = TMemberFuncSmoothBase(p1, p2, p3, p4, 1.0, self._fn.inf, self._fn.sup)

        else:
            raise ValueError(f"Unknown fuzzify method: {fuzzify}")

        return TFuzzySet(self.name, result, self.ops)

    def defuzzificate(self, defuzzify: DefuzzifyMethod) -> float:
        """
        Дефаззификация - преобразование нечеткого значения в четкое

        Args:
            defuzzify: метод дефаззификации

        Returns:
            четкое значение
        """
        if defuzzify == DefuzzifyMethod.dmCOG:
            return self._fn.cog(self.ops.points)
        elif defuzzify == DefuzzifyMethod.dmCOA:
            return self._fn.coa(self.ops.points)
        elif defuzzify == DefuzzifyMethod.dmLM:
            return self._fn.lm(self.ops.points)
        elif defuzzify == DefuzzifyMethod.dmRM:
            return self._fn.rm(self.ops.points)
        elif defuzzify == DefuzzifyMethod.dmMOM:
            return self._fn.mom(self.ops.points)
        else:
            raise ValueError(f"Unknown defuzzify method: {defuzzify}")

    def aggregate(self, fs: 'TFuzzySet') -> 'TFuzzySet':
        """
        Агрегация результатов по различным правилам

        Args:
            fs: другое нечеткое множество для агрегации

        Returns:
            агрегированное нечеткое множество
        """
        if (fs.func.inf != self._fn.inf) or (fs.func.sup != self._fn.sup):
            raise EFuzzySet("", NFE_INVALID_BASE_SET)

        out = TFuzzySet(
            f"({self._name} aggr {fs.name})",
            RESULT_FUNC(self._fn, self._ops.points),
            self._ops
        )

        val = self._fn.inf
        step = (self._fn.sup - self._fn.inf) / (self._ops.points - 1)

        for i in range(self._ops.points):
            out.func[i] = self._ops.rule_comp(self._fn(val), fs.func(val))
            val += step

        return out
