"""
Модуль для обработки ошибок нейро-нечеткой системы
"""


# Коды ошибок
NF_ERROR_BASE = 100
NFE_DOM_INVALID = NF_ERROR_BASE
NFE_OUT_OF_DOMAIN = NF_ERROR_BASE + 1
NFE_NOT_POINTS = NF_ERROR_BASE + 2
NFE_INVALID_BASE = NF_ERROR_BASE + 3
NFE_INVALID_INDEX = NF_ERROR_BASE + 4
NFE_INVALID_POINTS = NF_ERROR_BASE + 5
NFE_INVALID_MEMBER_FUNC = NF_ERROR_BASE + 6
NFE_INVALID_BASE_SET = NF_ERROR_BASE + 7
NFE_INVALID_TERM_INDEX = NF_ERROR_BASE + 8
NFE_INVALID_CERT_VALUE = NF_ERROR_BASE + 9
NFE_ERROR_MEMORY = NF_ERROR_BASE + 10
NFE_INVALID_INPUTS = NF_ERROR_BASE + 11
NFE_INVALID_FUZZIFY_METHOD = NF_ERROR_BASE + 12
NFE_INVALID_DEFUZZIFY_METHOD = NF_ERROR_BASE + 13
NFE_INVALID_EXPRESSION = NF_ERROR_BASE + 14
NFE_VAR_USED = NF_ERROR_BASE + 15
NFE_TERM_USED = NF_ERROR_BASE + 16

FCL_DONE = 999
FCL_ERROR_BASE = 1000
FCLE_INVALID_SYMBOL = FCL_ERROR_BASE
FCLE_UNFINISHED_COMMENT = FCL_ERROR_BASE + 1
FCLE_UNFINISHED_STRING = FCL_ERROR_BASE + 2
FCLE_END_COM_WO_BEGIN = FCL_ERROR_BASE + 3
FCLE_SYNTAX = FCL_ERROR_BASE + 4
FCLE_TOKEN_EXPECTED = FCL_ERROR_BASE + 5
FCLE_UNEXPECTED_END = FCL_ERROR_BASE + 6
FCLE_SYNTAX_ERROR = FCL_ERROR_BASE + 7
FCLE_UNKNOWN_IDENT = FCL_ERROR_BASE + 8
FCLE_NEED_INTEGER = FCL_ERROR_BASE + 9
FCLE_IDENTIFIER_EXPECTED = FCL_ERROR_BASE + 10
FCLE_STRING_EXPECTED = FCL_ERROR_BASE + 11
FCLE_NUMBER_EXPECTED = FCL_ERROR_BASE + 12
FCLE_EOF_EXPECTED = FCL_ERROR_BASE + 13
FCLE_UNKNOWN_TERM = FCL_ERROR_BASE + 14
FCLE_SEMANTICS_ERROR = FCL_ERROR_BASE + 15
FCLE_INVALID_FUZ_METHOD = FCL_ERROR_BASE + 16
FCLE_INVALID_DEFUZ_METHOD = FCL_ERROR_BASE + 17
FCLE_INVALID_OPERBASE = FCL_ERROR_BASE + 18

# Сообщения об ошибках ядра
kernel_error_messages = [
    "Значение функции принадлежности не принадлежит отрезку [0,1]",
    "Выход за область определения функции принадлежности",
    "Недостаточное количество точек функции принадлежности",
    "Неверное базовое множество нечеткого подмножества",
    "Неверный индекс, выход за границы массива",
    "Опорные точки функции принадлежности не упорядочены",
    "Неверная функция принадлежности",
    "Базовые множества нечетких подмножеств не совпадают",
    "Неверный индекс терма лингвистической переменной",
    "Неверное значение степени доверия правила",
    "Ошибка при распределении памяти",
    "Число входных нечетких переменных не соответствует правилу",
    "Не определен метод фаззификации",
    "Не определен метод дефаззификации",
    "Неверное выражение для получения значения переменной",
    "Входная переменная используется",
    "Терм нечеткой переменной используется"
]

# Сообщения об ошибках FCL
fcl_error_messages = [
    "Недопустимый символ",
    "Незавершенный многострочный комментарий",
    "Незавершенная строковая константа",
    "Достигнуто завершение многострочного комментария, но начало не определено",
    "Синтаксическая ошибка: неверный идентификатор",
    "Отсутствует ",
    "Неожиданный конец файла: ожидается ",
    "Ошибка синтаксиса FCL",
    "Неизвестный идентификатор ",
    "Требуется только целое число",
    "Ожидается идентификатор",
    "Ожидается строковая константа",
    "Ожидается числовая константа",
    "Ожидается конец файла",
    "Неизвестное имя терма ",
    "Семантическая ошибка: ",
    "Неверное имя метода фаззификации",
    "Неверное имя метода дефаззификации",
    "Неверное имя базиса операций"
]


class EErrorBase(Exception):
    """
    Базовый класс ошибки
    """

    def __init__(self, msg: str, code: int):
        """
        Конструктор базового класса ошибки

        Args:
            msg: сообщение об ошибке
            code: код ошибки
        """
        super().__init__(msg)
        self._error_code = code

    @property
    def error_code(self) -> int:
        """Получить код ошибки"""
        return self._error_code


