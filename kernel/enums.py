from enum import Enum, IntEnum


class MemberFuncType(Enum):
    """Тип функции принадлежности нечеткого множества"""
    mfNA = 0
    mfSingleton = 1
    mfLinear = 2
    mfSmooth = 3
    mfLnVector = 4


class VariableType(Enum):
    """Тип переменной"""
    vtNA = 0
    vtInput = 1
    vtOutput = 2
    vtIntermediate = 3


class ValueType(Enum):
    """Тип значения переменной"""
    valNA = 0
    valFuzzy = 1
    valLinguistic = 2
    valCategorical = 3


class FuzzifyMethod(Enum):
    """Метод фаззификации"""
    fmNA = 0
    fmTriangle = 1
    fmTrapezoid = 2
    fmSingleton = 3
    fmSmoothTri = 4
    fmSmoothTrap = 5


class DefuzzifyMethod(Enum):
    """Метод дефаззификации"""
    dmNA = 0
    dmCOG = 1  # Center of Gravity
    dmCOA = 2  # Center of Area
    dmLM = 3  # Left Most Maximum
    dmRM = 4  # Right Most Maximum
    dmMOM = 5  # Mean of Maximums


class OperationCode(IntEnum):
    """Коды операций над термами"""
    ocValue = 10000
    ocNot = 10001
    ocAnd = 10002
    ocOr = 10003
    ocVery = 10004
    ocAverage = 10005
