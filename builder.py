from errno import ECANCELED

from kernel.blocks import FunctionalBlock, RuleBlock
from kernel.consts import Crisp
from kernel.containers.evaluatedvar import EvaluatedVar
from kernel.enums import VariableType, ValueType, FuzzifyMethod, DefuzzifyMethod, MemberFuncType
from kernel.fuzzification import FuzzificationMethod
from kernel.fuzzy_set import TFuzzySet
from kernel.member_func import TMemberFunc, TMemberFuncSingle, TMemberFuncLinear, \
    TMemberFuncLnVect, GaussianMemberFunc
from kernel.node_value import TNodeValue
from kernel.operation import obMaxMin, OperationBase
from kernel.rules import CompositeRule
from kernel.variables.custom import CustomVariable


class Builder:
    def __init__(self):
        self._func_block = FunctionalBlock("Без названия")
        # todo вынести в класс транслятора
        self._identifier = ""
        self._string_literal = ""
        self.numeric_literal = 0

        # рассматриваемая переменная
        # todo сократить до одного свойства current_var
        self._current_var: CustomVariable | None = None
        self.var_type: VariableType | None = None
        self.var_value_type: ValueType | None = None
        self._fuzzify_method: FuzzificationMethod | None = None
        self._defuzzify_method: DefuzzifyMethod | None = None
        self._units: str = ""
        self.infinum: Crisp = 0
        self.supremum: Crisp = 1
        self._learning = False

        # рассматриваемая функция принадлежности
        self._current_func: TMemberFunc | None = None
        self._points = 0
        self._current_set: TFuzzySet | None = None
        self._func_type: MemberFuncType | None = None
        self._x = 0
        self._y = 0

        # Рассматриваемый блок правил
        self._oper_base: OperationBase | None = None
        self.certainty = 1
        self.current_rules: RuleBlock | None = None


        # Выражения правила
        self.rule_name = ""
        self.antecedent = []
        self.cons_value = []
        self.ant_comb = []

        self.ant_value: list[list[int]] = []
        self.consequent = 0
        self.current_val_vect = []
        self.curr_val_type: VariableType | None = None
        self.curr_val_num = 0

    @property
    def func_block(self):
        return self._func_block

    @property
    def identifier(self) -> str:
        return self._identifier

    @identifier.setter
    def identifier(self, value: str):
        self._identifier = value

    def create_term(self):
        self._current_set = TFuzzySet(self.identifier, self._current_func, obMaxMin)
        self._current_set.learn = self._learning
        self._learning = False
        match self._current_var.value_type:
            case ValueType.valFuzzy:
                self.current_var.fuzzy_set = self._current_set
            case ValueType.valLinguistic:
                self.current_var.terms.append(self._current_set)

    @property
    def oper_base(self):
        return self._oper_base

    @oper_base.setter
    def oper_base(self, value):
        self._oper_base = value

    def create_func(self):
        match self._func_type:
            case MemberFuncType.mfNA:
                self._current_func = TMemberFunc(self.infinum, self.supremum)
            case MemberFuncType.mfSingleton:
                self._current_func = TMemberFuncSingle(self.infinum, self.supremum)
            case MemberFuncType.mfLinear:
                self._current_func = TMemberFuncLinear(self.infinum, self.supremum)
            case MemberFuncType.mfGauss:
                self._current_func = GaussianMemberFunc(self.infinum, self.supremum, 1, 1)
            case MemberFuncType.mfLnVector:
                self._current_func = TMemberFuncLnVect(self.infinum, self.supremum, self._points)
                self._points = 0

    def set_string_literal(self, value: str):
        self._string_literal = value

    def set_numeric_literal(self, value: float):
        self.numeric_literal = value

    def set_x_val(self):
        self._x = self.numeric_literal

    def set_y_val(self):
        self._y = self.numeric_literal

    def create_point(self):
        match self.func_type:
            case MemberFuncType.mfSingleton | MemberFuncType.mfSmooth | MemberFuncType.mfLinear | MemberFuncType.mfNA:
                self._current_func.add_node(TNodeValue(self._x, self._y))
            case MemberFuncType.mfLnVector:
                idx = self._x * (len(self._current_func.data) - 1) // (self._current_func.sup - self._current_func.inf)
                self._current_func[idx] = self._y
            case MemberFuncType.mfGauss:
                self._current_func = GaussianMemberFunc(self._current_func.inf, self._current_func.sup, self._x, self._y)

    def set_var_type(self, var_type: VariableType):
        self.var_type = var_type

    def set_var_value_type(self, value_type: ValueType):
        self.var_value_type = value_type

    def set_fuzzify_method(self, fuzzify_method: FuzzificationMethod):
        self._fuzzify_method = fuzzify_method

    def set_units(self, units: str):
        self._units = units

    def set_units_from_literal(self):
        self._units = self._string_literal

    def set_points_count(self):
        self._points = int(abs(self.numeric_literal))

        if self._points != self.numeric_literal:
            raise Exception("need int")

    def set_infinum(self):
        self.infinum = self.numeric_literal
        self.fuzzify_method.inf = self.infinum

    def set_supremum(self):
        self.supremum = self.numeric_literal
        self.fuzzify_method.sup = self.supremum

    @property
    def current_var(self):
        return self._current_var

    @current_var.setter
    def current_var(self, value: CustomVariable):
        self._current_var = value

    @property
    def fuzzify_method(self):
        return self._fuzzify_method

    @property
    def defuzzify_method(self):
        return self._defuzzify_method

    @defuzzify_method.setter
    def defuzzify_method(self, value):
        self._defuzzify_method = value

    @property
    def units(self):
        return self._units

    @property
    def learning(self) -> bool:
        return self._learning

    @learning.setter
    def learning(self, value: bool):
        self._learning = value

    @property
    def func_type(self):
        return self._func_type

    @func_type.setter
    def func_type(self, value):
        self._func_type = value

    @property
    def points(self):
        return self._points

    @points.setter
    def points(self, value):
        self._points = value

    def create_rule_block(self):
        self.func_block.blocks.append(
            RuleBlock(self.identifier, self.func_block, self.oper_base)
        )
        self.current_rules = self.func_block.blocks[-1]

    def create_rule(self):
        rule = CompositeRule(
            self.rule_name,
            EvaluatedVar(self.func_block.outputs[self.consequent],self.cons_value),
            self.certainty, self.current_rules.ops
        )
        i = self.current_rules.add_rule(
            rule, self.antecedent, self.ant_value, self.ant_comb, self.consequent
        )
        self.current_rules.rules[i].learn = self._learning
        self._learning = False
        self.certainty = 1
        self.antecedent.clear()
        self.cons_value.clear()
        self.ant_comb.clear()
        self.ant_value.clear()
