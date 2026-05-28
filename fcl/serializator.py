from typing import List

from fcl.consts import VARIABLE_VAL_TYPE_NAME, FUZZIFY_METHOD_NAME, MEMBER_FUNC_TYPE_NAME, DEFUZZIFY_METHOD_NAME
from kernel.block.function import TFunctionBlock
from kernel.block.rule import TRuleBlock
from kernel.enums import OperationCode
from kernel.fuzzy_set import TFuzzySet
from kernel.member_func import TMemberFunc
from kernel.rules.composite import TCompositeRule
from kernel.variables.custom import TCustomVariable
from kernel.variables.fuzzy import TFuzzyVariable
from kernel.variables.ling import TLingVariable


def to_fcl(func_block: TFunctionBlock) -> str:
    return f"""FUNCTION_BLOCK {func_block.name}

VAR_INPUT
{'\n'.join(var_to_fcl(inp) for inp in func_block.inputs)}
END_VAR

VAR_OUTPUT
{'\n'.join(var_to_fcl(out) for out in func_block.outputs)}
END_VAR
{''.join(fuzzify_to_fcl(var) for var in func_block.inputs)}
{''.join(defuzzify_to_fcl(var) for var in func_block.outputs)}
{''.join(rule_block_to_fcl(block) for block in func_block.blocks)}
END_FUNCTION_BLOCK
    """

def var_to_fcl(var: TCustomVariable) -> str:
    return f"\t{var.name} : {VARIABLE_VAL_TYPE_NAME[var.value_type.value]};"


def var_full_to_fcl(var: TCustomVariable) -> str:
    res = ""
    if var.units:
        res += f"""UNITS: "{var.units}";\n"""

    if isinstance(var, TFuzzyVariable):
        res += f"\tRANGE := ({var.fuzzy_set.func.inf} .. {var.fuzzy_set.func.sup})\n;\t"
        res += fuzzy_set_to_fcl(var.fuzzy_set)

    elif isinstance(var, TLingVariable):
        res += f"\tRANGE := ({var.inf} .. {var.sup})\n\t"
        res += '\t'.join(fuzzy_set_to_fcl(term) for term in var.terms)

    return res


def fuzzify_to_fcl(var: TCustomVariable) -> str:
    return f"""FUZZIFY {var.name}
    METHOD: {FUZZIFY_METHOD_NAME[var.fuzzify.value]};
    {var_full_to_fcl(var)}END_FUZZIFY    
    """


def defuzzify_to_fcl(var: TCustomVariable) -> str:
    return f"""DEFUZZIFY {var.name}
    METHOD: {DEFUZZIFY_METHOD_NAME[var.defuzzify.value]};
    {var_full_to_fcl(var)}END_DEFUZZIFY 
"""


def member_func_to_fcl(func: TMemberFunc):
    result = f"{MEMBER_FUNC_TYPE_NAME[func.type.value]} "

    if func.is_nodes():
        for i in range(len(func.nodes)):
            result += str(func.nodes[i]) + " "
    elif func.is_vector():
        x = func.inf
        if len(func.data) > 1:
            step = (func.sup - func.inf) / (len(func._data) - 1)
        else:
            step = 0

        for d in func.data:
            result += f"({x}, {d}) "
            x += step

    return result

def fuzzy_set_to_fcl(fuzzy_set: TFuzzySet) -> str:
    res = f"TERM {fuzzy_set.name} := {member_func_to_fcl(fuzzy_set.func)}"
    if fuzzy_set.learn:
        res += "LEARN"

    return res + ';\n'


def rule_to_fcl(rule: TCompositeRule) -> str:
    # Формирование выражения антецедента
    res_stack: List[str] = []

    i = 0
    while i < len(rule.rule_expr):
        opcode = rule.rule_expr[i]
        i += 1

        if opcode == OperationCode.ocValue:
            val = rule.rule_expr[i]
            i += 1

            if val >= len(rule.rules):
                raise Exception("неверный индекс входной переменной правила")

            res_stack.append(f'({rule.rules[val].ant.name})')

        elif opcode == OperationCode.ocNot:
            if not res_stack:
                raise Exception("недостаточно операндов")
            op = res_stack.pop()
            res_stack.append(f"NOT {op}")

        elif opcode == OperationCode.ocAnd:
            if len(res_stack) < 2:
                raise Exception("недостаточно операндов")
            op2 = res_stack.pop()
            op1 = res_stack.pop()
            res_stack.append(f"{op1} AND {op2}")

        elif opcode == OperationCode.ocOr:
            if len(res_stack) < 2:
                raise Exception("недостаточно операндов")
            op2 = res_stack.pop()
            op1 = res_stack.pop()
            res_stack.append(f"({op1}) OR ({op2})")

        else:
            raise Exception("неверный оператор (допустимы И, ИЛИ, НЕ)")

    if len(res_stack) != 1:
        raise Exception("неполное выражение")

    result = f"RULE {rule.name} : IF {res_stack[0]} THEN {rule.rules[0].cons.name} WITN {rule.certainty}"

    if rule.learn:
        result += f" LEARN"

    result += ";"

    return result


def rule_block_to_fcl(block: TRuleBlock) -> str:
    return f"""RULEBLOCK {block.name}
    OPERATION_BASE : {block.ops.name}, {block.ops.points};
    {'\n\t'.join(rule_to_fcl(rule) for rule in block.rules)}
END_RULEBLOCK
"""