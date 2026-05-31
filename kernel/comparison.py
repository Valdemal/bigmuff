from kernel.consts import EPSILON


def eq(x: float, y: float) -> bool:
    """Приблизительное равенство"""
    return abs(x - y) < EPSILON

def ls(x: float, y: float) -> bool:
    """Строго меньше (с учетом погрешности)"""
    return x - y < -EPSILON

def gt(x: float, y: float) -> bool:
    """Строго больше (с учетом погрешности)"""
    return x - y > EPSILON

def le(x: float, y: float) -> bool:
    """Меньше или равно (с учетом погрешности)"""
    return x - y < EPSILON

def ge(x: float, y: float) -> bool:
    """Больше или равно (с учетом погрешности)"""
    return x - y > -EPSILON

def inrange(x: float, a: float, b: float) -> bool:
    """Проверка нахождения в диапазоне [a, b]"""
    return ge(x, a) and le(x, b)
