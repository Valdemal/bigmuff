from kernel.operation import OperationBase


class Named:
    def __init__(self, name: str):
        self._name = name

    @property
    def name(self) -> str:
        return self._name

    @name.setter
    def name(self, value: str):
        self._name = value


class OperationBased:
    def __init__(self, ops: OperationBase):
        self._ops = ops

    @property
    def ops(self) -> OperationBase:
        return self._ops

    @ops.setter
    def ops(self, value: OperationBase):
        self._ops = value


class Learnable:
    def __init__(self, learn: bool):
        self._learn = learn

    @property
    def learn(self) -> bool:
        return self._learn

    @learn.setter
    def learn(self, value: bool):
        self._learn = value
