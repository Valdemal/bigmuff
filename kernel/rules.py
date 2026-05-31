from abc import ABC, abstractmethod
from typing import List

from kernel.consts import Natural
from kernel.containers.evaluatedvar import EvaluatedVar
from kernel.enums import OperationCode
from kernel.exceptions import ESimpleRule, NFE_INVALID_BASE, ECompositeRule, NFE_INVALID_EXPRESSION, NFE_INVALID_INPUTS
from kernel.fuzzy_set import TFuzzySet
from kernel.member_func import RESULT_FUNC
from kernel.mixins import OperationBased, Named, Learnable
from kernel.operation import OperationBase


class RuleBase(ABC, OperationBased):
    def __init__(self, certainty: float, ops: OperationBase):
        super().__init__(ops)
        self._certainty = certainty

    @property
    def certainty(self) -> float:
        return self._certainty

    @certainty.setter
    def certainty(self, value: float):
        self._certainty = value


class SimpleRule(RuleBase):
    def __init__(self, antecedent: EvaluatedVar, consequent: EvaluatedVar, cert: float, ops: OperationBase):
        super().__init__(cert, ops)
        self._antecedent = antecedent
        self._consequent = consequent

    @property
    def antecedent(self) -> EvaluatedVar:
        return self._antecedent

    @property
    def consequent(self) -> EvaluatedVar:
        return self._consequent

    def evaluate(self, in_set: TFuzzySet) -> TFuzzySet:
        if (in_set.func.inf != self._antecedent.fuzzy.func.inf) or (in_set.func.sup != self._antecedent.fuzzy.func.sup):
            raise ESimpleRule("", NFE_INVALID_BASE)

        # Создаем выходное нечеткое множество
        out = TFuzzySet("", RESULT_FUNC(self._consequent.fuzzy.func, self._ops.points), self._ops)
        step_x = (self._antecedent.fuzzy.func.sup - self._antecedent.fuzzy.func.inf) / (self._ops.points - 1)
        step_y = (self._consequent.fuzzy.func.sup - self._consequent.fuzzy.func.inf) / (self._ops.points - 1)

        i = 0
        y = self._consequent.fuzzy.func.inf
        while y <= self._consequent.fuzzy.func.sup:
            val_y = self._consequent.fuzzy.func(y)
            max_val = 0.0

            x = self._antecedent.fuzzy.func.inf
            while x <= self._antecedent.fuzzy.func.sup:
                impl_res = self._ops.impl(self._antecedent.fuzzy.func(x), val_y)
                max_val = self._ops.t_conorm(
                    self._ops.t_norm(in_set.func(x), impl_res),
                    max_val
                )
                x += step_x

            out.func[i] = self._certainty * max_val
            i += 1
            y += step_y

        return out


class CompositeRule(RuleBase, Named, Learnable):
    def __init__(self, name: str, consequent: EvaluatedVar, cert: float, ops: OperationBase):
        Named.__init__(self, name=name)
        RuleBase.__init__(self, cert, ops)
        Learnable.__init__(self, False)
        self._cons = consequent
        self._rules: List[SimpleRule] = []
        self._rule_expr: List[Natural] = []

        # Проверка корректности консеквента
        # consequent.var.value(consequent.value)

    @property
    def consequent(self) -> EvaluatedVar:
        return self._cons

    @property
    def rule_expr(self) -> List[Natural]:
        """Получить выражение композиции антецедента"""
        return self._rule_expr

    @rule_expr.setter
    def rule_expr(self, value: List[Natural]):
        """Установить выражение композиции антецедента"""
        # Проверка правильности выражения
        res = 0
        try:
            i = 0
            while i < len(value):
                opcode = value[i]
                i += 1

                if opcode == OperationCode.ocValue:
                    val = value[i]
                    i += 1
                    if val >= len(self._rules):
                        raise Exception("неверный индекс входной переменной правила")
                    res += 1
                elif opcode == OperationCode.ocNot:
                    pass
                elif opcode == OperationCode.ocAnd:
                    res -= 1
                elif opcode == OperationCode.ocOr:
                    res -= 1
                else:
                    raise Exception("неверный оператор (допустимы И, ИЛИ, НЕ)")

            if res != 1:
                raise Exception("неполное выражение")

            self._rule_expr = value.copy()

        except Exception as e:
            raise ECompositeRule(str(e), NFE_INVALID_EXPRESSION)

    @property
    def rules(self) -> List[SimpleRule]:
        return self._rules

    def evaluate(self, in_sets: List[TFuzzySet]) -> TFuzzySet:
        """
        Вывод по правилу

        Args:
            in_sets: список входных нечетких множеств

        Returns:
            выходное нечеткое множество
        """
        if len(in_sets) != len(self._rules):
            raise ECompositeRule("", NFE_INVALID_INPUTS)

        # Получение результатов по всем правилам
        out = [rule.evaluate(in_set) for rule, in_set in zip(self._rules, in_sets)]

        # Композиция всех выводов правил
        res: List[TFuzzySet] = []

        i = 0
        while i < len(self._rule_expr):
            opcode = self._rule_expr[i]
            i += 1

            if opcode == OperationCode.ocValue:
                val = self._rule_expr[i]
                i += 1

                if val >= len(self._rules):
                    raise Exception("неверный индекс входной переменной правила")

                op = out[val]
                res.append(TFuzzySet(
                    "",
                    RESULT_FUNC(op.func, op.ops.points),
                    op.ops
                ))

            elif opcode == OperationCode.ocNot:
                if not res:
                    raise Exception("недостаточно операндов")
                op = res.pop()
                res.append(~op)

            elif opcode == OperationCode.ocAnd:
                if len(res) < 2:
                    raise Exception("недостаточно операндов")
                op2 = res.pop()
                op1 = res.pop()
                res.append(op1 & op2)

            elif opcode == OperationCode.ocOr:
                if len(res) < 2:
                    raise Exception("недостаточно операндов")
                op2 = res.pop()
                op1 = res.pop()
                res.append(op1 | op2)

            else:
                raise Exception("неверный оператор (допустимы И, ИЛИ, НЕ)")

        if len(res) != 1:
            raise Exception("неполное выражение")

        res[0].name = self._cons.var.name
        return res[0]
