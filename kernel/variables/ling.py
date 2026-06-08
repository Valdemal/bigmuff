from typing import Optional, List

from .custom import CustomVariable
from ..consts import Crisp
from ..enums import FuzzifyMethod, DefuzzifyMethod, ValueType, OperationCode
from ..fuzzification import SingletonFuzzification
from ..fuzzy_set import TFuzzySet
from ..member_func import RESULT_FUNC
from ..mixins import OperationBased
from ..operation import OperationBase


class LingVariable(CustomVariable, OperationBased):
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
        if a_fmethod is None:
            a_fmethod = SingletonFuzzification(a_inf, a_sup)

        CustomVariable.__init__(self, name,a_inf, a_sup, a_fmethod, a_dfmethod)
        OperationBased.__init__(self, a_ops)
        self._terms: List[TFuzzySet] = []
        self.value_type = ValueType.valLinguistic

    @property
    def terms(self) -> List[TFuzzySet]:
        return self._terms


    def _set_ops(self, value):
        super()._set_ops(value)
        for t in self._terms:
            t.ops = value

    def _set_inf(self, value):
        super()._set_inf(value)
        for t in self._terms:
            t.func.inf = value

    def _set_sup(self, value):
        super()._set_sup(value)
        for t in self._terms:
            t.func.sup = value

    def defuzzificate(self, value: TFuzzySet) -> Crisp:
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
