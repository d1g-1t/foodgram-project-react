import re

USERNAME_PATTERN = r'^[\w.@+-]+$'

def username_validator(username):
    """
    Проверяет, соответствует ли заданное имя пользователя указанному шаблону.

    Аргументы:
    username (str): Имя пользователя для проверки.

    Возвращает:
    bool: True, если имя пользователя соответствует шаблону
    и не равно 'me'.
    """
    if re.match(USERNAME_PATTERN, username) and username != 'me':
        return True
    else:
        raise ValueError(
            "Имя пользователя не может быть 'me'"
            " или содержать запрещенные символы."
        )
