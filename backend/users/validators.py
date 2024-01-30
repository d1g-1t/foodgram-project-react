import re


def username_validator(username):
    """
    Проверяет, соответствует ли заданное имя пользователя указанному шаблону.

    Аргументы:
    username (str): Имя пользователя для проверки.

    Возвращает:
    bool: True, если имя пользователя соответствует шаблону
    и не равно 'me'.
    """
    pattern = r'^[\w.@+-]+$'
    if re.match(pattern, username) and username != 'me':
        return True
    else:
        raise ValueError(
            "Имя пользователя не может быть 'me'"
            " или содержать запрещенные символы."
        )


def color_validator(color):
    """
    Валидатор для проверки добавления цвета тега в формате HEX.

    Аргументы:
    color (str): Цвет для проверки.

    Возвращает:
    bool: True, если цвет соответствует формату HEX.
    """
    pattern = r'^#([A-Fa-f0-9]{6}|[A-Fa-f0-9]{3})$'
    if re.match(pattern, color):
        return True
    else:
        raise ValueError(
            "Цвет должен быть в формате HEX."
        )
