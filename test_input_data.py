# test_input_data.py / from test_input_data import *
import re


# Проверка блока регистрации !!!!! ДОЛЖНА БЫТЬ В ПОСЛЕДСТВИИ ВЫНЕСЕНА В ОТДЕЛЬНЫЙ ФАЙЛ
async def clean_registration(server_stream, data: dict) -> dict:
    # проверка email по шаблону
    # шаблон Email
    pattern_Em = re.compile('(^|\s)([-a-z0-9_.]+@([-a-z0-9]+\.)+[a-z]{2,6}){,50}(\s|$)')
    # Полученное с клиента значение
    address = data['email']

    # результат проверки
    is_valid = pattern_Em.match(address)

    # действие по результатам проверки
    if not is_valid:  #если данные не прошли проверку
        # действие при неправильно введённых данных
        print('неправильный email:', is_valid.group())
        return {'flag': 'false', 'result': 'email failed'}
        result = {'flag': 'false', 'result': 'email failed'}
        await send_json_to_client(server_stream, result)

    else:
        # действие при правильно введённых данных
        print('email! введён правильно\n')
        result = {'flag': 'true', 'result': 'email OK'}
        await send_json_to_client(server_stream, result)

        # проверка пароля
        # https://habr.com/post/115825/
        pattern_Ad = re.compile('^.*(?=.{6,30})(?=.*\d)(?=.*[a-z])(?=.*[A-Z])(?=.*[@#$%^&+=]).*$')#здесь должен быть шаблон пароля
        password = data['password']
        is_valid = pattern_Ad.match(password)

        if not is_valid:  # если данные не прошли проверку
            # действие при неправильно введённых данных
            print('неправильно введён пароль:', is_valid.group())
            return {'flag': 'false', 'result': 'password failed'}
            result = {'flag': 'false', 'result': 'password failed'}
            await send_json_to_client(server_stream, result)

        else:
            # действие при правильно введённых данных
            print('password введён правильно\n')
            result = {'flag': 'true', 'result': 'password OK'}
            await send_json_to_client(server_stream, result)

            # проверка имени
            pattern_Ni = re.compile('^.*(?=.{3,20})(?=.*\d)(?=.*[a-z])(?=.*[A-Z])(?=.*[@#$%^&+=]).*$')#здесь должен быть шаблон имени
            nickname = data['nickname']
            is_valid = pattern_Ni.match(nickname)
            if not is_valid:  # если данные не прошли проверку
                # действие при неправильно введённых данных
                print('неправильно введён пароль:', is_valid.group())
                return {'flag': 'false', 'result': 'nickname failed'}
                result = {'flag': 'false', 'result': 'nickname failed'}
                await send_json_to_client(server_stream, result)

            else:
                # действие при правильно введённых данных
                print('nickname введён правильно\n')
                result = {'flag': 'true', 'result': 'nickname OK'}
                await send_json_to_client(server_stream, result)

        # FIXME Тут придется всю логику снова переписывать под параметр server_stream,
        # чтобы была возможность использовать отправку клиенту напрямую из функций проверки данных.
        return {'flag': 'true'}
