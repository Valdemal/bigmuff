from typing import List

from kernel.base import TNeuroFuzzyBase, Named
from kernel.consts import Natural
from kernel.enums import VariableType
from kernel.exceptions import EFuzzyModel, NFE_INVALID_INDEX, NFE_VAR_USED, NFE_INVALID_INPUTS
from kernel.fuzzy_set import TFuzzySet
from kernel.operation import TOperationBase
from kernel.rules.composite import TCompositeRule
from kernel.variables.custom import TCustomVariable


class TRuleBlock(Named, TNeuroFuzzyBase):
    def __init__(self, name: str, ops: TOperationBase):
        super().__init__(name=name)
        # todo уже задаются в блоке
        self._inputs: List[TCustomVariable] = []
        self._outputs: List[TCustomVariable] = []
        self._rules: List[TCompositeRule] = []
        self._in_rule: List[List[int]] = []
        self._out_rule: List[List[int]] = []
        self._ops = ops

    @property
    def ops(self) -> TOperationBase:
        return self._ops

    @ops.setter
    def ops(self, value: TOperationBase):
        self._ops = value

    @property
    def input_count(self) -> Natural:
        return len(self._inputs)

    @property
    def output_count(self) -> Natural:
        return len(self._outputs)


    @property
    def rules(self) -> List[TCompositeRule]:
        return self._rules

    def input(self, index: Natural) -> TCustomVariable:
        if len(self._inputs) <= index:
            raise EFuzzyModel("", NFE_INVALID_INDEX)
        return self._inputs[index]

    def output(self, index: Natural) -> TCustomVariable:
        if len(self._outputs) <= index:
            raise EFuzzyModel("", NFE_INVALID_INDEX)
        return self._outputs[index]

    def rule(self, index: Natural) -> TCompositeRule:
        if len(self._rules) <= index:
            raise EFuzzyModel("", NFE_INVALID_INDEX)
        return self._rules[index]

    def add_input(self, a_input: TCustomVariable) -> Natural:
        self._inputs.append(a_input)
        a_input.type = VariableType.vtInput
        input_id = len(self._in_rule)
        self._in_rule.append([])
        self._in_rule[input_id] = [0] * len(self._rules)
        return len(self._inputs) - 1

    def add_output(self, a_output: TCustomVariable) -> Natural:
        self._outputs.append(a_output)
        a_output.type = VariableType.vtOutput
        for row in self._out_rule:
            row.append(0)

        return len(self._outputs) - 1

    def add_rule(self, name: str, antecedent: List[int], ant_value: List[List[int]], consequent: int,
                 cons_value: List[Natural], ant_comb: List[Natural], certainty: float) -> Natural:
        if len(antecedent) != len(ant_value):
            raise EFuzzyModel("Antecedent and AntValue sizes don't match", NFE_INVALID_INDEX)

        if consequent >= len(self._outputs):
            raise EFuzzyModel("Consequent index out of range", NFE_INVALID_INDEX)

        new_rule = TCompositeRule(name, self._outputs[consequent], cons_value, certainty, self._ops)
        self._rules.append(new_rule)

        rule_id = len(self._rules)
        self._out_rule.append([])  # Resize rule_out to id
        rule_id -= 1  # Convert to zero-based index
        self._out_rule[rule_id] = [0] * len(self._outputs)  # Initialize with zeros

        for i in range(len(self._in_rule)):
            self._in_rule[i].append(0)

        self._out_rule[rule_id][consequent] = 1

        for i in range(len(antecedent)):
            new_rule.add_in_var(self._inputs[antecedent[i]], ant_value[i])
            self._in_rule[antecedent[i]][rule_id] = 1

        new_rule.rule_expr = ant_comb
        return rule_id

    def del_input(self, index: Natural) -> None:
        if index >= len(self._inputs):
            raise EFuzzyModel("Input index out of range", NFE_INVALID_INDEX)

        if self.is_input_var_used(index):
            raise EFuzzyModel("Input variable is still in use", NFE_VAR_USED)

        self._inputs.pop(index)
        self._in_rule.pop(index)

    def del_output(self, index: Natural) -> None:
        if index >= len(self._outputs):
            raise EFuzzyModel("Output index out of range", NFE_INVALID_INDEX)

        if self.is_output_var_used(index):
            raise EFuzzyModel("Output variable is still in use", NFE_VAR_USED)

        self._outputs.pop(index)

        for row in self._out_rule:
            row.pop(index)

    def del_rule(self, index: Natural) -> None:
        if index >= len(self._rules):
            raise EFuzzyModel("Rule index out of range", NFE_INVALID_INDEX)

        self._rules.pop(index)

        for row in self._in_rule:
            row.pop(index)

        self._out_rule.pop(index)

    def is_input_var_used(self, index: Natural) -> bool:
        return any(rule.is_input_var_used(index) for rule in self._rules)

    def is_output_var_used(self, index: Natural) -> bool:
        return any(out_rule[index] != 0 for out_rule in self._out_rule)

    def is_input_term_used(self, invar: Natural, index: Natural) -> bool:
        if invar >= len(self._inputs):
            return False

        return any(rule.is_input_term_used(invar, index) for rule in self._rules)

    def is_output_term_used(self, outvar: Natural, index: Natural) -> bool:
        if outvar >= len(self._outputs):
            return False

        return any(rule_out[outvar] != 0 and rule.is_output_term_used(index) for rule_out, rule in
                   zip(self._out_rule, self._rules))

    def is_input_term_exists(self, invar: Natural, name: str) -> int:
        if invar >= len(self._inputs):
            return -1

        return self._inputs[invar].is_term_exists(name)

    def is_output_term_exists(self, outvar: Natural, name: str) -> int:
        if outvar >= len(self._inputs):
            return -1

        return self._outputs[outvar].is_term_exists(name)

    def evaluate(self, inp: List[TFuzzySet]) -> List[TFuzzySet]:
        """Получение выходных сигналов"""
        if len(inp) != len(self._inputs):
            raise EFuzzyModel("Input count mismatch", NFE_INVALID_INPUTS)

        out, inr, out_use = [], [], [False] * len(self._outputs)

        for r in range(len(self._rules)):
            # Подготавливаем входы правила
            inr.clear()
            for i in range(len(self._in_rule)):
                if self._in_rule[i][r]:
                    inr.append(inp[i])

            outr = self._rules[r].evaluate(inr)

            for i in range(len(self._outputs)):
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

        for inp in self._inputs:
            inp.ops = self._ops

        for out in self._outputs:
            out.ops = self._ops

        for rule in self._rules:
            rule.prepare()