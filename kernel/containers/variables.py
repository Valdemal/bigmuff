from typing import Iterable, List

from kernel.containers.mediator import NeuroFuzzyComponent, NeuroFuzzyMediator
from kernel.variables.custom import CustomVariable


class VarContainer(NeuroFuzzyComponent):
    def __init__(self, variables: Iterable[CustomVariable]=None, mediator: NeuroFuzzyMediator = None):
        super().__init__(mediator)
        if variables is None:
            variables = []
        self._variables: List[CustomVariable] = list(variables)

    def append(self, variable: CustomVariable):
        self._variables.append(variable)

        if self._mediator is not None:
            self._mediator.notify(self, 'append', len(self._variables) - 1)


    def pop(self, index: int) -> CustomVariable:
        if self._mediator is not None:
            self._mediator.notify(self, 'pop', index)

        return self._variables.pop(index)

    def name_index(self, name: str):
        for i, var in enumerate(self._variables):
            if var.name == name:
                return i

        return -1

    def __getitem__(self, index) -> CustomVariable:
        return self._variables[index]

    def __iter__(self):
        return iter(self._variables)

    def __len__(self):
        return len(self._variables)
