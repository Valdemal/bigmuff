from abc import abstractmethod, ABC
from collections import defaultdict
from copy import deepcopy
from typing import List

import numpy as np
import numpy.typing as npt

from kernel.consts import Natural, Crisp, Membership
from kernel.containers.evaluatedvar import EvaluatedVar
from kernel.containers.mediator import NeuroFuzzyComponent, NeuroFuzzyMediator
from kernel.containers.variables import VarContainer
from kernel.exceptions import EFuzzyModel, NFE_INVALID_INPUTS, NFE_INVALID_INDEX
from kernel.fuzzy_set import TFuzzySet
from kernel.mixins import Named, OperationBased
from kernel.operation import OperationBase
from kernel.possibility import get_possibility_func
from kernel.rules import CompositeRule, SimpleRule
from kernel.variables.ling import LingVariable


class FunctionBlockBase(Named, NeuroFuzzyMediator, ABC):
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

    def fuzzy_evaluate_to_fuzzy(self, inp: List[TFuzzySet]) -> List[TFuzzySet]:
        if len(inp) != len(self.inputs):
            raise EFuzzyModel("", NFE_INVALID_INPUTS)

        out = self.blocks[0].evaluate(inp)

        for i in range(1, len(self.blocks)):
            res = self.blocks[i].evaluate(inp)
            for j, _ in enumerate(self.outputs):
                out[j] = out[j].aggregate(res[j])

            res.clear()

        return out

    def crisp_evaluate_to_fuzzy(self, inp: List[Crisp]) -> List[TFuzzySet]:
        if len(inp) != len(self.inputs):
            raise EFuzzyModel("", NFE_INVALID_INPUTS)

        return self.fuzzy_evaluate_to_fuzzy([inp1.fuzzificate(inp2) for inp1, inp2 in zip(self.inputs, inp)])

    def fuzzy_evaluate_to_crisp(self, inp: List[TFuzzySet]) -> List[Crisp]:
        return [out1.defuzzificate(out2) for out1, out2 in zip(self.outputs, self.fuzzy_evaluate_to_fuzzy(inp))]

    def crisp_evaluate_to_crisp(self, inp: List[Crisp]) -> List[Crisp]:
        if len(inp) != len(self.inputs):
            raise EFuzzyModel("", NFE_INVALID_INPUTS)

        out = self.fuzzy_evaluate_to_fuzzy([inp1.fuzzificate(inp2) for inp1, inp2 in zip(self.inputs, inp)])
        return [out1.defuzzificate(out2) for out1, out2 in zip(self.outputs, out)]


class RuleBlock(NeuroFuzzyComponent, Named, OperationBased):
    def __init__(self, name: str, system: FunctionBlockBase, ops: OperationBase):
        NeuroFuzzyComponent.__init__(self, mediator=system)
        Named.__init__(self, name=name)
        OperationBased.__init__(self, ops=ops)
        self._rules: List[CompositeRule] = []
        # todo использовать матрицы numpy, обязательно resize по входам выходам системы
        self._in_rule: List[List[int]] = [
            [0 for _ in range(len(self._rules))]
            for _ in range(len(system.inputs))
        ]
        self._out_rule: List[List[int]] = []

    @property
    def system(self) -> FunctionBlockBase:
        return self._mediator

    @property
    def rules(self) -> List[CompositeRule]:
        return self._rules

    # todo refactor later
    def add_rule(self, new_rule: CompositeRule, antecedent: List[int], ant_value: List[List[int]],
                 ant_comb: List[Natural], consequent_index: int) -> Natural:
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


class FunctionalBlock(FunctionBlockBase):
    def __init__(self, name: str):
        super().__init__(name)
        self._inputs, self._outputs  = VarContainer(mediator=self), VarContainer(mediator=self)
        self._blocks: List[RuleBlock] = []

    @property
    def inputs(self) -> VarContainer:
        return self._inputs

    @property
    def outputs(self) -> VarContainer:
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


PossibilityHash = defaultdict[str, defaultdict[str, Membership]]


class ClassifierFunctionalBlock(FunctionalBlock):
    def __init__(self, name: str, sampling_count=100):
        super().__init__(name)
        step = 1 / sampling_count
        self._v = np.arange(step, 1, step)

    @classmethod
    def create_from_func_block(cls, func_block: FunctionalBlock, *args, **kwargs) -> 'ClassifierFunctionalBlock':
        instance = ClassifierFunctionalBlock(func_block.name, *args, **kwargs)
        for inp in func_block.inputs:
            instance.inputs.append(deepcopy(inp))

        for out in func_block.outputs:
            instance.outputs.append(deepcopy(out))

        for rule_block in func_block.blocks:
            instance.blocks.append(deepcopy(rule_block))

        return instance

    def fuzzy_evaluate_to_crisp(self, inp: List[TFuzzySet]) -> List[Crisp]:
        if len(inp) != len(self.inputs):
            raise EFuzzyModel("", NFE_INVALID_INPUTS)

        inp_to_var: dict[str, TFuzzySet] = {inp_var.name: inp_elem for inp_var, inp_elem in zip(self.inputs, inp)}
        return self._get_out_for_block(inp_to_var, self._blocks[0])

    def crisp_evaluate_to_crisp(self, inp: List[Crisp]) -> List[Crisp]:
        if len(inp) != len(self.inputs):
            raise EFuzzyModel("", NFE_INVALID_INPUTS)

        return self.fuzzy_evaluate_to_crisp([inp1.fuzzificate(inp2) for inp1, inp2 in zip(self.inputs, inp)])

    def _get_out_for_block(self, inp_to_var: dict[str, TFuzzySet], rule_block: RuleBlock) -> np.ndarray:
        min_row = np.min(self._get_possibility_matrix(inp_to_var, rule_block), axis=1)
        out = np.zeros(len(self.outputs))

        for rule_idx, rule in enumerate(rule_block.rules):
            output_idx = self.outputs.name_index(rule.consequent.fuzzy.name.split(' IS ')[0])

            if min_row[rule_idx] > out[output_idx]:
                out[output_idx] = min_row[rule_idx]

        return out

    def _get_possibility_matrix(self, inp_to_var: dict[str, TFuzzySet], rule_block: RuleBlock) -> npt.NDArray[np.float64]:
        possibility_hash: PossibilityHash = defaultdict(lambda: defaultdict(Membership))

        return np.array([[
            self._get_possibility_for_terms(
                rule_block.ops, inp_to_var, possibility_hash, *self._get_input_and_term_from_rule(simple_rule)
            ) for simple_rule in rule.rules
        ] for rule in rule_block.rules])

    def _get_input_and_term_from_rule(self, rule: SimpleRule) -> tuple[LingVariable, TFuzzySet]:
        var_name, term_name = rule.antecedent.fuzzy.name.split(' IS ')
        inp_var: LingVariable = self.inputs[self.inputs.name_index(var_name)]
        term: TFuzzySet = next(
            term for term in inp_var.terms
            if term.name == term_name
        )
        return inp_var, term

    def _get_possibility_for_terms(
            self, operation_base: OperationBase, inp_to_var: dict[str, TFuzzySet], possibility_hash: PossibilityHash,
            input_var: LingVariable, term: TFuzzySet
    ) -> Membership:
        possibility_val = possibility_hash[input_var.name][term.name]

        if not possibility_val:
            cp = get_possibility_func(inp_to_var[input_var.name], term)
            possibility_val = possibility_hash[input_var.name][term.name] = max(
                operation_base.t_norm(cp(vi), vi) for vi in self._v
            )

        return possibility_val
