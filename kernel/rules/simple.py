from typing import List

from kernel.consts import Natural
from kernel.enums import OperationCode
from kernel.exceptions import ESimpleRule, NFE_INVALID_CERT_VALUE, NFE_INVALID_BASE
from kernel.fuzzy_set import TFuzzySet
from kernel.base import TNeuroFuzzyBase, LE
from kernel.member_func import RESULT_FUNC
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
        # todo отдельная структрутура для антецедента и консеквента
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

    @property
    def ant(self):
        return self._ant

    @property
    def cons(self):
        return self._cons

    @property
    def ant_value(self) -> List[Natural]:
        """Получить выражение антецедента"""
        return self._ant_value

    @ant_value.setter
    def ant_value(self, value: List[Natural]):
        """Установить выражение антецедента"""
        self._ant = self._ant_var.value(value)
        self._ant.name = f"{self._ant_var.name} IS {self._ant.name}"
        self._ant_value = value.copy()


    @property
    def cons_value(self) -> List[Natural]:
        """Получить выражение консеквента"""
        return self._cons_value

    @cons_value.setter
    def cons_value(self, value: List[Natural]):
        """Установить выражение консеквента"""
        self._cons = self._cons_var.value(value)
        self._cons.name = f"{self._cons_var.name} IS {self._cons.name}"
        self._cons_value = value.copy()


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
        if (in_set.func.inf != self._ant.func.inf) or (in_set.func.sup != self._ant.func.sup):
            raise ESimpleRule("", NFE_INVALID_BASE)

        # Создаем выходное нечеткое множество
        out = TFuzzySet("", RESULT_FUNC(self._cons.func, self._ops.points), self._ops)
        step_x = (self._ant.func.sup - self._ant.func.inf) / (self._ops.points - 1)
        step_y = (self._cons.func.sup - self._cons.func.inf) / (self._ops.points - 1)

        i = 0
        y = self._cons.func.inf
        while LE(y, self._cons.func.sup):
            val_y = self._cons.func(y)
            max_val = 0.0

            x = self._ant.func.inf
            while LE(x, self._ant.func.sup):
                impl_res = self._ops.impl(self._ant.func(x), val_y)
                max_val = self._ops.t_conorm(
                    self._ops.t_norm(in_set.func(x), impl_res),
                    max_val
                )
                x += step_x

            out.func[i] = self._certainty * max_val
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
