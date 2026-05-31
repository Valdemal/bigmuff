from typing import Optional, List

from .custom import TCustomVariable
from ..consts import Crisp, Natural
from ..enums import FuzzifyMethod, DefuzzifyMethod, ValueType, OperationCode
from ..exceptions import ELingVariable, NFE_INVALID_BASE, NFE_INVALID_INDEX, NFE_INVALID_BASE_SET
from ..fuzzy_set import TFuzzySet
from ..member_func import RESULT_FUNC
from ..operation import OperationBase


class TLingVariable(TCustomVariable):
    """
    Лингвистическая переменная
    """

    def __init__(self, name: str, a_inf: Crisp, a_sup: Crisp,
                 a_ops: OperationBase,
                 a_fmethod: Optional[FuzzifyMethod] = None,
                 a_dfmethod: Optional[DefuzzifyMethod] = None):
        """
        Конструктор лингвистической переменной

        Args:
            name: имя переменной
            a_inf: нижняя граница
            a_sup: верхняя граница
            a_ops: набор базовых операций
            a_fmethod: метод фаззификации
            a_dfmethod: метод дефаззификации
        """
        if a_fmethod is not None and a_dfmethod is not None:
            super().__init__(name, a_fmethod, a_dfmethod)
        else:
            super().__init__(name)

        if a_inf >= a_sup:
            raise ELingVariable("", NFE_INVALID_BASE)

        self._inf_base = a_inf
        self._sup_base = a_sup
        self._operation = a_ops
        self._terms: List[TFuzzySet] = []
        self.value_type = ValueType.valLinguistic

    @property
    def terms(self) -> List[TFuzzySet]:
        return self._terms

    @property
    def ops(self) -> Optional[OperationBase]:
        return self._operation

    @ops.setter
    def ops(self, value: OperationBase):
        for t in self._terms:
            t.ops = value
        self._operation = value

    @property
    def inf(self) -> Crisp:
        """Получить нижнюю границу"""
        return self._inf_base

    @inf.setter
    def inf(self, value: Crisp):
        """Установить нижнюю границу"""
        if value >= self._sup_base:
            raise ELingVariable("", NFE_INVALID_BASE)

        self._inf_base = value
        for t in self._terms:
            t.func.inf = value

    @property
    def sup(self) -> Crisp:
        """Получить верхнюю границу"""
        return self._sup_base

    @sup.setter
    def sup(self, value: Crisp):
        """Установить верхнюю границу"""
        if self._inf_base >= value:
            raise ELingVariable("", NFE_INVALID_BASE)

        self._sup_base = value
        for t in self._terms:
            t.func.sup = value

    def set_term(self, index: Natural, value: TFuzzySet):
        """
        Установить терм по индексу

        Args:
            index: индекс терма
            value: новое значение терма
        """
        if index < len(self._terms):
            self._terms[index] = value
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

        self._terms.append(fv)
        fv.ops = self._operation

    def del_term(self, index: Natural):
        """
        Удалить терм по индексу

        Args:
            index: индекс удаляемого терма
        """
        if index < len(self._terms):
            del self._terms[index]
        else:
            raise ELingVariable("", NFE_INVALID_INDEX)

    def sort_terms(self):
        """
        Упорядочивание термов по центру площади (COA)
        """
        n = len(self._terms)
        for i in range(n - 2, -1, -1):
            swapped = False
            for j in range(i + 1):
                coa_j = self._terms[j].func.coa(self._terms[j].ops.points)
                coa_j1 = self._terms[j + 1].func.coa(self._terms[j + 1].ops.points)

                if coa_j > coa_j1:
                    self._terms[j], self._terms[j + 1] = self._terms[j + 1], self._terms[j]
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
        return self._terms[0].fuzzificate(crisp, self._fuzzify)

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
        for t in self._terms:
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
        for i, t in enumerate(self._terms):
            if t.name == value:
                return i
        return -1

    def value(self, revform: List[int]) -> TFuzzySet:
        """
        Получение композитного значения нечеткой переменной
        Выражение записывается в обратной польской записи

        Args:
            revform: выражение в обратной польской записи

        Returns:
            результат вычисления
        """
        res: List[TFuzzySet] = []

        i = 0
        while i < len(revform):
            opcode = revform[i]
            i += 1

            match opcode:
                case OperationCode.ocValue:
                    val = revform[i]
                    i += 1

                    if val >= len(self._terms):
                        raise Exception("неверный индекс терма ЛП")

                    op = self._terms[val]
                    res.append(TFuzzySet(
                        op.name,
                        RESULT_FUNC(op.func, op.ops.points)
                    ))

                case OperationCode.ocNot:
                    if not res:
                        raise Exception("недостаточно операндов")

                    res.append(~res.pop())

                case OperationCode.ocVery:
                    if not res:
                        raise Exception("недостаточно операндов")

                    res.append(res.pop().con())

                case OperationCode.ocAverage:
                    if not res:
                        raise Exception("недостаточно операндов")

                    res.append(res.pop().dil())

                case OperationCode.ocAnd:
                    if len(res) < 2:
                        raise Exception("недостаточно операндов")
                    op2 = res.pop()
                    op1 = res.pop()
                    res.append(op1 & op2)

                case OperationCode.ocOr:
                    if len(res) < 2:
                        raise Exception("недостаточно операндов")
                    op2 = res.pop()
                    op1 = res.pop()
                    res.append(op1 | op2)

                case _:
                    raise Exception(f"неверный оператор: {opcode}")

        if len(res) != 1:
            raise Exception("неполное выражение")

        return res[0]
