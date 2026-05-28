from typing import List

from kernel.base import TNeuroFuzzyBase, Named
from kernel.block.rule import TRuleBlock
from kernel.consts import Natural, BaseSet
from kernel.exceptions import EFuzzyModel, NFE_INVALID_INDEX, NFE_INVALID_INPUTS
from kernel.fuzzy_set import TFuzzySet
from kernel.variables.custom import TCustomVariable


class TFunctionBlock(Named, TNeuroFuzzyBase):
    def __init__(self, name: str, *args, **kwargs):
        super().__init__(name=name)
        self._inputs: List[TCustomVariable] = []
        self._outputs: List[TCustomVariable] = []
        self._blocks: List[TRuleBlock] = []

    @property
    def inputs(self) -> List[TCustomVariable]:
        return self._inputs

    def add_input(self, inp: TCustomVariable) -> Natural:
        self._inputs.append(inp)

        for block in self._blocks:
            block.add_input(inp)

        return len(self._inputs) - 1

    def del_input(self, index: Natural):
        if len(self._inputs) <= index:
            raise EFuzzyModel("Input index is out of range", NFE_INVALID_INDEX)

        if self.is_input_var_used(index):
            raise EFuzzyModel("Input is used", NFE_INVALID_INDEX)

        self._inputs.pop(index)
        for block in self._blocks:
            block.del_input(index)

    @property
    def outputs(self) -> List[TCustomVariable]:
        return self._outputs

    def add_output(self, out: TCustomVariable) -> Natural:
        self._outputs.append(out)
        for block in self._blocks:
            block.add_output(out)
        return len(self._outputs) - 1

    def del_output(self, index: Natural):
        if len(self._outputs) <= index:
            raise EFuzzyModel("Output index is out of range", NFE_INVALID_INDEX)

        if self.is_output_var_used(index):
            raise EFuzzyModel("Outpur is used", NFE_INVALID_INDEX)

        self._outputs.pop(index)
        for block in self._blocks:
            block.del_output(index)

    @property
    def blocks(self) -> List[TRuleBlock]:
        return self._blocks

    def add_block(self, new_block: TRuleBlock) -> int:
        self._blocks.append(new_block)

        for inp in self._inputs:
            new_block.add_input(inp)

        for out in self._outputs:
            new_block.add_output(out)

        return len(self._blocks) - 1

    def del_block(self, index: Natural):
        if len(self._blocks) <= index:
            raise EFuzzyModel("Block index is out of range", NFE_INVALID_INDEX)

        self._blocks.pop(index)

    def is_input_exists(self, name: str) -> int:
        for i in range(len(self._inputs)):
            if self._inputs[i].name == name:
                return i

        return -1

    def is_output_exists(self, name: str) -> int:
        for i in range(len(self._outputs)):
            if self._outputs[i].name == name:
                return i

        return -1

    def is_rule_block_exists(self, name: str) -> int:
        for i in range(len(self._blocks)):
            if self._blocks[i].name == name:
                return i

        return -1

    def is_input_value_exists(self, name: str, a_input: Natural) -> bool:
        if len(self._inputs) <= a_input:
            raise EFuzzyModel("Input index is out of range", NFE_INVALID_INDEX)

        return self._inputs[a_input].is_value_exists(name)

    def is_output_value_exists(self, name: str, a_output: Natural) -> bool:
        if len(self._outputs) <= a_output:
            raise EFuzzyModel("Output index is out of range", NFE_INVALID_INDEX)

        return self._outputs[a_output].is_value_exists(name)

    def is_input_var_used(self, index: Natural) -> bool:
        return any(block.is_input_var_used(index) for block in self._blocks)

    def is_output_var_used(self, index: Natural) -> bool:
        return any(block.is_output_var_used(index) for block in self._blocks)

    def is_input_term_used(self, invar: Natural, index: Natural) -> bool:
        if invar >= len(self._inputs):
            return False

        return any(block.is_input_term_used(invar, index) for block in self._blocks)

    def is_output_term_used(self, outvar: Natural, index: Natural) -> bool:
        if outvar >= len(self._outputs):
            return False

        return any(block.is_output_term_used(outvar, index) for block in self._blocks)

    def f_evaluate_f(self, inp: List[TFuzzySet]) -> List[TFuzzySet]:
        if len(inp) != len(self._inputs):
            raise EFuzzyModel("", NFE_INVALID_INPUTS)

        out = self._blocks[0].evaluate(inp)

        for i in range(1, len(self._blocks)):
            res = self._blocks[i].evaluate(inp)
            for j in range(len(self._outputs)):
                tmp = out[j].aggregate(res[j])
                out[j] = tmp

            res.clear()

        return out

    def f_evaluate_c(self, inp: List[BaseSet]) -> List[TFuzzySet]:
        if len(inp) != len(self._inputs):
            raise EFuzzyModel("", NFE_INVALID_INPUTS)

        return self.f_evaluate_f([inp1.fuzzificate(inp2) for inp1, inp2 in zip(self._inputs, inp)])

    def c_evaluate_f(self, inp: List[TFuzzySet]) -> List[BaseSet]:
        return [out1.defuzzificate(out2) for out1, out2 in zip(self._outputs, self.f_evaluate_f(inp))]

    def c_evaluate_c(self, inp: List[BaseSet]) -> List[BaseSet]:
        if len(inp) != len(self._inputs):
            raise EFuzzyModel("", NFE_INVALID_INPUTS)

        out = self.f_evaluate_f([inp1.fuzzificate(inp2) for inp1, inp2 in zip(self._inputs, inp)])
        return [out1.defuzzificate(out2) for out1, out2 in zip(self._outputs, out)]

    def prepare(self):
        for block in self._blocks:
            block.prepare()
