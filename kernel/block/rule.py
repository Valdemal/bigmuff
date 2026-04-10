from typing import List

from kernel.base import TNeuroFuzzyBase
from kernel.consts import Natural
from kernel.enums import VariableType
from kernel.exceptions import EFuzzyModel, NFE_INVALID_INDEX, NFE_VAR_USED, NFE_INVALID_INPUTS
from kernel.fuzzy_set import TFuzzySet
from kernel.operation import TOperationBase
from kernel.rules.composite import TCompositeRule
from kernel.variables.custom import TCustomVariable


class TRuleBlock(TNeuroFuzzyBase):
    def __init__(self, name: str, ops: TOperationBase):
        super().__init__()
        self._input: List[TCustomVariable] = []
        self._output: List[TCustomVariable] = []
        self._rule: List[TCompositeRule] = []
        self._in_rule: List[List[int]] = []
        self._out_rule: List[List[int]] = []
        self._name = name
        self._ops = ops

    @property
    def name(self) -> str:
        return self._name

    @name.setter
    def name(self, value: str):
        self._name = value

    @property
    def ops(self) -> TOperationBase:
        return self._ops

    @ops.setter
    def ops(self, value: TOperationBase):
        self._ops = value

    @property
    def input_count(self) -> Natural:
        return len(self._input)

    @property
    def output_count(self) -> Natural:
        return len(self._output)

    @property
    def rule_count(self) -> Natural:
        return len(self._rule)

    def input(self, index: Natural) -> TCustomVariable:
        if len(self._input) <= index:
            raise EFuzzyModel("", NFE_INVALID_INDEX)
        return self._input[index]

    def output(self, index: Natural) -> TCustomVariable:
        if len(self._output) <= index:
            raise EFuzzyModel("", NFE_INVALID_INDEX)
        return self._output[index]

    def rule(self, index: Natural) -> TCompositeRule:
        if len(self._rule) <= index:
            raise EFuzzyModel("", NFE_INVALID_INDEX)
        return self._rule[index]

    def add_input(self, a_input: TCustomVariable) -> Natural:
        self._input.append(a_input)
        a_input.type = VariableType.vtInput
        input_id = len(self._in_rule)
        self._in_rule.append([])
        self._in_rule[input_id] = [0] * len(self._rule)
        return len(self._input) - 1

    def add_output(self, a_output: TCustomVariable) -> Natural:
        self._output.append(a_output)
        a_output.type = VariableType.vtOutput
        for row in self._out_rule:
            row.append(0)

        return len(self._output) - 1

    def add_rule(self, name: str, antecedent: List[int], ant_value: List[List[int]], consequent: int,
                 cons_value: List[Natural], ant_comb: List[Natural], certainty: float) -> Natural:
        if len(antecedent) != len(ant_value):
            raise EFuzzyModel("Antecedent and AntValue sizes don't match", NFE_INVALID_INDEX)

        if consequent >= len(self._output):
            raise EFuzzyModel("Consequent index out of range", NFE_INVALID_INDEX)

        new_rule = TCompositeRule(name, self._output[consequent], cons_value, certainty, self._ops)
        self._rule.append(new_rule)

        rule_id = len(self._rule)
        self._out_rule.append([])  # Resize rule_out to id
        rule_id -= 1  # Convert to zero-based index
        self._out_rule[rule_id] = [0] * len(self._output)  # Initialize with zeros

        for i in range(len(self._in_rule)):
            self._in_rule[i].append(0)

        self._out_rule[rule_id][consequent] = 1

        for i in range(len(antecedent)):
            new_rule.add_in_var(self._input[antecedent[i]], ant_value[i])
            self._in_rule[antecedent[i]][rule_id] = 1

        new_rule.rule_expr = ant_comb
        return rule_id

    def del_input(self, index: Natural) -> None:
        if index >= len(self._input):
            raise EFuzzyModel("Input index out of range", NFE_INVALID_INDEX)

        if self.is_input_var_used(index):
            raise EFuzzyModel("Input variable is still in use", NFE_VAR_USED)

        self._input.pop(index)
        self._in_rule.pop(index)

    def del_output(self, index: Natural) -> None:
        if index >= len(self._output):
            raise EFuzzyModel("Output index out of range", NFE_INVALID_INDEX)

        if self.is_output_var_used(index):
            raise EFuzzyModel("Output variable is still in use", NFE_VAR_USED)

        self._output.pop(index)

        for row in self._out_rule:
            row.pop(index)

    def del_rule(self, index: Natural) -> None:
        if index >= len(self._rule):
            raise EFuzzyModel("Rule index out of range", NFE_INVALID_INDEX)

        self._rule.pop(index)

        for row in self._in_rule:
            row.pop(index)

        self._out_rule.pop(index)

    def is_input_var_used(self, index: Natural) -> bool:
        return any(rule.is_input_var_used(index) for rule in self._rule)

    def is_output_var_used(self, index: Natural) -> bool:
        return any(out_rule[index] != 0 for out_rule in self._out_rule)

    def is_input_term_used(self, invar: Natural, index: Natural) -> bool:
        if invar >= len(self._input):
            return False

        return any(rule.is_input_term_used(invar, index) for rule in self._rule)

    def is_output_term_used(self, outvar: Natural, index: Natural) -> bool:
        if outvar >= len(self._output):
            return False

        return any(rule_out[outvar] != 0 and rule.is_output_term_used(index) for rule_out, rule in
                   zip(self._out_rule, self._rule))

    def is_input_term_exists(self, invar: Natural, name: str) -> int:
        if invar >= len(self._input):
            return -1

        return self._input[invar].is_term_exists(name)

    def is_output_term_exists(self, outvar: Natural, name: str) -> int:
        if outvar >= len(self._input):
            return -1

        return self._input[outvar].is_term_exists(name)

    def evaluate(self, inp: List[TFuzzySet]) -> List[TFuzzySet]:
        """Получение выходных сигналов"""
        if len(inp) != len(self._input):
            raise EFuzzyModel("Input count mismatch", NFE_INVALID_INPUTS)

        out, inr, out_use = [], [], [False] * len(self._output)

        for r in range(len(self._rule)):
            # Подготавливаем входы правила
            inr.clear()
            for i in range(len(self._in_rule)):
                if self._in_rule[i][r]:
                    inr.append(inp[i])

            outr = self._rule[r].evaluate(inr)

            for i in range(len(self._output)):
                if self._out_rule[r][i]:
                    if out_use[i]:
                        tmp = outr.aggregate(out[i])
                        out[i] = tmp
                    else:
                        out.append(outr)
                        out_use[i] = True

        return out

    def prepare(self) -> None:
        """Подготовка к нечеткому выводу"""

        for inp in self._input:
            inp.ops = self._ops

        for out in self._output:
            out.ops = self._ops

        for rule in self._rule:
            rule.prepare()