import sys
from typing import List

from kernel.consts import Natural
from kernel.enums import OperationCode
from kernel.exceptions import ECompositeRule, NFE_INVALID_CERT_VALUE, NFE_INVALID_EXPRESSION, ESimpleRule, \
    NFE_INVALID_INDEX, NFE_VAR_USED, NFE_INVALID_INPUTS
from kernel.fuzzy_set import TFuzzySet
from kernel.base import TNeuroFuzzyBase
from kernel.member_func import RESULT_FUNC
from kernel.operation import TOperationBase
from kernel.rules.simple import TSimpleRule
from kernel.variables.custom import TCustomVariable


class TCompositeRule(TNeuroFuzzyBase):
    """
    Реализует комплексное правило на n входов и n выходов
    используется вывод с декомпозицией
    """

    def __init__(self, a_name: str, consequent: TCustomVariable,
                 cons_value: List[Natural], cert: float, a_ops: TOperationBase):
        """
        Конструктор композитного правила

        Args:
            a_name: имя правила
            consequent: переменная консеквента
            cons_value: выражение консеквента
            cert: степень доверия
            a_ops: базовые операции
        """
        super().__init__()
        self._cons = consequent
        self._cons_val = cons_value.copy()
        self._certainty = cert
        self._ops = a_ops
        self._name_value = a_name
        self._is_learn = False
        self._rule: List[TSimpleRule] = []
        self._rule_expr: List[Natural] = []

        # Проверка корректности консеквента
        consequent.value(cons_value)

        if self._certainty < 0.0 or self._certainty > 1.0:
            raise ECompositeRule("", NFE_INVALID_CERT_VALUE)

    def __del__(self):
        """Деструктор"""
        # В Python не нужно явно удалять объекты
        pass

    @property
    def name(self) -> str:
        """Получить имя правила"""
        return self._name_value

    @name.setter
    def name(self, value: str):
        """Установить имя правила"""
        self._name_value = value

    @property
    def cons_value(self) -> List[Natural]:
        """Получить выражение консеквента"""
        return self._cons_val

    @cons_value.setter
    def cons_value(self, value: List[Natural]):
        """Установить выражение консеквента"""
        try:
            for r in self._rule:
                r.cons_value = value
            self._cons_val = value.copy()
        except Exception:
            for r in self._rule:
                r.cons_value = self._cons_val
            raise

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
                    if val >= len(self._rule):
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
    def certainty(self) -> float:
        """Получить степень доверия"""
        return self._certainty

    @certainty.setter
    def certainty(self, value: float):
        """Установить степень доверия"""
        if value < 0.0 or value > 1.0:
            raise ESimpleRule("", NFE_INVALID_CERT_VALUE)
        self._certainty = value
        for r in self._rule:
            r.certainty = value

    @property
    def learn(self) -> bool:
        """Получить признак обучения"""
        return self._is_learn

    @learn.setter
    def learn(self, value: bool):
        """Установить признак обучения"""
        self._is_learn = value

    @property
    def cons(self) -> TCustomVariable:
        """Получить переменную консеквента"""
        return self._cons

    def add_in_var(self, antecedent: TCustomVariable, ant_value: List[Natural]):
        """
        Добавить входную переменную

        Args:
            antecedent: переменная антецедента
            ant_value: выражение антецедента
        """
        r = TSimpleRule(antecedent, ant_value, self._cons,
                        self._cons_val, self._certainty, self._ops)
        self._rule.append(r)

    def del_in_var(self, index: Natural):
        """
        Удалить входную переменную

        Args:
            index: индекс удаляемой переменной
        """
        if index >= len(self._rule):
            raise ECompositeRule("", NFE_INVALID_INDEX)

        if self.is_input_var_used(index):
            raise ECompositeRule("", NFE_VAR_USED)

        del self._rule[index]

    def is_input_var_used(self, index: Natural) -> bool:
        """
        Проверка, используется ли входная переменная

        Args:
            index: индекс переменной

        Returns:
            True если используется
        """
        for i in range(len(self._rule_expr) - 1):
            if (self._rule_expr[i] == OperationCode.ocValue and
                    self._rule_expr[i + 1] == index):
                return True
        return False

    def evaluate(self, in_sets: List[TFuzzySet]) -> TFuzzySet:
        """
        Вывод по правилу

        Args:
            in_sets: список входных нечетких множеств

        Returns:
            выходное нечеткое множество
        """
        if len(in_sets) != len(self._rule):
            raise ECompositeRule("", NFE_INVALID_INPUTS)

        # Получение результатов по всем правилам
        out = [self._rule[i].evaluate(in_sets[i]) for i in range(len(self._rule))]

        # Композиция всех выводов правил
        res: List[TFuzzySet] = []

        try:
            i = 0
            while i < len(self._rule_expr):
                opcode = self._rule_expr[i]
                i += 1

                if opcode == OperationCode.ocValue:
                    val = self._rule_expr[i]
                    i += 1

                    if val >= len(self._rule):
                        raise Exception("неверный индекс входной переменной правила")

                    op = out[val]
                    res.append(TFuzzySet(
                        "",
                        RESULT_FUNC(op.func.inf, op.func.sup, op.ops.points),
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

            res[0].name = self._cons.name
            return res[0]

        except Exception as e:
            raise ECompositeRule(str(e), NFE_INVALID_EXPRESSION)

    def prepare(self):
        """Подготовка правила к работе"""
        for r in self._rule:
            r.prepare()

    def is_input_term_used(self, invar: Natural, index: Natural) -> bool:
        """
        Проверка, используется ли терм входной переменной

        Args:
            invar: индекс входной переменной
            index: индекс терма

        Returns:
            True если используется
        """
        if invar >= len(self._rule):
            return False

        val = self._rule[invar].ant_value
        for i in range(len(val) - 1):
            if val[i] == OperationCode.ocValue and val[i + 1] == index:
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
        for i in range(len(self._cons_val) - 1):
            if (self._cons_val[i] == OperationCode.ocValue and
                    self._cons_val[i + 1] == index):
                return True
        return False

    # def __str__(self) -> str:
    #     """
    #     Выгрузка правила в FCL файл
    #
    #     Returns:
    #         строка в формате FCL
    #     """
    #     # Формирование выражения антецедента
    #     res_stack: List[str] = []
    #
    #     try:
    #         i = 0
    #         while i < len(self._rule_expr):
    #             opcode = self._rule_expr[i]
    #             i += 1
    #
    #             if opcode == OperationCode.ocValue:
    #                 val = self._rule_expr[i]
    #                 i += 1
    #
    #                 if val >= len(self._rule):
    #                     raise Exception("неверный индекс входной переменной правила")
    #
    #                 res_stack.append(self._rule[val]._ant.name)
    #
    #             elif opcode == OperationCode.ocNot:
    #                 if not res_stack:
    #                     raise Exception("недостаточно операндов")
    #                 op = res_stack.pop()
    #                 res_stack.append(f"NOT {op}")
    #
    #             elif opcode == OperationCode.ocAnd:
    #                 if len(res_stack) < 2:
    #                     raise Exception("недостаточно операндов")
    #                 op2 = res_stack.pop()
    #                 op1 = res_stack.pop()
    #                 res_stack.append(f"({op1}) AND ({op2})")
    #
    #             elif opcode == OperationCode.ocOr:
    #                 if len(res_stack) < 2:
    #                     raise Exception("недостаточно операндов")
    #                 op2 = res_stack.pop()
    #                 op1 = res_stack.pop()
    #                 res_stack.append(f"({op1}) OR ({op2})")
    #
    #             else:
    #                 raise Exception("неверный оператор (допустимы И, ИЛИ, НЕ)")
    #
    #         if len(res_stack) != 1:
    #             raise Exception("неполное выражение")
    #
    #     except Exception as e:
    #         raise ECompositeRule(str(e), NFE_INVALID_EXPRESSION)
    #
    #     result = f"{RuleToken[0]} {self._name_value} : {RuleToken[1]} {res_stack[0]} "
    #     result += f"{RuleToken[2]} {self._rule[0]._cons.name} {RuleToken[3]} {self._certainty}"
    #
    #     if self._is_learn:
    #         result += f" {LearnToken}"
    #
    #     result += " ;"
    #
    #     return result

    def to_fcl(self, out=sys.stdout):
        """Выгрузка правила в FCL файл"""
        out.write(str(self) + "\n")



def create_composite_rule(name: str, consequent: TCustomVariable,
                          cons_value: List[Natural], cert: float,
                          ops: TOperationBase) -> TCompositeRule:
    """
    Создание композитного правила

    Returns:
        объект композитного правила
    """
    return TCompositeRule(name, consequent, cons_value, cert, ops)