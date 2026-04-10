from typing import List

from kernel.base import TNeuroFuzzyBase
from kernel.block.rule import TRuleBlock
from kernel.consts import Natural, BaseSet
from kernel.exceptions import EFuzzyModel, NFE_INVALID_INDEX, NFE_INVALID_INPUTS
from kernel.fuzzy_set import TFuzzySet
from kernel.operation import TOperationBase
from kernel.variables.custom import TCustomVariable


class TFunctionBlock(TNeuroFuzzyBase):
    def __init__(self, name: str):
        super().__init__()
        self._name = name
        self._input: List[TCustomVariable] = []
        self._output: List[TCustomVariable] = []
        self._blocks: List[TRuleBlock] = []

    @property
    def name(self) -> str:
        return self._name

    @name.setter
    def name(self, value: str):
        self._name = value

    @property
    def input_count(self) -> int:
        return len(self._input)

    def input(self, index: Natural) -> TCustomVariable:
        if len(self._input) <= index:
            raise EFuzzyModel("", NFE_INVALID_INDEX)
        return self._input[index]

    def add_input(self, inp: TCustomVariable) -> Natural:
        self._input.append(inp)

        for block in self._blocks:
            block.add_input(inp)

        return len(self._input) - 1

    def del_input(self, index: Natural):
        if len(self._input) <= index:
            raise EFuzzyModel("Input index is out of range", NFE_INVALID_INDEX)

        if self.is_input_var_used(index):
            raise EFuzzyModel("Input is used", NFE_INVALID_INDEX)

        self._input.pop(index)
        for block in self._blocks:
            block.del_input(index)

    @property
    def output_count(self) -> int:
        return len(self._output)

    def output(self, index: Natural) -> TCustomVariable:
        if len(self._output) <= index:
            raise EFuzzyModel("", NFE_INVALID_INDEX)
        return self._output[index]

    def add_output(self, out: TCustomVariable) -> Natural:
        self._output.append(out)
        for block in self._blocks:
            block.add_output(out)
        return len(self._output) - 1

    def del_output(self, index: Natural):
        if len(self._output) <= index:
            raise EFuzzyModel("Output index is out of range", NFE_INVALID_INDEX)

        if self.is_output_var_used(index):
            raise EFuzzyModel("Outpur is used", NFE_INVALID_INDEX)

        self._output.pop(index)
        for block in self._blocks:
            block.del_output(index)

    @property
    def block_count(self) -> Natural:
        return len(self._blocks)

    def block(self, index: Natural) -> TRuleBlock:
        if len(self._blocks) <= index:
            raise EFuzzyModel("", NFE_INVALID_INDEX)

        return self._blocks[index]

    def add_block(self, name: str, ops: TOperationBase):
        new_block = TRuleBlock(name, ops)
        self._blocks.append(new_block)

        for inp in self._input:
            new_block.add_input(inp)

        for out in self._output:
            new_block.add_output(out)

        return len(self._blocks) - 1

    def del_block(self, index: Natural):
        if len(self._blocks) <= index:
            raise EFuzzyModel("Block index is out of range", NFE_INVALID_INDEX)

        self._blocks.pop(index)

    def is_input_exists(self, name: str) -> int:
        for i in range(len(self._input)):
            if self._input[i].name == name:
                return i

        return -1

    def is_output_exists(self, name: str) -> int:
        for i in range(len(self._output)):
            if self._output[i].name == name:
                return i

        return -1

    def is_rule_block_exists(self, name: str) -> int:
        for i in range(len(self._blocks)):
            if self._blocks[i].name == name:
                return i

        return -1

    def is_input_value_exists(self, name: str, a_input: Natural) -> bool:
        if len(self._input) <= a_input:
            raise EFuzzyModel("Input index is out of range", NFE_INVALID_INDEX)

        return self._input[a_input].is_value_exists(name)

    def is_output_value_exists(self, name: str, a_output: Natural) -> bool:
        if len(self._output) <= a_output:
            raise EFuzzyModel("Output index is out of range", NFE_INVALID_INDEX)

        return self._output[a_output].is_value_exists(name)

    def is_input_var_used(self, index: Natural) -> bool:
        return any(block.is_input_var_used(index) for block in self._blocks)

    def is_output_var_used(self, index: Natural) -> bool:
        return any(block.is_output_var_used(index) for block in self._blocks)

    def is_input_term_used(self, invar: Natural, index: Natural) -> bool:
        if invar >= len(self._input):
            return False

        return any(block.is_input_term_used(invar, index) for block in self._blocks)

    def is_output_term_used(self, outvar: Natural, index: Natural) -> bool:
        if outvar >= len(self._output):
            return False

        return any(block.is_output_term_used(outvar, index) for block in self._blocks)

    def f_evaluate_f(self, inp: List[TFuzzySet]) -> List[TFuzzySet]:
        if len(inp) != len(self._input):
            raise EFuzzyModel("", NFE_INVALID_INPUTS)

        out = self._blocks[0].evaluate(inp)

        for i in range(1, len(self._blocks)):
            res = self._blocks[i].evaluate(inp)
            for j in range(len(self._output)):
                tmp = out[j].aggregate(res[j])
                out[j] = tmp

            res.clear()

        return out

    def f_evaluate_c(self, inp: List[BaseSet]) -> List[TFuzzySet]:
        if len(inp) != len(self._input):
            raise EFuzzyModel("", NFE_INVALID_INPUTS)

        return self.f_evaluate_f([inp1.fuzzificate(inp2) for inp1, inp2 in zip(self._input, inp)])

    def c_evaluate_f(self, inp: List[TFuzzySet]) -> List[BaseSet]:
        return [out1.defuzzificate(out2) for out1, out2 in zip(self._output, self.f_evaluate_f(inp))]

    def c_evaluate_c(self, inp: List[BaseSet]) -> List[BaseSet]:
        if len(inp) != len(self._input):
            raise EFuzzyModel("", NFE_INVALID_INPUTS)

        out = self.f_evaluate_f([inp1.fuzzificate(inp2) for inp1, inp2 in zip(self._input, inp)])
        return [out1.defuzzificate(out2) for out1, out2 in zip(self._output, out)]

    def prepare(self):
        for block in self._blocks:
            block.prepare()
