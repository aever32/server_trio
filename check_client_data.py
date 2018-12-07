import re


# Проверка блока регистрации
async def clean_registration(data: dict) -> dict:
    # проверка email по шаблону
    # шаблон Email
    pattern_email = re.compile('(^|\s)[-a-z0-9_.]+@([-a-z0-9]+\.)+[a-z]{2,6}(\s|$)')
    # Полученное с клиента значение
    address = data['email']
    # результат проверки
    is_address_valid = pattern_email.match(address)
    if is_address_valid:
        # Минимум 3 символа, максимум 30
        # Разрешены латинские буквы и числа, обязательно первой должна быть буква.
        pattern_nickname = re.compile('^[a-zA-Z][a-zA-Z0-9]{2,30}$')
        nickname = data['nickname']
        is_nickname_valid = pattern_nickname.match(nickname)
        if is_nickname_valid:
            # Минимум 6 символов, максимум 30 из них хотя бы
            # (одно число, один спецсимвол, одна латинская буква в нижнем регистре и в верхнем)
            pattern_password = re.compile('^(?=.*[a-z])(?=.*[A-Z])(?=.*[0-9])(?=.*[^\w]).{6,30}')
            password = data['password']
            is_password_valid = pattern_password.match(password)
            if is_password_valid:
                return {'result': 'true'}
            else:
                return {'result': 'false', 'password': 'failed'}
        else:
            return {'result': 'false', 'nickname': 'failed'}
    else:
        return {'result': 'false', 'email': 'failed'}


# Проверка блока аутентификации
async def clean_login(data: dict) -> dict:
    return {'result': 'true'}


# Проверка блока действий
async def clean_action(data: dict) -> dict:
    # Сверка данных токена от пользователя с глобальным словарем токенов сервера
    if data['token'] == TOKENS.get(data['id']):
        return {'result': 'true'}
    else:
        return {'result': 'false'}