class EKernelError(EErrorBase):
    """
    Базовый класс ошибок ядра
    """

    def __init__(self, msg: str, code: int):
        """
        Конструктор ошибки ядра

        Args:
            msg: сообщение об ошибке
            code: код ошибки
        """
        error_index = code - NF_ERROR_BASE
        if 0 <= error_index < len(kernel_error_messages):
            error_text = kernel_error_messages[error_index]
        else:
            error_text = "Неизвестная ошибка"

        full_msg = f"KERNEL{code}: {msg}{error_text}."
        super().__init__(full_msg, code)


class EMemberFunc(EKernelError):
    """
    Ошибки при работе с функцией принадлежности
    """

    def __init__(self, msg: str, code: int):
        """
        Конструктор ошибки функции принадлежности

        Args:
            msg: сообщение об ошибке
            code: код ошибки
        """
        super().__init__(f"Ошибка функции принадлежности ({msg}): ", code)


class EFuzzySet(EKernelError):
    """
    Ошибки при работе с нечетким множеством
    """

    def __init__(self, msg: str, code: int):
        """
        Конструктор ошибки нечеткого множества

        Args:
            msg: сообщение об ошибке
            code: код ошибки
        """
        super().__init__(f"Ошибка нечеткого множества ({msg}): ", code)


class EFuzzyVariable(EKernelError):
    """
    Ошибки при работе с нечеткой переменной
    """

    def __init__(self, msg: str, code: int):
        """
        Конструктор ошибки нечеткой переменной

        Args:
            msg: сообщение об ошибке
            code: код ошибки
        """
        super().__init__(f"Ошибка нечеткой переменной ({msg}): ", code)


class ELingVariable(EKernelError):
    """
    Ошибки при работе с лингвистической переменной
    """

    def __init__(self, msg: str, code: int):
        """
        Конструктор ошибки лингвистической переменной

        Args:
            msg: сообщение об ошибке
            code: код ошибки
        """
        super().__init__(f"Ошибка лингвистической переменной ({msg}): ", code)


class ESimpleRule(EKernelError):
    """
    Ошибки при работе с простым правилом
    """

    def __init__(self, msg: str, code: int):
        """
        Конструктор ошибки простого правила

        Args:
            msg: сообщение об ошибке
            code: код ошибки
        """
        super().__init__(f"Ошибка простого правила ({msg}): ", code)


class ECompositeRule(EKernelError):
    """
    Ошибки при работе с составным правилом
    """

    def __init__(self, msg: str, code: int):
        """
        Конструктор ошибки составного правила

        Args:
            msg: сообщение об ошибке
            code: код ошибки
        """
        super().__init__(f"Ошибка составного правила ({msg}): ", code)


class EFuzzyModel(EKernelError):
    """
    Ошибки при работе с блоком правил
    """

    def __init__(self, msg: str, code: int):
        """
        Конструктор ошибки блока правил

        Args:
            msg: сообщение об ошибке
            code: код ошибки
        """
        super().__init__(f"Ошибка блока правил ({msg}): ", code)


class ESyntaxError(EErrorBase):
    """
    Ошибки при работе с FCL файлами
    """

    def __init__(self, file_name: str, msg: str, code: int,
                 str_num: int, chr_num: int):
        """
        Конструктор синтаксической ошибки FCL

        Args:
            file_name: имя файла
            msg: сообщение об ошибке
            code: код ошибки
            str_num: номер строки
            chr_num: номер символа в строке
        """
        error_index = code - FCL_ERROR_BASE
        if 0 <= error_index < len(fcl_error_messages):
            error_text = fcl_error_messages[error_index]
        else:
            error_text = "Неизвестная ошибка FCL"

        full_msg = (f"[ошибка FCL] {file_name}({str_num},{chr_num}): "
                    f"E{code} {error_text}{msg}.")
        super().__init__(full_msg, code)
        self._str_num = str_num
        self._chr_num = chr_num

    @property
    def str_num(self) -> int:
        """Получить номер строки"""
        return self._str_num

    @property
    def chr_num(self) -> int:
        """Получить номер символа в строке"""
        return self._chr_num


def format_kernel_error_msg(code: int) -> str:
    """
    Получить текст сообщения об ошибке ядра по коду

    Args:
        code: код ошибки

    Returns:
        текст сообщения
    """
    error_index = code - NF_ERROR_BASE
    if 0 <= error_index < len(kernel_error_messages):
        return kernel_error_messages[error_index]
    return "Неизвестная ошибка ядра"


def format_fcl_error_msg(code: int) -> str:
    """
    Получить текст сообщения об ошибке FCL по коду

    Args:
        code: код ошибки

    Returns:
        текст сообщения
    """
    error_index = code - FCL_ERROR_BASE
    if 0 <= error_index < len(fcl_error_messages):
        return fcl_error_messages[error_index]
    return "Неизвестная ошибка FCL"


# Словарь для быстрого получения классов ошибок по коду
error_classes = {
    **{code: EMemberFunc for code in range(NFE_DOM_INVALID, NFE_TERM_USED + 1)},
    **{code: ESyntaxError for code in range(FCLE_INVALID_SYMBOL, FCLE_INVALID_OPERBASE + 1)}
}
