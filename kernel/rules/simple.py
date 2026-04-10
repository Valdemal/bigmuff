from typing import List

from kernel.consts import Natural
from kernel.enums import OperationCode
from kernel.exceptions import ESimpleRule, NFE_INVALID_CERT_VALUE, NFE_INVALID_BASE
from kernel.fuzzy_set import TFuzzySet
from kernel.base import TNeuroFuzzyBase, RESULT_FUNC, LE
from kernel.operation import TOperationBase
from kernel.variables.custom import TCustomVariable


class TSimpleRule(TNeuroFuzzyBase):
    """
    Класс определяет правило вида
    "ЕСЛИ <x1> есть <V1> ТО <y1> есть <W1> с доверием <F>"
    """

    def __init__(self, antecedent: TCustomVariable, ant_value: List[Natural],
                 consequent: TCustomVariable, cons_value: List[Natural],
                 cert: float, a_ops: TOperationBase):
        """
        Args:
            antecedent: переменная антецедента
            ant_value: выражение антецедента в обратной польской записи
            consequent: переменная консеквента
            cons_value: выражение консеквента в обратной польской записи
            cert: степень доверия к правилу
            a_ops: базовые операции
        """
        super().__init__()
        self._certainty = cert
        self._ops = a_ops
        self._ant_value = ant_value.copy()
        self._cons_value = cons_value.copy()
        self._ant_var = antecedent
        self._cons_var = consequent

        # Вычисляем значения антецедента и консеквента
        self._ant = antecedent.value(ant_value)
        self._ant.name = f"{antecedent.name} IS {self._ant.name}"

        self._cons = consequent.value(cons_value)
        self._cons.name = f"{consequent.name} IS {self._cons.name}"

        if self._certainty < 0.0 or self._certainty > 1.0:
            raise ESimpleRule("", NFE_INVALID_CERT_VALUE)

    def __del__(self):
        """Деструктор"""
        # В Python не нужно явно удалять объекты
        pass

    @property
    def ant_value(self) -> List[Natural]:
        """Получить выражение антецедента"""
        return self._ant_value

    @ant_value.setter
    def ant_value(self, value: List[Natural]):
        """Установить выражение антецедента"""
        try:
            self._ant = self._ant_var.value(value)
            self._ant.name = f"{self._ant_var.name} IS {self._ant.name}"
            self._ant_value = value.copy()
        except Exception:
            self._ant = self._ant_var.value(self._ant_value)
            self._ant.name = f"{self._ant_var.name} IS {self._ant.name}"
            raise

    @property
    def cons_value(self) -> List[Natural]:
        """Получить выражение консеквента"""
        return self._cons_value

    @cons_value.setter
    def cons_value(self, value: List[Natural]):
        """Установить выражение консеквента"""
        try:
            self._cons = self._cons_var.value(value)
            self._cons.name = f"{self._cons_var.name} IS {self._cons.name}"
            self._cons_value = value.copy()
        except Exception:
            self._cons = self._cons_var.value(self._cons_value)
            self._cons.name = f"{self._cons_var.name} IS {self._cons.name}"
            raise

    @property
    def certainty(self) -> float:
        """Получить степень доверия"""
        return self._certainty

    @certainty.setter
    def certainty(self, value: float):
        """Установить степень доверия"""
        if value < 0.0 or value > 1.0:
            raise ESimpleRule("", NFE_INVALID_CERT_VALUE)
        self._certainty = value

    def evaluate(self, in_set: TFuzzySet) -> TFuzzySet:
        """
        Вывод по правилу (композиционное правило вывода)

        Args:
            in_set: входное нечеткое множество

        Returns:
            выходное нечеткое множество
        """
        ant_fn = self._ant.func
        cons_fn = self._cons.func
        in_fn = in_set.func

        if (in_fn.inf != ant_fn.inf) or (in_fn.sup != ant_fn.sup):
            raise ESimpleRule("", NFE_INVALID_BASE)

        # Создаем выходное нечеткое множество
        out = TFuzzySet(
            "",
            RESULT_FUNC(cons_fn.inf, cons_fn.sup, self._ops.points),
            self._ops
        )
        out_fn = out.func

        step_x = (ant_fn.sup - ant_fn.inf) / (self._ops.points - 1)
        step_y = (cons_fn.sup - cons_fn.inf) / (self._ops.points - 1)

        i = 0
        y = cons_fn.inf
        while LE(y, cons_fn.sup):
            val_y = cons_fn(y)
            max_val = 0.0

            x = ant_fn.inf
            while LE(x, ant_fn.sup):
                impl_res = self._ops.impl(ant_fn(x), val_y)
                max_val = self._ops.t_conorm(
                    self._ops.t_norm(in_fn(x), impl_res),
                    max_val
                )
                x += step_x

            out_fn[i] = self._certainty * max_val
            i += 1
            y += step_y

        return out

    def prepare(self):
        """Подготовка правила к работе"""
        self._ant = self._ant_var.value(self._ant_value)
        self._ant.name = f"{self._ant_var.name} IS {self._ant.name}"

        self._cons = self._cons_var.value(self._cons_value)
        self._cons.name = f"{self._cons_var.name} IS {self._cons.name}"

    def is_input_term_used(self, index: Natural) -> bool:
        """
        Проверка, используется ли терм входной переменной

        Args:
            index: индекс терма

        Returns:
            True если используется
        """
        for i in range(len(self._ant_value) - 1):
            if (self._ant_value[i] == OperationCode.ocValue and
                    self._ant_value[i + 1] == index):
                return True
        return False

    def is_output_term_used(self, index: Natural) -> bool:
        """
        Проверка, используется ли терм выходной переменной

        Args:
            index: индекс терма

        Returns:
            True если используется
        """
        for i in range(len(self._cons_value) - 1):
            if (self._cons_value[i] == OperationCode.ocValue and
                    self._cons_value[i + 1] == index):
                return True
        return False


def create_simple_rule(antecedent: TCustomVariable, ant_value: List[Natural],
                       consequent: TCustomVariable, cons_value: List[Natural],
                       cert: float, ops: TOperationBase) -> TSimpleRule:
    """
    Создание простого правила

    Returns:
        объект простого правила
    """
    return TSimpleRule(antecedent, ant_value, consequent, cons_value, cert, ops)

