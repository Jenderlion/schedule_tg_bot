import requests
from lxml import html
from dataclasses import dataclass


@dataclass
class Session:
    time: str
    session: str
    classroom: str


class Day:
    def __init__(self, day):
        self.day = day
        self.sessions = []

    def __str__(self):
        return self.day

    def add_session(self, time, session, classroom):
        self.sessions.append(Session(time, session, classroom))


def schedule_return(input_time=None, user_id=None):

    def get_user_link(us_id):

        with open('db.txt', 'r') as links_file:
            list_of_lines = links_file.readlines()
            for line in list_of_lines:
                entry_num = line.find(':')
                if line[:entry_num] == str(us_id):
                    return line[entry_num + 1:-1]

        return 'https://bseu-api.appspot.com/schedule?faculty=14&group=8101&course=3&form=11'

    url_with_param = get_user_link(us_id=user_id)

    # url = 'https://bseu-api.appspot.com/schedule'
    # # ?faculty=14&group=8101&course=3&form=11
    # param_dict = {'faculty': 14, 'group': 8101, 'course': 3, 'form': 11}
    try:
        response = requests.get(url_with_param)
    except requests.exceptions.MissingSchema:
        response = requests.get('https://bseu-api.appspot.com/schedule?faculty=14&group=8101&course=3&form=11')

    root = html.fromstring(response.text)
    xpath = '/html/body/div[2]/div[1]/div/div/div/div[1]/div/div[2]/table'
    table = root.xpath(xpath)
    try:
        schedule_list = table[0].text_content().split('\n')[4:]
    except:
        result = {}
        result['эту группу'] = 'пусто'
        return result
    native_schedule_dict = {}
    week = ['понедельник', 'вторник', 'среда',
            'четверг', 'пятница', 'суббота', 'воскресенье']
    week_dict = {}

    for elem in schedule_list:
        if any(x in elem for x in week):
            last_day = elem
            native_schedule_dict[elem] = []
        else:
            native_schedule_dict[last_day].append(elem)

    for day, data in native_schedule_dict.items():
        if 'подгр.' in data:
            data.append(':')
            sch_list = []
            term_list = [data[0]]
            for elem_ind in range(1, len(data)):
                if ':' not in data[elem_ind]:
                    term_list.append(data[elem_ind])
                else:
                    if len(term_list) < 4:
                        for elem in term_list:
                            sch_list.append(elem)
                    else:
                        sch_list.append(term_list[0])
                        sch_list.append(f'{term_list[1]}, {term_list[3]} / {term_list[5]}, '
                                        f'{term_list[2]}')
                        sch_list.append(term_list[4])
                    term_list = [data[elem_ind]]
            native_schedule_dict[day] = sch_list

    for day, data in native_schedule_dict.items():
        week_dict[day] = []

        for session in range(0, len(data), 3):
            week_dict[day].append(
                Session(data[session], data[session + 1], data[session + 2]))

    # result = []
    # for KEY, VALUE in WEEK_DICT.items():
    #     result.append(f'|День: {KEY}')
    #     for VALUE_IND in range(len(VALUE)):
    #         result.append('|')
    #         result.append(f'||Занятие {VALUE_IND + 1}: ')
    #         result.append(f'||Во сколько: {VALUE[VALUE_IND].time}')
    #         result.append(f'||Что и у кого: {VALUE[VALUE_IND].session}')
    #         result.append(f'||Где: {VALUE[VALUE_IND].time}')
    #     result.append('')
    #
    # return result
    if input_time is None:
        return week_dict
    else:
        result = {}
        result[input_time] = week_dict.setdefault(input_time, 'пусто')
        return result

# print(schedule_return())
