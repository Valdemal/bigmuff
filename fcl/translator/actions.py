from builder import Builder
from fcl.enums import FCLTokens
from fcl.structs import FCLElement
from kernel.enums import VariableType, ValueType, FuzzifyMethod, MemberFuncType, DefuzzifyMethod, OperationCode
from kernel.fuzzy_set import TFuzzySet
from kernel.member_func import TMemberFuncLinear
from kernel.operation import obMaxMin, obSumProd, obLukasiewicz, obKDLogic, obZ2Logic, obZ3Logic
from kernel.variables.custom import TCustomVariable
from kernel.variables.fuzzy import TFuzzyVariable
from kernel.variables.ling import TLingVariable


def set_var_type(element: FCLElement, builder: Builder):
    match element.id:
        case FCLTokens.var_input:
            builder.set_var_type(VariableType.vtInput)
        case FCLTokens.var_output:
            builder.set_var_type(VariableType.vtOutput)
        case FCLTokens.var:
            builder.set_var_type(VariableType.vtIntermediate)


def create_function_block(element: FCLElement, builder: Builder):
    builder.func_block.name = builder.identifier


def create_variable(element: FCLElement, builder: Builder):
    match builder.var_value_type:
        case ValueType.valNA:
            raise Exception("Variable type is not valid")
        case ValueType.valFuzzy:
            v = TFuzzyVariable(builder.identifier,
                               TFuzzySet("", TMemberFuncLinear(float('-inf'), float('inf')), obMaxMin))
        case ValueType.valLinguistic:
            v = TLingVariable(builder.identifier, float('-inf'), float('inf'), obMaxMin)

    match builder.var_type:
        case VariableType.vtInput:
            v.type = VariableType.vtInput
            builder.func_block.add_input(v)
        case VariableType.vtOutput:
            v.type = VariableType.vtOutput
            builder.func_block.add_output(v)
        case VariableType.vtIntermediate:
            v.type = VariableType.vtIntermediate


def set_value_type(element: FCLElement, builder: Builder):
    match element.id:
        case FCLTokens.null:
            builder.set_var_value_type(ValueType.valNA)
        case FCLTokens.fuzzy:
            builder.set_var_value_type(ValueType.valFuzzy)
        case FCLTokens.ling:
            builder.set_var_value_type(ValueType.valLinguistic)
        case FCLTokens.cat:
            builder.set_var_value_type(ValueType.valCategorical)


def identifier_token(element: FCLElement, builder: Builder):
    builder.identifier = element.value


def string_token(element: FCLElement, builder: Builder):
    builder.set_string_literal(element.value)


def numeric_token(element: FCLElement, builder: Builder):
    builder.set_numeric_literal(float(element.value))


def end_function_block():
    pass


def set_fuzzify_method(element: FCLElement, builder: Builder):
    match element.id:
        case FCLTokens.null:
            builder.set_fuzzify_method(FuzzifyMethod.fmNA)
        case FCLTokens.tri:
            builder.set_fuzzify_method(FuzzifyMethod.fmTriangle)
        case FCLTokens.trap:
            builder.set_fuzzify_method(FuzzifyMethod.fmTrapezoid)
        case FCLTokens.singleton:
            builder.set_fuzzify_method(FuzzifyMethod.fmSingleton)
        case FCLTokens.gauss:
            builder.set_fuzzify_method(FuzzifyMethod.fmSmoothTrap)


def null_units(element: FCLElement, builder: Builder):
    builder.set_units("")


def set_points_count(element: FCLElement, builder: Builder):
    builder.set_points_count()


def set_units(element: FCLElement, builder: Builder):
    builder.set_units_from_literal()


def set_infinum(element: FCLElement, builder: Builder):
    builder.set_infinum()


def set_supremum(element: FCLElement, builder: Builder):
    builder.set_supremum()


