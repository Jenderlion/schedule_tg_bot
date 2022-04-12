import telebot
from telebot import types
import my_parser
import datetime
import time
from receiving_api import get_api
import requests
import logging
import json


logging.basicConfig(filename="log.txt", level=logging.INFO)
API_KEY = get_api()
bot = telebot.TeleBot(API_KEY)

# Keyboard buttons
button_today = types.KeyboardButton('/расписание сегодня')
button_tomorrow = types.KeyboardButton('/расписание завтра')
button_week = types.KeyboardButton('/расписание неделя')
button_killer = types.KeyboardButton('/расписание всё')
button_fun = types.KeyboardButton('/анекдот')
button_certificate = types.KeyboardButton('/справка')
button_start = types.KeyboardButton('/start')
button_help = types.KeyboardButton('/help')


greet_kb = types.ReplyKeyboardMarkup(resize_keyboard=True)
greet_kb.add(button_today, button_tomorrow, button_week, button_killer, button_fun,
             button_certificate, button_help, button_start)

# global variables
msg_info_from_bot = telebot.types.Message
msg_info_from_user = telebot.types.Message


def debug_write(msg):
    print(msg)
    bot.send_message(449808966, msg)
    logging.error(f'{msg}\n')


@bot.message_handler(content_types=['text'])
def get_text_messages(message):
    if message.text[0] == '/':

        def get_input_t(time_s, day_s):

            # processing input time from real time and date for pattern "поенедльник (14.3.2022)"
            # all extra zeros are removed
            if time_s[5] != '0':
                input_ti = f' ({time_s[8:10]}.{time_s[5:7]}.{time_s[0:4]})'
            else:
                input_ti = f' ({time_s[8:10]}.{time_s[6]}.{time_s[0:4]})'

            if input_ti[2] == '0':
                input_ti = input_ti[:2] + input_ti[3:]

            print(input_ti)

            dict_of_week = {0: 'понедельник', 1: 'вторник', 2: 'среда', 3: 'четверг',
                            4: 'пятница', 5: 'суббота', 6: 'воскресенье'}

            result = f'{dict_of_week[day_s]}{input_ti}'
            return result

        def send_message_with_timed_schedule(input_time=None):

            # getting day dictionary
            input_dict = my_parser.schedule_return(input_time, user_id=message.from_user.id)

            # primary handler of day dictionary
            if list(input_dict.values())[0] == 'пусто':

                # no data in dictionary:
                if input_time:
                    bot.send_message(message.from_user.id, f'Расписание на {input_time} '
                                                           f'пока не завезли!')
                else:
                    bot.send_message(message.from_user.id, f'Расписание пока не завезли!')

            else:

                # some data in dictionary
                debug_msg = f'@{message.from_user.username} with param {input_time}'
                debug_write(debug_msg)

                for key, value in input_dict.items():
                    or_result = f'День: {key}'
                    for value_ind in range(len(value)):
                        or_result += f'\n\n|Занятие {value_ind + 1}:\n|' \
                                     f'{value[value_ind].time}\n|' \
                                     f'{value[value_ind].session}\n|' \
                                     f'{value[value_ind].classroom}'
                    bot.send_message(message.from_user.id, or_result)
                    time.sleep(1)

        def id_handler(user_id):

            # checking for user data
            checked_file = open('db.txt', 'a+')
            checked_file.close()
            checked_file = open('db.txt', 'r')
            list_of_lines = checked_file.readlines()

            for line in list_of_lines:
                s_line = line[:-1]
                entry_in_line = s_line.find(':')

                if s_line[:entry_in_line] == str(user_id):
                    print(f'Find user data: ID: {s_line[:entry_in_line]} '
                          f'Link: {s_line[entry_in_line + 1:]}')
                    checked_file.close()
                    return s_line[entry_in_line + 1:]

            checked_file.close()
            return 'empty'

        if message.text[1:] in ['расписание сегодня', 'рс', 'hfcgbcfybt ctujlyz']:
            bot.send_message(message.from_user.id, 'Сейчас посмотрим расписание на'
                                                   ' сегодня...', reply_markup=greet_kb)

            time_stamp = str(datetime.datetime.now())
            day_stamp = datetime.datetime.weekday(datetime.datetime.now())
            # print(f'Исходное время: {time_stamp}, день {day_stamp}')
            # Uncomment that lines for debug
            # time_stamp = '2022-03-15 20:39:32.331950'
            # day_stamp = 1
            # print(f'Заданное время: {time_stamp}, день {day_stamp}')

            input_t = get_input_t(time_stamp, day_stamp)
            send_message_with_timed_schedule(input_t)

        elif message.text[1:] in ['расписание завтра', 'рз', 'hfcgbcfybt pfdnhf']:
            bot.send_message(message.from_user.id, 'Сейчас посмотрим расписание на'
                                                   ' завтра...', reply_markup=greet_kb)
            _date = datetime.datetime.now()
            _date += datetime.timedelta(days=1)
            time_stamp = str(_date)
            day_stamp = datetime.datetime.weekday(_date)

            input_t = get_input_t(time_stamp, day_stamp)
            send_message_with_timed_schedule(input_t)

        elif message.text[1:] in ['расписание всё', 'рс', 'hfcgbcfybt dc`']:
            bot.send_message(message.from_user.id, 'Prepare your butter!', reply_markup=greet_kb)
            time.sleep(1)
            bot.send_message(message.from_user.id, 'What? Butter?.. '
                                                   'What does butter have to do with it?..')
            send_message_with_timed_schedule(None)

        elif message.text[1:] in ['расписание неделя', 'рн', 'hfcgbcfybt ytltkz']:
            bot.send_message(message.from_user.id, 'Сейчас посмотрим расписание на'
                                                   ' неделю...', reply_markup=greet_kb)
            _date = datetime.datetime.now()

            for i in range(7):
                time_stamp = str(_date)
                day_stamp = datetime.datetime.weekday(_date)
                input_t = get_input_t(time_stamp, day_stamp)
                send_message_with_timed_schedule(input_t)
                _date += datetime.timedelta(days=1)

        elif message.text[1:11] in ['расписание', 'hfcgbcfybt']:
            bot.send_message(message.from_user.id, f'Я попробую поискать по запросу: '
                                                   f'{message.text[12:]}\nЕсли не'
                                                   f' получится - введи по образцу:'
                                                   f' "понедельник (14.3.2022)"\n'
                                                   f'Также должно сработать: ДД.ММ.ГГГГ\n'
                                                   f'И не ставь лишних символов!')
            date_for_proc = message.text[12:]
            if len(date_for_proc) != 10:
                send_message_with_timed_schedule(message.text[12:])
            else:
                p_day, p_month, p_year = (int(x) for x in date_for_proc.split('.'))
                try:
                    date_stamp = datetime.date(p_year, p_month, p_day)
                    day_stamp = datetime.datetime.weekday(date_stamp)
                    print(date_stamp)
                    print(day_stamp)
                    input_time_for_func = (get_input_t(time_s=str(date_stamp), day_s=day_stamp))
                    print(input_time_for_func)
                    send_message_with_timed_schedule(input_time=input_time_for_func)
                except Exception:
                    bot.send_message(message.from_user.id, 'С датой что-то не так :(')

        elif message.text[1:8] == 'addlink':

            # add or change user data
            if len(message.text) >= 10:

                user_info = id_handler(message.from_user.id)

                if user_info == 'empty':
                    # add user data
                    bot.send_message(message.from_user.id, 'Сейчас запишем тебя!')
                    check_file = open('db.txt', 'a')
                    check_file.write(f'{message.from_user.id}:{message.text[9:]}\n')
                    check_file.close()
                    debug_msg = f'Add user @{message.from_user.username} with ' \
                                f'id {message.from_user.id}, link {message.text[9:]}'
                    debug_write(debug_msg)
                    bot.send_message(message.from_user.id, 'Тебя успешно записали :)')
                else:
                    # change user data
                    bot.send_message(message.from_user.id, 'Сейчас перезапишем тебя!')
                    with open('db.txt', 'r+') as check_file:
                        list_of_lines = check_file.readlines()

                        for line_ind in range(len(list_of_lines)):
                            entry_num = list_of_lines[line_ind].find(':')

                            condition_value = f'{message.from_user.id}'
                            if list_of_lines[line_ind][:entry_num] == condition_value:
                                addable = f'{message.from_user.id}:{message.text[9:]}\n'
                                debug_msg = f'Removed: {list_of_lines.pop(line_ind)}' \
                                            f'Change in db.txt: {addable}'
                                debug_write(debug_msg)
                                list_of_lines.append(addable)
                                changed = ''.join(list_of_lines)

                    with open('db.txt', 'w') as check_file:
                        check_file.write(changed)
                    bot.send_message(message.from_user.id, 'Тебя успешно перезаписали :)')

            else:
                bot.send_message(message.from_user.id, 'Ссылочка коротковата...')

        elif message.text[1:] == 'start':
            bot.send_message(message.from_user.id, 'Добро пожаловать(ся)! '
                                                   'Попробуй набрать /help'
                                                   '', reply_markup=greet_kb)
            debug_write(f'New user: @{message.from_user.username}')

            user_info = id_handler(message.from_user.id)
            if user_info == 'empty':
                bot.send_message(message.from_user.id, 'Кажется, я тебя не узнал :(\n\n'
                                                       'Зайди, пожалуйста, на '
                                                       'https://bseu-api.appspot.com/\n'
                                                       'Введи там всю информацию про себя,'
                                                       ' скопируй'
                                                       ' ссылку и отправь мне в команде'
                                                       ' /addlink'
                                                       ' (ссылка)\n\n'
                                                       'Кстати, если у тебя поменялись'
                                                       ' данные, ты'
                                                       ' можешь использовать ту же'
                                                       ' команду для'
                                                       ' их обновления!\n\n'
                                                       'Выражаю благодарность Stanislau'
                                                       ' Charniakou'
                                                       ' и Dennis Dashkevich за создание'
                                                       ' этого замечательного сайта :)')

        elif message.text[1:] in ['help', 'h', 'помощь', 'п']:
            bot.send_message(message.from_user.id, 'Сейчас я умею только отправлять'
                                                   ' расписание.\n'
                                                   'Попробуй ввести что-то из:\n'
                                                   '/расписание сегодня или /рс\n'
                                                   '/расписание завтра или /рз\n'
                                                   '/расписание всё - это если ты'
                                                   ' самоубийца\n'
                                                   '/расписание дата', reply_markup=greet_kb)

        elif message.text[1:] in ['d', 'debug']:
            bot.send_message(message.from_user.id, 'Пишу в консоль')
            debug_write(f'User ID: {message.from_user.id}\nUsername: {message.from_user.username}\n'
                        f'Message.text: {message.text}\nMessage.date: {datetime.datetime.now()}')

        elif message.text[1:6] == 'check':
            bot.send_message(message.from_user.id, 'Пишу в консоль всё, что есть')
            debug_write(message)
            debug_write(message.json)

        elif message.text[1:] == 'маселко':
            debug_write('Butter is active!')
            bot.send_message(message.from_user.id, '— Для чего я создан?')
            time.sleep(2)
            bot.send_message(message.from_user.id, '— Чтобы передать масло.')
            time.sleep(2)
            bot.send_message(message.from_user.id, '— Боже мой…')
            time.sleep(2)
            bot.send_message(message.from_user.id, '— Да, добро пожаловать в клуб,'
                                                   ' приятель.')
            time.sleep(2)

        elif message.text[1:] == 'енот':
            bot.send_message(message.from_user.id, 'I <3 U')
            debug_write('I <3 U')

        elif message.text[1:] == 'admin':
            bot.send_message(message.from_user.id, 'https://www.youtube.com/'
                                                   'watch?v=dQw4w9WgXcQ')
            debug_write(f'User @{message.from_user.username} are RickRolled!')

        elif message.text[1:] == 'анекдот':
            debug_write(f'User @{message.from_user.username} wants to laugh!')
            fun_response = requests.get('http://rzhunemogu.ru/RandJSON.aspx?CType=12').text
            bot.send_message(message.from_user.id, fun_response[12:-2])

        elif message.text[1:] == 'справка':

            certificate_menu = telebot.types.InlineKeyboardMarkup(row_width=1)
            certificate_menu.add(telebot.types.InlineKeyboardButton(text='Справка-вызов',
                                                                    callback_data='first'))
            certificate_menu.add(telebot.types.InlineKeyboardButton(text='Справка об учёбе',
                                                                    callback_data='second'))
            global msg_info_from_user
            msg_info_from_user = message
            global msg_info_from_bot
            msg_info_from_bot = bot.send_message(message.from_user.id, 'Какая справка нужна?',
                                                 reply_markup=certificate_menu)

        elif message.text[1:4] == 'кто':
            who_is_list = message.text[5:].split()
            with open('base.txt', 'r') as file:
                user_dict = json.load(file)
                if str(message.from_user.id) in user_dict.keys():
                    if len(message.text) > 4:
                        check_mark = 0
                        for req_h in who_is_list:
                            req = req_h.lower()
                            for key, value in user_dict.items():
                                name_list = value[1].lower().split()
                                check_list = [key, value[0].lower(), name_list[0], name_list[1], name_list[2]]
                                if req in check_list:
                                    check_mark = 1
                                    if message.from_user.id == 449808966:
                                        bot.send_message(449808966, f'{value[1]} - {value[0]} - {key}')
                                    else:
                                        bot.send_message(message.from_user.id, f'{value[1]} - {value[0]}')
                                        debug_write(f'User @{message.from_user.username} found {value[0]}')
                                    break

                        if check_mark != 1:
                            bot.send_message(message.from_user.id, f'Так не нашёл '
                                                                   f':(\nПопробуй /кто')
                            debug_write(f'User @{message.from_user.username} try to found {message.text[5:]}')
                    else:
                        answer_list = []
                        answer = 'Список нашей группы:\n'
                        for key, value in user_dict.items():
                            if message.from_user.id == 449808966:
                                answer_list.append(f'{value[1]}: {value[0]} - {key}\n')
                            else:
                                answer_list.append(f'{value[1]}: {value[0]}\n')
                            answer_list.sort()
                        for item in answer_list:
                            answer += item
                        bot.send_message(message.from_user.id, answer)
                        debug_write(f'User @{message.from_user.username} requested list!')
                else:
                    bot.send_message(message.from_user.id, f'Тебе нельзя, извини :(')
                    debug_write(f'User @{message.from_user.username} is double matherfucker!')

        elif message.from_user.id == 449808966 and message.text[0] == '/':
            if message.text[1:8] == 'message':
                msg_text = message.text[9:]
                with open('base.txt', 'r') as file:
                    user_dict = json.load(file)
                    for key, value in user_dict.items():
                        try:
                            bot.send_message(int(key), msg_text)
                        except Exception:
                            bot.send_message(449808966, f'User {value[0]} rediska!')
                debug_write(f'Newsletter completed!')

            elif message.text[1:4] == 'log':
                bot.send_document(449808966, open(r'log.txt', 'rb'))

            elif message.text[1:5] == 'wlog':
                len_of_m = int(message.text[6:])
                with open('log.txt', 'r') as log_file:
                    list_of_log = log_file.readlines()
                    if len(list_of_log) < len_of_m:
                        len_of_m = len(list_of_log)
                    ans_list = list_of_log[- len_of_m - 1:]
                    ans = ''
                    for string in ans_list:
                        ans += f'{string}'
                    bot.send_message(449808966, ans)



        else:
            bot.send_message(message.from_user.id, 'Я тебя не понимаю')
            print(f'User @{message.from_user.username} is matherfucker')
            debug_write(f'User @{message.from_user.username} is matherfucker!\n'
                        f'Reason: {message.text}')

    else:
        debug_write(f'"{message.text}"\n@{message.from_user.username}')


