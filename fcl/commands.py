from fcl.enums import FCLTokens, FCLRules
from kernel.enums import VariableType


def set_var_type(current_token):
    match current_token:
        case FCLTokens.var_input:
            return VariableType.vtInput
        case FCLTokens.var_output:
            return VariableType.vtOutput
        case FCLTokens.var:
            return VariableType.vtIntermediate


def create_function_block():
    pass


def create_variable():
    pass


def set_value_type():
    pass


def identifier_token():
    pass


def string_token():
    pass


def numeric_token():
    pass


def end_function_block():
    pass


def set_fuzzify_method():
    pass


def null_units():
    pass


def set_points_count():
    pass


def set_units():
    pass


def set_infinum():
    pass


def set_supremum():
    pass


def set_in_var_param():
    pass


def false_learn():
    pass


def true_learn():
    pass


def create_term():
    pass


def set_func_type():
    pass


def create_func():
    pass


def set_x_val():
    pass


def set_y_val():
    pass


def create_point():
    pass


def set_defuzzify_method():
    pass


def set_out_var_param():
    pass


def set_oper_base():
    pass


def set_oper_poins():
    pass


def set_certainty():
    pass


def create_rule_block():
    pass


def create_rule():
    pass


def add_in_var():
    pass


def add_in_not():
    pass


def add_in_or():
    pass


def add_in_and():
    pass


def add_ter_or():
    pass


def add_term():
    pass


def add_term_not():
    pass


def add_term_con():
    pass


def add_term_dil():
    pass


def add_term_and():
    pass


def add_out_var():
    pass


def set_rule_name():
    pass


def bad_fuzzify():
    pass


def bad_defuzzify():
    pass


def bad_oper_base():
    pass


def fcl_tok_exp():
    pass


def fcl_idt_exp():
    pass


def fcl_num_exp():
    pass


def fcl_str_exp():
    pass


def fcl_eof_exp():
    pass


def fcl_err_tok():
    pass


def fcl_parse_done():
    pass


NOTHING = 0, None, False, False, None, -1
NEXT = 0, None, True, True, None, -1

ERR_TOC = 0, None, False, False, fcl_tok_exp, -1

ERR_IDT = 0, None, False, False, fcl_idt_exp, -1

ERR_NUM = 0, None, False, False, fcl_num_exp, -1

ERR_STR = 0, None, False, False, fcl_str_exp, -1

ERR_EOF = 0, None, False, False, fcl_eof_exp, -1

FC_ERR = 0, None, False, False, fcl_err_tok, -1

FC_DONE = 0, None, False, False, fcl_parse_done, -1

FB = 4, (FCLTokens.identifier, FCLRules.c_fb, FCLRules.fb1, FCLTokens.end_function_block), True, True, None, -1

C_FB = 0, None, True, False, create_function_block, -1

FB1_1 = 0, None, True, False, None, -1
FB1_2 = 2, (FCLRules.iv, FCLRules.fb1), True, False, None, -1
FB1_3 = 2, (FCLRules.ov, FCLRules.fb1), True, False, None, -1
FB1_4 = 2, (FCLRules.fzb, FCLRules.fb1), True, False, None, -1
FB1_5 = 2, (FCLRules.dfb, FCLRules.fb1), True, False, None, -1
FB1_6 = 2, (FCLRules.rb, FCLRules.fb1), True, False, None, -1

IV = 3, (FCLTokens.var_input, FCLRules.vd, FCLTokens.end_var), True, False, set_var_type, -1
OV = 3, (FCLTokens.var_output, FCLRules.vd, FCLTokens.end_var), True, False, set_var_type, -1

VD_1 = 0, None, True, False, None, -1
VD_2 = (
    6, (FCLTokens.identifier, FCLTokens.colon, FCLRules.vt, FCLTokens.semicolon, FCLRules.c_var, FCLRules.vd), True,
    False,
    None, -1)

C_VAR = 0, None, True, True, create_variable, -1
VT = 0, None, True, False, set_value_type, -1

IDENTIF = 0, None, True, True, identifier_token, -1

STRINGL = 0, None, True, True, string_token, -1