def set_in_var_param(element: FCLElement, builder: Builder):
    idx = builder.func_block.is_input_exists(builder.identifier)
    if idx == -1:
        raise Exception()

    builder.current_var = builder.func_block.inputs[idx]
    builder.current_var.fuzzify = builder.fuzzify_method
    builder.current_var.units = builder.units

    match builder.current_var.value_type:
        case ValueType.valFuzzy:
            builder.current_var.fuzzy_set.func.inf = builder.infinum
            builder.current_var.fuzzy_set.func.sup = builder.supremum
        case ValueType.valLinguistic:
            builder.current_var.inf = builder.infinum
            builder.current_var.sup = builder.supremum


def false_learn(element: FCLElement, builder: Builder):
    builder.learning = False


def true_learn(element: FCLElement, builder: Builder):
    builder.learning = True


def create_term(element: FCLElement, builder: Builder):
    builder.create_term()


def set_func_type(element: FCLElement, builder: Builder):
    match element.id:
        case FCLTokens.abstract:
            builder.func_type = MemberFuncType.mfNA
        case FCLTokens.singleton:
            builder.func_type = MemberFuncType.mfSingleton
        case FCLTokens.linear:
            builder.func_type = MemberFuncType.mfLinear
        case FCLTokens.smooth:
            builder.func_type = MemberFuncType.mfSmooth
        case FCLTokens.vect:
            builder.func_type = MemberFuncType.mfLnVector


def create_func(element: FCLElement, builder: Builder):
    builder.create_func()


def set_x_val(element: FCLElement, builder: Builder):
    builder.set_x_val()


def set_y_val(element: FCLElement, builder: Builder):
    builder.set_y_val()


def create_point(element: FCLElement, builder: Builder):
    builder.create_point()


def set_defuzzify_method(element: FCLElement, builder: Builder):
    match element.id:
        case FCLTokens.null:
            builder.defuzzify_method = DefuzzifyMethod.dmNA
        case FCLTokens.cog:
            builder.defuzzify_method = DefuzzifyMethod.dmCOG
        case FCLTokens.coa:
            builder.defuzzify_method = DefuzzifyMethod.dmCOA
        case FCLTokens.lm:
            builder.defuzzify_method = DefuzzifyMethod.dmLM
        case FCLTokens.rm:
            builder.defuzzify_method = DefuzzifyMethod.dmRM
        case FCLTokens.mom:
            builder.defuzzify_method = DefuzzifyMethod.dmMOM


def set_out_var_param(element: FCLElement, builder: Builder):
    idx = builder.func_block.is_output_exists(builder.identifier)
    if idx == -1:
        raise Exception()

    builder.current_var = builder.func_block.outputs[idx]
    builder.current_var.defuzzify = builder.defuzzify_method
    builder.current_var.units = builder.units

    match builder.current_var.value_type:
        case ValueType.valFuzzy:
            builder.current_var.fuzzy_set.func.inf = builder.infinum
            builder.current_var.fuzzy_set.func.sup = builder.supremum
        case ValueType.valLinguistic:
            builder.current_var.inf = builder.infinum
            builder.current_var.sup = builder.supremum


def set_oper_base(element: FCLElement, builder: Builder):
    match element.id:
        case FCLTokens.maxmin:
            builder.oper_base = obMaxMin
        case FCLTokens.sumprod:
            builder.oper_base = obSumProd
        case FCLTokens.lukasiewicz:
            builder.oper_base = obLukasiewicz
        case FCLTokens.kdlogic:
            builder.oper_base = obKDLogic
        case FCLTokens.z2logic:
            builder.oper_base = obZ2Logic
        case FCLTokens.z3logic:
            builder.oper_base = obZ3Logic


def set_oper_poins(element: FCLElement, builder: Builder):
    if builder.points == 0:
        builder.oper_base.points = 100
    else:
        builder.oper_base.points = builder.points

    builder.points = 0


def set_certainty(element: FCLElement, builder: Builder):
    builder.certainty = builder.numeric_literal


