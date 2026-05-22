import sys
from typing import Optional, List

from .custom import TCustomVariable
from ..consts import BaseSet, Natural
from ..enums import FuzzifyMethod, DefuzzifyMethod, ValueType, OperationCode, VariableType
from ..exceptions import ELingVariable, NFE_INVALID_BASE, NFE_INVALID_INDEX, NFE_INVALID_BASE_SET, \
    NFE_INVALID_EXPRESSION
from ..fuzzy_set import TFuzzySet
from ..base import GE, LS
from ..member_func import RESULT_FUNC
from ..operation import TOperationBase


class TLingVariable(TCustomVariable):
    """
    Лингвистическая переменная
    """

    def __init__(self, a_name: str, a_inf: BaseSet, a_sup: BaseSet,
                 a_ops: TOperationBase,
                 a_fmethod: Optional[FuzzifyMethod] = None,
                 a_dfmethod: Optional[DefuzzifyMethod] = None):
        """
        Конструктор лингвистической переменной

        Args:
            a_name: имя переменной
            a_inf: нижняя граница
            a_sup: верхняя граница
            a_ops: набор базовых операций
            a_fmethod: метод фаззификации
            a_dfmethod: метод дефаззификации
        """
        if a_fmethod is not None and a_dfmethod is not None:
            super().__init__(a_name, a_fmethod, a_dfmethod)
        else:
            super().__init__(a_name)

        if GE(a_inf, a_sup):
            raise ELingVariable("", NFE_INVALID_BASE)

        self._inf_base = a_inf
        self._sup_base = a_sup
        self._operation = a_ops
        self._term: List[TFuzzySet] = []
        self.value_type = ValueType.valLinguistic

    @property
    def term(self):
        return self._term

    @property
    def ops(self) -> Optional[TOperationBase]:
        return self._operation

    @ops.setter
    def ops(self, value: TOperationBase):
        for t in self._term:
            t.ops = value
        self._operation = value

    def __del__(self):
        """Деструктор"""
        self._term.clear()

    @property
    def inf(self) -> BaseSet:
        """Получить нижнюю границу"""
        return self._inf_base

    @inf.setter
    def inf(self, value: BaseSet):
        """Установить нижнюю границу"""
        if LS(value, self._sup_base):
            self._inf_base = value
            for t in self._term:
                t.func.inf = value
        else:
            raise ELingVariable("", NFE_INVALID_BASE)

    @property
    def sup(self) -> BaseSet:
        """Получить верхнюю границу"""
        return self._sup_base

    @sup.setter
    def sup(self, value: BaseSet):
        """Установить верхнюю границу"""
        if LS(self._inf_base, value):
            self._sup_base = value
            for t in self._term:
                t.func.sup = value
        else:
            raise ELingVariable("", NFE_INVALID_BASE)

    def get_term(self, index: Natural) -> TFuzzySet:
        """
        Получить терм по индексу

        Args:
            index: индекс терма

        Returns:
            терм
        """
        if index < len(self._term):
            return self._term[index]
        else:
            raise ELingVariable("", NFE_INVALID_INDEX)

    def set_term(self, index: Natural, value: TFuzzySet):
        """
        Установить терм по индексу

        Args:
            index: индекс терма
            value: новое значение терма
        """
        if index < len(self._term):
            self._term[index] = value
            value.ops = self._operation
        else:
            raise ELingVariable("", NFE_INVALID_INDEX)

    def add_term(self, fv: TFuzzySet):
        """
        Добавить терм

        Args:
            fv: терм для добавления
        """
        if (fv.func.inf != self._inf_base) or (fv.func.sup != self._sup_base):
            raise ELingVariable("", NFE_INVALID_BASE_SET)

        self._term.append(fv)
        fv.ops = self._operation

    def del_term(self, index: Natural):
        """
        Удалить терм по индексу

        Args:
            index: индекс удаляемого терма
        """
        if index < len(self._term):
            del self._term[index]
        else:
            raise ELingVariable("", NFE_INVALID_INDEX)

    def sort_terms(self):
        """
        Упорядочивание термов по центру площади (COA)
        """
        n = len(self._term)
        for i in range(n - 2, -1, -1):
            swapped = False
            for j in range(i + 1):
                coa_j = self._term[j].func.coa(self._term[j].ops.points)
                coa_j1 = self._term[j + 1].func.coa(self._term[j + 1].ops.points)

                if coa_j > coa_j1:
                    self._term[j], self._term[j + 1] = self._term[j + 1], self._term[j]
                    swapped = True

            if not swapped:
                break

    def _internal_fuzzificate(self, crisp: float) -> TFuzzySet:
        """
        Внутренняя фаззификация

        Args:
            crisp: четкое значение

        Returns:
            нечеткое множество
        """
        if self._term:
            return self._term[0].fuzzificate(crisp, self._fuzzify)

    def _internal_defuzzificate(self, value: Optional[TFuzzySet]) -> float:
        """
        Внутренняя дефаззификация

        Args:
            value: нечеткое множество

        Returns:
            четкое значение
        """
        if value is not None:
            return value.defuzzificate(self._defuzzify)
        return float('-inf')


    def is_value_exists(self, value: str) -> bool:
        """
        Проверить существование значения

        Args:
            value: имя значения

        Returns:
            True если значение существует
        """
        for t in self._term:
            if t.name == value:
                return True
        return False

    def is_term_exists(self, value: str) -> int:
        """
        Проверить существование терма

        Args:
            value: имя терма

        Returns:
            индекс терма или -1 если не найден
        """
        for i, t in enumerate(self._term):
            if t.name == value:
                return i
        return -1

    def value(self, revform: List[int]) -> Optional[TFuzzySet]:
        """
        Получение композитного значения нечеткой переменной
        Выражение записывается в обратной польской записи

        Args:
            revform: выражение в обратной польской записи

        Returns:
            результат вычисления
        """
        res: List[TFuzzySet] = []

        # try:
        i = 0
        while i < len(revform):
            opcode = revform[i]
            i += 1

            if opcode == OperationCode.ocValue:
                val = revform[i]
                i += 1

                if val >= len(self._term):
                    raise Exception("неверный индекс терма ЛП")

                op = self._term[val]
                res.append(TFuzzySet(
                    op.name,
                    RESULT_FUNC(op.func.inf, op.func.sup, op.ops.points),
                    op.ops
                ))

            elif opcode == OperationCode.ocNot:
                if not res:
                    raise Exception("недостаточно операндов")
                op = res.pop()
                res.append(~op)

            elif opcode == OperationCode.ocVery:
                if not res:
                    raise Exception("недостаточно операндов")
                op = res.pop()
                res.append(op.con())

            elif opcode == OperationCode.ocAverage:
                if not res:
                    raise Exception("недостаточно операндов")
                op = res.pop()
                res.append(op.dil())

            elif opcode == OperationCode.ocAnd:
                if len(res) < 2:
                    raise Exception("недостаточно операндов")
                op2 = res.pop()
                op1 = res.pop()
                res.append(op1 & op2)

            elif opcode == OperationCode.ocOr:
                if len(res) < 2:
                    raise Exception("недостаточно операндов")
                op2 = res.pop()
                op1 = res.pop()
                res.append(op1 | op2)

            else:
                raise Exception(f"неверный оператор: {opcode}")

        if len(res) != 1:
            raise Exception("неполное выражение")

        return res[0]

        # except Exception as e:
        #     raise ELingVariable(str(e), NFE_INVALID_EXPRESSION)

    # def __str__(self) -> str:
    #     """
    #     Выгрузка переменной в FCL файл
    #
    #     Returns:
    #         строка в формате FCL
    #     """
    #     result = ""
    #
    #     if self.type == VariableType.vtInput:
    #         result += f"{FuzzifyToken[0]} {self.name}\n"
    #         result += f"{IdentToken}{MethodToken}: {FuzzifyMethodName.get(self.fuzzify, 'UNKNOWN')} ;\n"
    #         result += f"{IdentToken}"
    #
    #         if self.units:
    #             result += f"{UnitsToken}: \"{self.units}\" ;\n{IdentToken}"
    #
    #         result += f"{RangeToken} := ({self._inf_base} .. {self._sup_base}) ;\n"
    #
    #         for t in self._term:
    #             result += f"{IdentToken}{t}\n"
    #
    #         result += FuzzifyToken[1]
    #
    #     elif self.type == VariableType.vtOutput:
    #         result += f"{DeFuzzifyToken[0]} {self.name}\n"
    #         result += f"{IdentToken}{MethodToken}: {DeFuzzifyMethodName.get(self.defuzzify, 'UNKNOWN')} ;\n"
    #         result += f"{IdentToken}"
    #
    #         if self.units:
    #             result += f"{UnitsToken}: \"{self.units}\" ;\n{IdentToken}"
    #
    #         result += f"{RangeToken} := ({self._inf_base} .. {self._sup_base}) ;\n"
    #
    #         for t in self._term:
    #             result += f"{IdentToken}{t}\n"
    #
    #         result += DeFuzzifyToken[1]
    #
    #     elif self.type == VariableType.vtIntermediate:
    #         result += f"{IntermediateToken[0]} {self.name}\n"
    #         result += f"{IdentToken}"
    #
    #         if self.units:
    #             result += f"{UnitsToken}: \"{self.units}\" ;\n{IdentToken}"
    #
    #         result += f"{RangeToken} := ({self._inf_base} .. {self._sup_base}) ;\n"
    #
    #         for t in self._term:
    #             result += f"{IdentToken}{t}\n"
    #
    #         result += IntermediateToken[1]
    #
    #     return result

    def to_fcl(self, out=sys.stdout):
        """Выгрузка переменной в FCL файл"""
        out.write(str(self))


