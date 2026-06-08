from abc import abstractmethod, ABC

from kernel.consts import Crisp, DELTA_AMOUNT, CRISP_AMOUNT
from kernel.member_func import TMemberFunc, TMemberFuncSingle, GaussianMemberFunc
from kernel.member_func.linear import TMemberFuncTriangular, TMemberFuncTrapezoidal
from kernel.mixins import RangeDefined


class FuzzificationMethod(ABC):
    @abstractmethod
    def __call__(self, crisp: Crisp, base: RangeDefined) -> TMemberFunc:
        pass


class NeighborhoodFuzzification(FuzzificationMethod, ABC):
    def __init__(self, delta_amount=DELTA_AMOUNT, crisp_amount=CRISP_AMOUNT):
        self._delta_amount = delta_amount
        self._crisp_amount = crisp_amount

    def _get_delta(self, base: RangeDefined):
        return (base.sup - base.inf) * self._delta_amount / 2

    def _get_crdel(self, base: RangeDefined):
        return (base.sup - base.inf) * self._crisp_amount / 2


class TriangularFuzzification(NeighborhoodFuzzification):
    def __call__(self, crisp: Crisp, base: RangeDefined) -> TMemberFunc:
        delta = self._get_delta(base)
        p1 = max(base.inf, crisp - delta)
        p2 = min(base.sup, crisp + delta)
        return TMemberFuncTriangular(p1, crisp, p2, 1.0, base.inf, base.sup)


class TrapezoidFuzzification(NeighborhoodFuzzification):
    def __call__(self, crisp: Crisp, base: RangeDefined) -> TMemberFunc:
        delta, crdelta = self._get_delta(base), self._get_crdel(base)
        p1 = max(base.inf, crisp - delta - crdelta)
        p2 = max(base.inf, crisp - crdelta)
        p3 = min(base.sup, crisp + crdelta)
        p4 = min(base.sup, crisp + crdelta + delta)
        return TMemberFuncTrapezoidal(p1, p2, p3, p4, 1.0, base.inf, base.sup)


class SingletonFuzzification(NeighborhoodFuzzification):
    def __call__(self, crisp: Crisp, base: RangeDefined) -> TMemberFunc:
        return TMemberFuncSingle(crisp, 1.0, base.inf, base.sup)


class GaussFuzzification(NeighborhoodFuzzification):
    def __call__(self, crisp: Crisp, base: RangeDefined) -> TMemberFunc:
        mean = self._get_delta(base)
        return GaussianMemberFunc(base.inf, base.sup, crisp, mean)
