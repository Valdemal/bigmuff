"""
Модуль для работы с нечеткими множествами (термами)
"""

import sys
from typing import Optional, Union, Any

from kernel.consts import DELTA_AMOUNT, CRISP_AMOUNT
from kernel.enums import DefuzzifyMethod, FuzzifyMethod
from kernel.exceptions import EFuzzySet, NFE_INVALID_BASE_SET
from kernel.base import TNeuroFuzzyBase, MAX, MIN, Named
from kernel.member_func import TMemberFunc, RESULT_FUNC, TMemberFuncLinear, TMemberFuncSingle, TMemberFuncSmooth
from kernel.member_func.linear import TMemberFuncTriangular, TMemberFuncTrapezoidal
from kernel.operation import TOperationBase, TMaxMin


class TFuzzySet(Named, TNeuroFuzzyBase):
    """
    Именованное нечеткое множество (терм лингвистической переменной)
    Используется для хранения термов лингвистических переменных
    """

    def __init__(self, name: str, mf: Optional[TMemberFunc],
                 a_ops: Optional[TOperationBase] = None):
        """
        Конструктор нечеткого множества

        Args:
            name: имя нечеткого множества
            mf: функция принадлежности
            a_ops: набор базовых операций
        """
        super().__init__(name=name)
        self._fn = mf
        self._ops = a_ops if a_ops is not None else TMaxMin()
        self._name = name
        self._is_learn = False

    @property
    def learn(self) -> bool:
        """Получить признак необходимости обучения"""
        return self._is_learn

    @learn.setter
    def learn(self, value: bool):
        """Установить признак необходимости обучения"""
        self._is_learn = value

    @property
    def func(self) -> Optional[TMemberFunc]:
        """Получить функцию принадлежности"""
        return self._fn

    @func.setter
    def func(self, new_mf: TMemberFunc):
        """Установить функцию принадлежности"""
        self._fn = new_mf

    @property
    def ops(self) -> TOperationBase:
        """Получить набор базовых операций"""
        return self._ops

    @ops.setter
    def ops(self, value: TOperationBase):
        """Установить набор базовых операций"""
        self._ops = value

    def __invert__(self) -> 'TFuzzySet':
        """Операция отрицания (~)"""
        # Создаем новый объект с измененным именем
        out = TFuzzySet(
            f"not {self._name}",
            RESULT_FUNC(self._fn.inf, self._fn.sup, self._ops.points),
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
            RESULT_FUNC(self._fn.inf, self._fn.sup, self._ops.points),
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
            RESULT_FUNC(self._fn.inf, self._fn.sup, self._ops.points),
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
            RESULT_FUNC(self._fn.inf, self._fn.sup, self._ops.points),
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
            RESULT_FUNC(self._fn.inf, self._fn.sup, self._ops.points),
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

        out_func = RESULT_FUNC(self._fn.inf, self._fn.sup, self._ops.points)
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

        out_func = RESULT_FUNC(self._fn.inf, self._fn.sup, self._ops.points)
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
            RESULT_FUNC(self._fn.inf, self._fn.sup, self._ops.points),
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
            RESULT_FUNC(self._fn.inf, self._fn.sup, self._ops.points),
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
        delta = (self._fn.sup - self._fn.inf) * DELTA_AMOUNT / 2.0
        crdel = (self._fn.sup - self._fn.inf) * CRISP_AMOUNT / 2.0

        if fuzzify == FuzzifyMethod.fmTriangle:
            p1 = MAX(self._fn.inf, crisp - delta)
            p2 = MIN(self._fn.sup, crisp + delta)
            result = TMemberFuncTriangular(p1, crisp, p2, 1.0, self._fn.inf, self._fn.sup)

        elif fuzzify == FuzzifyMethod.fmTrapezoid:
            p1 = MAX(self._fn.inf, crisp - delta - crdel)
            p2 = MAX(self._fn.inf, crisp - crdel)
            p3 = MIN(self._fn.sup, crisp + crdel)
            p4 = MIN(self._fn.sup, crisp + crdel + delta)
            result = TMemberFuncTrapezoidal(p1, p2, p3, p4, 1.0, self._fn.inf, self._fn.sup)

        elif fuzzify == FuzzifyMethod.fmSingleton:
            result = TMemberFuncSingle(crisp, 1.0, self._fn.inf, self._fn.sup)

        elif fuzzify == FuzzifyMethod.fmSmoothTri:
            p1 = MAX(self._fn.inf, crisp - delta)
            p2 = MIN(self._fn.sup, crisp + delta)
            result = TMemberFuncSmooth(p1, crisp, p2, 1.0, self._fn.inf, self._fn.sup)

        elif fuzzify == FuzzifyMethod.fmSmoothTrap:
            p1 = MAX(self._fn.inf, crisp - delta - crdel)
            p2 = MAX(self._fn.inf, crisp - crdel)
            p3 = MIN(self._fn.sup, crisp + crdel)
            p4 = MIN(self._fn.sup, crisp + crdel + delta)
            result = TMemberFuncSmooth(p1, p2, p3, p4, 1.0, self._fn.inf, self._fn.sup)

        else:
            raise ValueError(f"Unknown fuzzify method: {fuzzify}")

        return TFuzzySet(self._name, result, self._ops)

    def defuzzificate(self, defuzzify: DefuzzifyMethod) -> float:
        """
        Дефаззификация - преобразование нечеткого значения в четкое

        Args:
            defuzzify: метод дефаззификации

        Returns:
            четкое значение
        """
        if defuzzify == DefuzzifyMethod.dmCOG:
            return self._fn.cog(self._ops.points)
        elif defuzzify == DefuzzifyMethod.dmCOA:
            return self._fn.coa(self._ops.points)
        elif defuzzify == DefuzzifyMethod.dmLM:
            return self._fn.lm(self._ops.points)
        elif defuzzify == DefuzzifyMethod.dmRM:
            return self._fn.rm(self._ops.points)
        elif defuzzify == DefuzzifyMethod.dmMOM:
            return self._fn.mom(self._ops.points)
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
            RESULT_FUNC(self._fn.inf, self._fn.sup, self._ops.points),
            self._ops
        )

        val = self._fn.inf
        step = (self._fn.sup - self._fn.inf) / (self._ops.points - 1)

        for i in range(self._ops.points):
            out.func[i] = self._ops.rule_comp(self._fn(val), fs.func(val))
            val += step

        return out

    # def __str__(self) -> str:
    #     """Строковое представление в формате FCL"""
    #     result = f"{TermToken} {self._name_value} := "
    #     result += str(self._fn)
    #     if self._is_learn:
    #         result += f" {LearnToken} "
    #     result += ";"
    #     return result

    def to_fcl(self, out=sys.stdout):
        """Выгрузка терма в формат FCL"""
        out.write(str(self) + "\n")