NUMBERL = 0, None, True, True, numeric_token, -1

ENDFNCB = 0, None, True, True, end_function_block, -1

FZB = 8, (
    FCLTokens.fuzzify, FCLTokens.identifier, FCLRules.fzm, FCLRules.un, FCLRules.rn, FCLRules.c_fzb, FCLRules.tr,
    FCLTokens.end_fuzzify), True, False, None, -1

FZM = 4, (FCLTokens.method, FCLTokens.colon, FCLRules.fzm1, FCLTokens.semicolon), True, False, None, -1

FZM1 = 0, None, True, True, set_fuzzify_method, -1

UN1 = 0, None, True, False, null_units, -1

UN = 5, (
    FCLTokens.units, FCLTokens.colon, FCLTokens.string_literal, FCLTokens.semicolon, FCLRules.c_un
), True, False, None, -1

RN = 11, (
    FCLTokens.range_tok, FCLTokens.assign, FCLTokens.lbrac, FCLTokens.numeric_literal, FCLRules.c_inf,
    FCLTokens.doubledot, FCLTokens.numeric_literal, FCLRules.c_sup, FCLRules.rn1, FCLTokens.rbrac, FCLTokens.semicolon
), True, False, None, -1

RN1_1 = 0, None, True, False, None, -1

RN1_2 = 3, (FCLTokens.comma, FCLTokens.numeric_literal, FCLRules.c_pnt), True, False, None, -1

C_PNT = 0, None, True, False, set_points_count, -1

C_UN = 0, None, True, False, set_units, -1

C_INF = 0, None, True, False, set_infinum, -1

C_SUP = 0, None, True, False, set_supremum, -1

C_FZB = 0, None, True, False, set_in_var_param, -1

TR_1 = 0, None, True, False, None, -1

TR_2 = 8, (
    FCLTokens.term, FCLTokens.identifier, FCLTokens.assign, FCLRules.mf, FCLRules.lrn, FCLTokens.semicolon,
    FCLRules.c_ter, FCLRules.tr
), True, False, None, -1

LRN1 = 0, None, True, False, false_learn, -1

LRN2 = 1, (FCLTokens.learn,), True, False, true_learn, -1

C_TER = 0, None, True, False, create_term, -1

MF = 3, (FCLRules.mt, FCLRules.c_mt, FCLRules.pt), True, False, None, -1

MT = 0, None, True, True, set_func_type, -1

C_MT = 0, None, True, False, create_func, -1

PT_1 = 0, None, True, False, None, -1

PT_2 = 9, (
    FCLTokens.lbrac, FCLTokens.numeric_literal, FCLRules.c_xdom, FCLTokens.comma, FCLTokens.numeric_literal,
    FCLRules.c_ydom, FCLTokens.rbrac, FCLRules.c_pt, FCLRules.pt
), True, False, None, -1

C_XDOM = 0, None, True, False, set_x_val, -1

C_YDOM = 0, None, True, False, set_y_val, -1

C_PT = 0, None, True, False, create_point, -1

DFB = 8, (
    FCLTokens.defuzzify, FCLTokens.identifier, FCLRules.dfm, FCLRules.un, FCLRules.rn, FCLRules.c_dfb, FCLRules.tr,
    FCLTokens.end_defuzzify
), True, False, None, -1

DFM = 4, (FCLTokens.method, FCLTokens.colon, FCLRules.dfm1, FCLTokens.semicolon), True, False, None, -1

DFM1 = 0, None, True, True, set_defuzzify_method, -1

C_DFB = 0, None, True, False, set_out_var_param, -1

RB = 6, (
    FCLTokens.ruleblock, FCLTokens.identifier, FCLRules.ob, FCLRules.c_rb, FCLRules.rl, FCLTokens.end_ruleblock
), True, False, None, -1

OB = 6, (
    FCLTokens.operation_base, FCLTokens.colon, FCLRules.obt, FCLRules.rn1, FCLRules.obpn, FCLTokens.semicolon
), True, False, None, -1

RL_1 = 0, None, True, False, None, -1

