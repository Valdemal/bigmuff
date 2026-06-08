from kernel.comparison import ge, le
from kernel.consts import Crisp
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
        self._set_ops(value)

    def _set_ops(self, value):
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


class RangeDefined:
    def __init__(self, inf: Crisp, sup: Crisp):
        if ge(inf, sup):
            raise ValueError()

        self._inf = inf
        self._sup = sup

    @property
    def inf(self) -> Crisp:
        return self._inf

    @property
    def sup(self) -> Crisp:
        return self._sup

    @inf.setter
    def inf(self, value: Crisp):
        """Установить нижнюю границу базового множества"""
        if ge(value, self.sup):
            raise ValueError()

        self._set_inf(value)

    @sup.setter
    def sup(self, value: Crisp):
        """Установить верхнюю границу базового множества"""
        if le(value, self.inf):
            raise ValueError()

        self._set_sup(value)

    def _set_inf(self, value):
        self._inf = value

    def _set_sup(self, value):
        self._sup = value