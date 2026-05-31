from abc import abstractmethod
from typing import List

from kernel.consts import Natural, Crisp
from kernel.containers.mediator import NeuroFuzzyComponent, NeuroFuzzyMediator
from kernel.containers.evaluatedvar import EvaluatedVar
from kernel.containers.variables import VarContainer
from kernel.exceptions import EFuzzyModel, NFE_INVALID_INPUTS, NFE_INVALID_INDEX
from kernel.fuzzy_set import TFuzzySet
from kernel.mixins import Named, OperationBased
from kernel.operation import OperationBase
from kernel.rules import CompositeRule, SimpleRule


class NeuroFuzzyBase(Named, NeuroFuzzyMediator):
    @property
    @abstractmethod
    def inputs(self) -> VarContainer:
        pass

    @property
    @abstractmethod
    def outputs(self) -> VarContainer:
        pass

    @property
    @abstractmethod
    def blocks(self) -> List['RuleBlock']:
        pass


    def f_evaluate_f(self, inp: List[TFuzzySet]) -> List[TFuzzySet]:
        if len(inp) != len(self.inputs):
            raise EFuzzyModel("", NFE_INVALID_INPUTS)

        out = self.blocks[0].evaluate(inp)

        for i in range(1, len(self.blocks)):
            res = self.blocks[i].evaluate(inp)
            for j, _ in enumerate(self.outputs):
                out[j] = out[j].aggregate(res[j])

            res.clear()

        return out

    def f_evaluate_c(self, inp: List[Crisp]) -> List[TFuzzySet]:
        if len(inp) != len(self.inputs):
            raise EFuzzyModel("", NFE_INVALID_INPUTS)

        return self.f_evaluate_f([inp1.fuzzificate(inp2) for inp1, inp2 in zip(self.inputs, inp)])

    def c_evaluate_f(self, inp: List[TFuzzySet]) -> List[Crisp]:
        return [out1.defuzzificate(out2) for out1, out2 in zip(self.outputs, self.f_evaluate_f(inp))]

    def c_evaluate_c(self, inp: List[Crisp]) -> List[Crisp]:
        if len(inp) != len(self.inputs):
            raise EFuzzyModel("", NFE_INVALID_INPUTS)

        out = self.f_evaluate_f([inp1.fuzzificate(inp2) for inp1, inp2 in zip(self.inputs, inp)])
        return [out1.defuzzificate(out2) for out1, out2 in zip(self.outputs, out)]


class RuleBlock(NeuroFuzzyComponent, Named, OperationBased):
    def __init__(self, name: str, system: NeuroFuzzyBase, ops: OperationBase):
        NeuroFuzzyComponent.__init__(self, mediator=system)
        Named.__init__(self, name=name)
        OperationBased.__init__(self, ops=ops)
        self._rules: List[CompositeRule] = []
        # todo использовать матрицы numpy, обязательно resize по входам выходам системы
        self._in_rule: List[List[int]] = [
            [0 for _ in  range(len(self._rules))]
            for _ in range(len(system.inputs))
        ]
        self._out_rule: List[List[int]] = []

    @property
    def system(self) -> NeuroFuzzyBase:
        return self._mediator

    @property
    def rules(self) -> List[CompositeRule]:
        return self._rules

    # todo refactor later
    def add_rule(self, new_rule: CompositeRule, antecedent: List[int], ant_value: List[List[int]], ant_comb: List[Natural], consequent_index: int) -> Natural:
        if len(antecedent) != len(ant_value):
            raise EFuzzyModel("Antecedent and AntValue sizes don't match", NFE_INVALID_INDEX)

        self._rules.append(new_rule)

        rule_id = len(self._rules)
        self._out_rule.append([])  # Resize rule_out to id
        rule_id -= 1  # Convert to zero-based index
        self._out_rule[rule_id] = [0] * len(self.system.outputs)  # Initialize with zeros

        for i in range(len(self._in_rule)):
            self._in_rule[i].append(0)

        self._out_rule[rule_id][consequent_index] = 1

        for i in range(len(antecedent)):
            new_rule.rules.append(SimpleRule(
                EvaluatedVar(self.system.inputs[antecedent[i]], ant_value[i]),
                new_rule.consequent, new_rule.certainty, new_rule.ops
            ))
            self._in_rule[antecedent[i]][rule_id] = 1

        new_rule.rule_expr = ant_comb
        return rule_id


    def evaluate(self, inp: List[TFuzzySet]) -> List[TFuzzySet]:
        if len(inp) != len(self.system.inputs):
            raise EFuzzyModel("Input count mismatch", NFE_INVALID_INPUTS)

        out, inr, out_use = [], [], [False for _ in enumerate(self.system.outputs)]

        for r in range(len(self._rules)):
            # Подготавливаем входы правила
            inr.clear()
            for i in range(len(self._in_rule)):
                if self._in_rule[i][r]:
                    inr.append(inp[i])

            outr = self._rules[r].evaluate(inr)

            for i, _ in enumerate(self.system.outputs):
                if self._out_rule[r][i]:
                    if out_use[i]:
                        tmp = outr.aggregate(out[i])
                        out[i] = tmp
                    else:
                        out.append(outr)
                        out_use[i] = True

        return out

    def on_add_input(self):
        self._in_rule.append([0] * len(self._rules))

    def on_add_output(self):
        for row in self._out_rule:
            row.append(0)

    def on_pop_input(self, index: int):
        pass

    def on_pop_output(self, index: int):
        pass


class FunctionalBlock(NeuroFuzzyBase):
    def __init__(self, name: str):
        super().__init__(name)
        self._inputs = VarContainer(mediator=self)
        self._outputs = VarContainer(mediator=self)
        self._blocks: List[RuleBlock] = []

    @property
    def inputs(self)-> VarContainer:
        return self._inputs

    @property
    def outputs(self)-> VarContainer:
        return self._outputs

    @property
    def blocks(self) -> List[RuleBlock]:
        return self._blocks

    def notify(self, sender: NeuroFuzzyComponent, event: str, index=None):
        if sender == self._inputs:
            if event == 'append':
                for block in self._blocks:
                    block.on_add_input()
            elif event == 'pop':
                for block in self._blocks:
                    block.on_pop_input(index)

        elif sender == self._outputs:
            if event == 'append':
                for block in self._blocks:
                    block.on_add_output()
            elif event == 'pop':
                for block in self._blocks:
                    block.on_pop_output(index)