RL_2 = 13, (
    FCLTokens.rule, FCLTokens.identifier, FCLRules.c_rl2, FCLTokens.colon, FCLTokens.if_tok, FCLRules.an,
    FCLTokens.then, FCLRules.cn, FCLRules.wt, FCLRules.lrn, FCLTokens.semicolon, FCLRules.c_rl, FCLRules.rl
), True, False, None, -1

OBT = 0, None, True, True, set_oper_base, -1

OBPN = 0, None, True, False, set_oper_poins, -1

WT_1 = 0, None, True, False, None, -1

WT_2 = 3, (
    FCLTokens.with_tok, FCLTokens.numeric_literal, FCLRules.c_wt
), True, False, None, -1

C_WT = 0, None, True, False, set_certainty, -1

C_RB = 0, None, True, False, create_rule_block, -1

C_RL = 0, None, True, False, create_rule, -1

AN = 2, (FCLRules.an1, FCLRules.an2), True, False, None, -1

AN1 = 2, (FCLRules.an3, FCLRules.an4), True, False, None, -1

AN2_1 = 0, None, True, False, None, -1

AN2_2 = 4, (
    FCLTokens.or_tok, FCLRules.an1, FCLRules.c_an2, FCLRules.an2
), True, False, None, -1

AN3_1 = 4, (
    FCLTokens.identifier, FCLRules.c_an3, FCLTokens.is_tok, FCLRules.ter
), True, False, None, -1

AN3_2 = 3, (FCLTokens.lbrac, FCLRules.an, FCLTokens.rbrac), True, False, None, -1

AN3_3 = 3, (FCLTokens.not_tok, FCLRules.an, FCLRules.c_an33), True, False, None, -1

AN4_1 = 0, None, True, False, None, -1

AN4_2 = 4, (FCLTokens.and_tok, FCLRules.an3, FCLRules.c_an4, FCLRules.c_an33), True, False, None, -1

C_AN3 = 0, None, True, False, add_in_var, -1

C_AN33 = 0, None, True, False, add_in_not, -1

C_AN2 = 0, None, True, False, add_in_or, -1

C_AN4 = 0, None, True, False, add_in_and, -1

TER = 2, (FCLRules.ter1, FCLRules.ter2), True, False, None, -1

TER1 = 2, (FCLRules.ter3, FCLRules.ter4), True, False, None, -1

TER2_1 = 0, None, True, False, None, -1

TER2_2 = 0, (FCLTokens.or_tok, FCLRules.ter1, FCLRules.c_ter2, FCLRules.ter2), True, False, None, -1

C_TER2 = 0, None, True, False, add_ter_or, -1

TER3_1 = 2, (FCLTokens.identifier, FCLRules.c_ter31), True, False, None, -1

C_TER31 = 0, None, True, False, add_term, -1

TER3_2 = 3, (FCLTokens.lbrac, FCLRules.ter, FCLTokens.rbrac), True, False, None, -1

TER3_3 = 3, (FCLTokens.not_tok, FCLRules.ter, FCLRules.c_ter33), True, False, None, -1

TER3_4 = 3, (FCLTokens.con, FCLRules.ter, FCLRules.c_ter34), True, False, None, -1

TER3_5 = 3, (FCLTokens.dil, FCLRules.ter, FCLRules.c_ter35), True, False, None, -1

TER4_1 = 0, None, True, False, None, -1

TER4_2 = 4, (FCLTokens.and_tok, FCLRules.ter3, FCLRules.c_ter4, FCLRules.ter4), True, False, None, -1

C_TER33 = 0, None, True, False, add_term_not, -1

C_TER34 = 0, None, True, False, add_term_con, -1

C_TER35 = 0, None, True, False, add_term_dil, -1

C_TER4 = 0, None, True, False, add_term_and, -1

CN = 4, (FCLTokens.identifier, FCLRules.c_cn, FCLTokens.is_tok, FCLRules.ter), True, False, None, -1

C_CN = 0, None, True, False, add_out_var, -1

C_RL2 = 0, None, True, False, set_rule_name, -1

FC_FZME = 0, None, False, False, bad_fuzzify, -1

FC_DFME = 0, None, False, False, bad_defuzzify, -1

FC_OPBE = 0, None, False, False, bad_oper_base, -1
