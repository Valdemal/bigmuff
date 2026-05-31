from kernel.enums import MemberFuncType

EPSILON = 1E-3
DELTA_AMOUNT = 0.1                  # Степень нечеткости при фаззификации в % / 100
CRISP_AMOUNT = 0.02                  # Степень абсолютной принадлежности при фаззификации в % / 100


# Типы данных
Membership = float  # Тип значений степени принадлежности
Crisp = float     # Тип значений базового множества
Natural = int       # Беззнаковый тип индекса и размера массивов