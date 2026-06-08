import math

from kernel.comparison import le
from kernel.consts import Crisp, Membership
from kernel.member_func.linear import TMemberFuncLinearBase
from kernel.node_value import TNodeValue


class GaussianMemberFunc(TMemberFuncLinearBase):
    _ACCURACY = 0.05
    def __init__(self, inf: Crisp, sup: Crisp, mean: Crisp, dev: Crisp, accuracy: float = _ACCURACY):
        super().__init__(inf, sup)
        self._mean = mean
        self._dev = dev
        self._gauss = self._get_gauss(mean, dev)
        xi = self.inf
        while le(xi, self.sup):
            self.append_node(TNodeValue(xi, self._gauss(xi), self))
            xi += accuracy

    def _get_value(self, value: Crisp) -> Membership:
        return self._gauss(value)

    @property
    def mean(self) -> Crisp:
        return self._mean

    @property
    def dev(self) -> Crisp:
        return self._dev

    @staticmethod
    def _get_gauss(mean, dev):
        def gauss(x):
                return math.exp(-(x - mean) ** 2 / (2 * dev ** 2))

        return gauss