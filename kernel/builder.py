from typing import List

from kernel.block.function import TFunctionBlock
from kernel.consts import BaseSet, Natural, StdLingNames
from kernel.enums import FuzzifyMethod, DefuzzifyMethod, VariableType, OperationCode
from kernel.fuzzy_set import TFuzzySet
from kernel.member_func.linear import TMemberFuncLinear
from kernel.member_func.smooth import TMemberFuncSmooth
from kernel.operation import TOperationBase
from kernel.variables.ling import TLingVariable


def create_classify_block(
    name: str, points_count: Natural, inf: BaseSet, sup: BaseSet, units: str, terms_count: Natural,
    classes_count: Natural, class_name: List[str], fuzz: FuzzifyMethod, defuzz: DefuzzifyMethod,
    op_base: TOperationBase, learn_in_mf: bool, learn_out_mf: bool
) -> TFunctionBlock:
    block = TFunctionBlock(name)

    for i in range(points_count):
        var = TLingVariable('in_' + str(i), inf, sup, op_base, fuzz, defuzz)
        var.type = VariableType.vtInput

        s_fact, b_fact = 0, 1

        cwid = (sup - inf) / 200 * 20
        step = (sup - inf - 2 * cwid) / (terms_count - 1)

        x1 = inf + cwid
        x2 = x1 + step * b_fact
        b_fact += s_fact
        x3 = x2 + step * b_fact
        n_id = (7 - terms_count) / 2
        name = StdLingNames[3][n_id]

        # первый краевой терм
        func = TMemberFuncSmooth(True, x1, x2, inf, sup)
        set = TFuzzySet(name, func, op_base)
        set.learn = learn_in_mf
        var.add_term(set)

        for _ in range(1, terms_count - 1):
            n_id += 1
            name = StdLingNames[3][n_id]
            func = TMemberFuncSmooth(x1, x2, x3, 1, inf, sup)
            set = TFuzzySet(name, func, op_base)
            set.learn = learn_in_mf
            var.add_term(set)

            x1 = x2
            x2 = x3
            b_fact += s_fact
            x3 = step * b_fact

        n_id += 1
        name = StdLingNames[3][n_id]
        func = TMemberFuncSmooth(False, x1, x2, inf, sup)
        set = TFuzzySet(name, func, op_base)
        set.learn = learn_in_mf
        var.add_term(set)
        block.add_input(var)

    for i in range(classes_count):
        var = TLingVariable(class_name[i], 0, 1, op_base, fuzz, defuzz)
        var.type = VariableType.vtOutput
        var.add_term(TFuzzySet("соответсвует", TMemberFuncLinear(False, 0, 1, 0, 1), op_base))

        for j in range(len(var.term)):
            var.term[i].learn = learn_out_mf

        block.add_output(var)

    block.add_block("Main", op_base)

    return block

def add_rules(block: TFunctionBlock,  learn: bool):
    # todo требуется переписать модуль с ген. алгоритмом
    ant = [0] * block.input_count
    ant_val = [[] for _ in range(block.input_count)]

    ant_comb = [OperationCode.ocValue, 0]
    ant[0] = 0

    for i in range(1, len(ant)):
        ant[i] = i
        ant_comb.append(OperationCode.ocValue)
        ant_comb.append(i)
        ant_comb.append(OperationCode.ocAnd)

    cons_val = [OperationCode.ocValue, 0]

    # for i in range(len())
    #     pass


def select_rules(proj: TFunctionBlock, count: Natural):
    # todo требуется переписать модуль с ген. алгоритмом
    pass