def create_rule_block(element: FCLElement, builder: Builder):
    builder.create_rule_block()


def create_rule(element: FCLElement, builder: Builder):
    builder.create_rule()


def add_in_var(element: FCLElement, builder: Builder):
    idx = builder.func_block.is_input_exists(builder.identifier)
    if idx == -1:
        raise Exception()

    builder.ant_comb.append(OperationCode.ocValue)
    builder.ant_comb.append(len(builder.antecedent))
    builder.antecedent.append(idx)

    builder.ant_value.append([])
    builder.current_val_vect = builder.ant_value[-1]
    builder.curr_val_type = VariableType.vtInput
    builder.curr_val_num = idx


def add_in_not(element: FCLElement, builder: Builder):
    builder.ant_comb.append(OperationCode.ocNot)


def add_in_or(element: FCLElement, builder: Builder):
    builder.ant_comb.append(OperationCode.ocOr)


def add_in_and(element: FCLElement, builder: Builder):
    builder.ant_comb.append(OperationCode.ocAnd)


def add_ter_or(element: FCLElement, builder: Builder):
    builder.current_val_vect.append(OperationCode.ocOr)


def add_term(element: FCLElement, builder: Builder):
    idx = -1

    match builder.curr_val_type:
        case VariableType.vtInput:
            idx = builder.current_rules.is_input_term_exists(builder.curr_val_num, builder.identifier)
        case VariableType.vtOutput:
            idx = builder.current_rules.is_output_term_exists(builder.curr_val_num, builder.identifier)

    if idx == -1:
        raise Exception("FCLE_UNKNOWN_TERM")

    builder.current_val_vect.append(OperationCode.ocValue)
    builder.current_val_vect.append(idx)


def add_term_not(element: FCLElement, builder: Builder):
    builder.current_val_vect.append(OperationCode.ocNot)


def add_term_con(element: FCLElement, builder: Builder):
    builder.current_val_vect.append(OperationCode.ocVery)


def add_term_dil(element: FCLElement, builder: Builder):
    builder.current_val_vect.append(OperationCode.ocAverage)


def add_term_and(element: FCLElement, builder: Builder):
    builder.current_val_vect.append(OperationCode.ocAnd)


def add_out_var(element: FCLElement, builder: Builder):
    idx = builder.func_block.is_output_exists(builder.identifier)
    if idx == -1:
        raise Exception("FCLE_UNKNOWN_IDENT")
    builder.consequent = idx
    builder.current_val_vect = builder.cons_value
    builder.curr_val_type = VariableType.vtOutput
    builder.curr_val_num = idx


def set_rule_name(element: FCLElement, builder: Builder):
    builder.rule_name = builder.identifier


def bad_fuzzify(element: FCLElement, builder: Builder):
    raise Exception("FCLE_INVALID_FUZ_METHOD")


def bad_defuzzify(element: FCLElement, builder: Builder):
    raise Exception("FCLE_INVALID_DEFUZ_METHOD")


def bad_oper_base(element: FCLElement, builder: Builder):
    raise Exception("FCLE_INVALID_OPERBASE")


def fcl_tok_exp(element: FCLElement, builder: Builder):
    raise Exception("FCLE_TOKEN_EXPECTED")


def fcl_idt_exp(element: FCLElement, builder: Builder):
    raise Exception("FCLE_IDENTIFIER_EXPECTED")


def fcl_num_exp(element: FCLElement, builder: Builder):
    raise Exception("FCLE_IDENTIFIER_EXPECTED")


def fcl_str_exp(element: FCLElement, builder: Builder):
    raise Exception("FCLE_STRING_EXPECTED")


def fcl_eof_exp(element: FCLElement, builder: Builder):
    raise Exception("FCLE_EOF_EXPECTED")


def fcl_err_tok(element: FCLElement, builder: Builder):
    raise Exception("FCLE_SYNTAX_ERROR")


def fcl_parse_done(element: FCLElement, builder: Builder):
    pass
