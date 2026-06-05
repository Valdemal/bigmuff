import math

from kernel.comparison import le
from kernel.consts import Crisp
from kernel.member_func.linear import TMemberFuncLinearBase
from kernel.node_value import TNodeValue


class GaussianMemberFunc(TMemberFuncLinearBase):
    _ACCURACY = 0.1
    def __init__(self, mean: Crisp, dev: Crisp, accuracy: float = _ACCURACY):
        edge = dev * math.sqrt(2 * dev ** 2)
        super().__init__(mean - edge, mean + edge)

        self._mean = mean
        self._dev = dev
        gauss = self._get_gauss(mean, dev)
        xi = self.inf
        while le(xi, self.sup):
            self.append_node(TNodeValue(xi, gauss(xi), self))
            xi += accuracy

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