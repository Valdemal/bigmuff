import math
from typing import Callable

from kernel.consts import Membership
from kernel.fuzzy_set import TFuzzySet
from kernel.member_func import GaussianMemberFunc

PossibilityFunction = Callable[[Membership], Membership]

def get_possibility_func(set1: TFuzzySet, set2: TFuzzySet) -> PossibilityFunction:
    func1, func2 = set1.func, set2.func

    if isinstance(func1, GaussianMemberFunc):
        if isinstance(func2, GaussianMemberFunc):
            return get_cp_for_gaussians(func1, func2)

    raise NotImplemented()

def get_cp_for_gaussians(gauss1: GaussianMemberFunc, gauss2: GaussianMemberFunc) -> PossibilityFunction:
    def callback(tau: Membership) -> Membership:
        coef = gauss1.dev * math.sqrt(-2 * math.log(tau))
        denominator = 2 * gauss2.dev ** 2
        mean_delta = gauss1.mean - gauss2.mean
        pow1 = -(mean_delta - coef) ** 2 / denominator
        pow2 = -(mean_delta + coef) ** 2 / denominator
        return max(math.exp(pow1), math.exp(pow2))

    return callback