@bot.callback_query_handler(func=lambda call: True)
def callback_inline(call):
    try:
        if call.message:
            if call.data == 'first':
                # bot.edit_message_reply_markup(chat_id=msg_info.chat.id,
                #                               message_id=msg_info.message_id, reply_markup=None)
                bot.edit_message_text(chat_id=msg_info_from_bot.chat.id,
                                      message_id=msg_info_from_bot.message_id,
                                      text=f'Справка-вызов:\nhttp://fcti.by/zakaz-spravok-vizov/',
                                      reply_markup=None)
                debug_write(f'For @{msg_info_from_user.from_user.username} link '
                            f'http://fcti.by/zakaz-spravok-vizov/!')
            elif call.data == 'second':
                # bot.edit_message_reply_markup(chat_id=msg_info.chat.id,
                #                               message_id=msg_info.message_id, reply_markup=None)
                bot.edit_message_text(chat_id=msg_info_from_bot.chat.id,
                                      message_id=msg_info_from_bot.message_id,
                                      text=f'Справка об учёбе:\nhttp://fcti.by/zakaz-spravok/',
                                      reply_markup=None)
                debug_write(f'For @{msg_info_from_user.from_user.username} link '
                            f'http://fcti.by/zakaz-spravok/!')

    except Exception as Exc_txt:

        time.sleep(10)
        debug_write(Exc_txt)


while True:
    try:
        bot.polling(none_stop=True, interval=1)

    except Exception as Exc_txt:

        time.sleep(10)
        debug_write(Exc_txt)