# Для удобства создаем функции-фабрики
def create_input_variable(name: str, inf: BaseSet, sup: BaseSet,
                          fuzzify: FuzzifyMethod, ops: TOperationBase) -> TLingVariable:
    """
    Создание входной лингвистической переменной

    Args:
        name: имя переменной
        inf: нижняя граница
        sup: верхняя граница
        fuzzify: метод фаззификации
        ops: набор операций

    Returns:
        лингвистическая переменная
    """
    var = TLingVariable(name, inf, sup, ops, fuzzify, DefuzzifyMethod.dmCOG)
    var.type = VariableType.vtInput
    return var


def create_output_variable(name: str, inf: BaseSet, sup: BaseSet,
                           defuzzify: DefuzzifyMethod, ops: TOperationBase) -> TLingVariable:
    """
    Создание выходной лингвистической переменной

    Args:
        name: имя переменной
        inf: нижняя граница
        sup: верхняя граница
        defuzzify: метод дефаззификации
        ops: набор операций

    Returns:
        лингвистическая переменная
    """
    var = TLingVariable(name, inf, sup, ops, FuzzifyMethod.fmTriangle, defuzzify)
    var.type = VariableType.vtOutput
    return var


def create_intermediate_variable(name: str, inf: BaseSet, sup: BaseSet,
                                 ops: TOperationBase) -> TLingVariable:
    """
    Создание промежуточной лингвистической переменной

    Args:
        name: имя переменной
        inf: нижняя граница
        sup: верхняя граница
        ops: набор операций

    Returns:
        лингвистическая переменная
    """
    var = TLingVariable(name, inf, sup, ops)
    var.type = VariableType.vtIntermediate
    return var