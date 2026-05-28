from typing import Callable, Iterable

from attr import dataclass

from builder import Builder
from fcl.enums import FCLTokens, FCLRules
from kernel.block.rule import TRuleBlock
from kernel.consts import BaseSet, Natural
from kernel.enums import VariableType, ValueType, FuzzifyMethod, DefuzzifyMethod, MemberFuncType
from kernel.fuzzy_set import TFuzzySet
from kernel.member_func.base import TMemberFunc
from kernel.operation import TOperationBase
from kernel.variables.custom import TCustomVariable

# Структура лексемы
@dataclass
class FCLElement:
    id: FCLTokens
    value: str
    str_pos: int
    chr_pos: int


@dataclass
class FCLMatrixSymbol:
    pop: bool
    next: bool
    action: Callable[[FCLElement, Builder], None] = None
    to_stack: Iterable[FCLTokens | FCLRules] = ()

@dataclass
class ParserState:
    filename: str
    current_token: FCLTokens
    current_rule: str
    current_element: FCLElement
    FCLProgram: list[FCLElement] = []
    stack: list[FCLElement] = []
    error_state:int = 0

@dataclass
class TranslatorState:
    identifier: str
    string_literal: str
    numeric_literal: float
    string_pos: int
    char_pos: int

@dataclass
class CurrentVar:
    current_var: TCustomVariable
    var_type: VariableType
    var_value_type: ValueType
    fuz_method: FuzzifyMethod
    defuz_method: DefuzzifyMethod
    units: str
    infinum: BaseSet
    supremum: BaseSet
    learning: bool = False

@dataclass
class CurrentFunction:
    current_set: TFuzzySet
    current_func: TMemberFunc
    func_type: MemberFuncType
    x_value: BaseSet
    y_value: BaseSet
    points: Natural = 0


@dataclass
class CurrentRuleBlock:
    current_rules: TRuleBlock
    oper_base: TOperationBase
    certainty: float = 1


@dataclass
class RuleValue:
    rule_name: str
    consequent: Natural
    current_val_vect: list[Natural]
    curr_val_type: VariableType
    curr_val_num: Natural
    antecedent: list[Natural] = []
    cons_value: list[Natural] = []
    ant_comb: list[Natural] = []
    ant_value: list[list[Natural]] = []


