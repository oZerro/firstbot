import telebot
import requests
from bs4 import BeautifulSoup as BS
import json
from datetime import date
from datetime import time
from telebot import types


def tochka(num):
    sr = str(num)
    arr = list(sr)

    if len(arr) <= 3:
        return num

    i = len(arr)
    k = 0
    while i > 0:
        if k % 3 == 0 and k != 0:
            arr.insert(i, ".")
        i -= 1
        k += 1

    return "".join(arr) + "р"

def bez_tochka_and_p(num):
    arr = list(num)

    for k in arr:
        if k == ".":
            index = arr.index(".")
            del arr[index]
            continue
        if k == "р":
            index = arr.index("р")
            del arr[index]
            continue
        if k == "p":
            index = arr.index("p")
            del arr[index]
            continue

    num1 = "".join(arr)
    return int(num1)

def dney_ostalos():
    today = date.today()
    if today.year % 4 == 0 and today.year % 100 != 0 or today.year % 400 == 0:
        vis = 1
    else:
        vis = 0
    if today.month == 1 or today.month == 3 or today.month == 5 or today.month == 7 or today.month == 8 or today.month == 10 or today.month == 12:
        return 31 - int(today.day) + 1
    elif today.month == 2:
        if vis == 1:
            return 29 - int(today.day) + 1
        else:
            return 28 - int(today.day) + 1
    else:
        return 30 - int(today.day) + 1


def othet():
    # -------------------------  готовим дату
    today = date.today()
    current_time = time(6)
    today2 = "{}-{}-{}".format(today.year, today.month, int(today.day) - 1)
    arr_today2 = today2.split("-")
    for i in range(len(arr_today2)):
        if len(arr_today2[i]) == 1:
            arr_today2[i] = "0" + str(arr_today2[i])

    gotov_date2 = "-".join(arr_today2) + " " + str(current_time)
    gotov_date2 = gotov_date2[:16]

    today_preob3 = "{}-{}-{}".format(today.year, today.month, int(today.day))
    arr_today3 = today_preob3.split("-")
    for i in range(len(arr_today3)):
        if len(arr_today3[i]) == 1:
            arr_today3[i] = "0" + str(arr_today3[i])

    gotov_date3 = "-".join(arr_today3) + " " + str(current_time)
    gotov_date3 = gotov_date3[:16]

    today_preob = "{}.{}.{}".format(int(today.day) - 1, today.month, today.year)
    arr_today = today_preob.split(".")
    for i in range(len(arr_today)):
        if len(arr_today[i]) == 1:
            arr_today[i] = "0" + str(arr_today[i])

    gotov_date = ".".join(arr_today)
        # ---------------------------------------------------------------------------------------------

    link = 'https://realtycalendar.ru/users/sign_in'
    session = requests.Session()
    auth_html = session.get(link)
    auth_bs = BS(auth_html.content, "html.parser")
    token_au = auth_bs.select('input[name="authenticity_token"]')[0]['value']

    header = {
        'User-agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/99.0.4844.82 Safari/537.36'}

    datas = {
            "utf8": "✓",
            "authenticity_token": token_au,
            "user[email]": "otelotdyh@yandex.ru",
            "user[password]": "Avopih71@",
            "user[remember_me]": "0",
            "commit": "Войти"
    }

    response = session.post(link, data=datas, headers=header).text

    link2 = "https://realtycalendar.ru/agencies/9355/apartments"
    re = session.get(link2)
    soup = BS(re.content, 'html.parser')
    # ---------------------------------------------------------------------------

    nal = 0  # сумма ВСЕХ НАЛИЧНЫХ ЗА СЕГОДНЯ
    terminal = 0  # сумма ВСЕХ оплат по терминалу ЗА СЕГОДНЯ
    rs_tink = 0  # сумма ВСЕХ ПЕРЕВОДОВ НА РС ЗА СЕГОДНЯ
    perevod_karta = 0  # сумма ВСЕХ переводов на карту ЗА СЕГОДНЯ
    book = 0  # сумма ВСЕХ оплат на площадках ЗА СЕГОДНЯ
    bar = 0
    traty = []
    traty_int = 0
    traty_water = 0

    arr_id_kap = []  # ТУТ БУДЕТ ХРАНИТТЬСЯ ID БРОНИ
    arr_name_kap = []  # ТУТ БУДУТ КОНТАКТЫ КЛИЕНТА
    num_page = 1
    while num_page <= 2:

            # ПАРСИМ СТРАНИЦУ С БРОНЯМИ
        link23 = "https://realtycalendar.ru/requests_bookings/bookings?page="
        link_gotov = link23 + str(num_page) + "&order=begin_date"
        re1 = session.get(link_gotov)
        soup1 = BS(re1.content, 'html.parser')

        massiv = str(soup1)  # тут преобразуем бэтифулсуп в строку
        slovar = json.loads(massiv)  # тут преобразуем строку в словарь
        massiv_gostei = slovar["event_calendars"]  # тут достаем из словаря массив гостей

        arr_id_kap_bar = []  # ТУТ БУДЕТ БАР
        for i in massiv_gostei:  # достаем данные только тех гостей у которых в адресе есть КАП
            if "КАП" in i["apartment_address"]:
                arr_id_kap.append(i["id"])  # записываем id ГОСТЯ в массив
                arr_name_kap.append(i["contacts"])  # записываем КОНТАКТЫ ГОСТЯ в массив
        num_page += 1

        # будем доставать данные об оплатах по каждому id
    link_op = "https://realtycalendar.ru/agencies/9355/search/"

        # ТУТ ОТКРЫВАЕМ КАЖДОГО ГОСТЯ ПО ID И СМОТРИ ИНФОРМАЦИЮ ОБ ОПЛАТАХ
    for i in range(len(arr_id_kap)):
        link_op_gotov = link_op + str(arr_id_kap[i])  # ДЕЛАЕМ ССЫЛКУ  - ССЫЛКА + ID
        re3 = session.get(link_op_gotov)

        soup3 = BS(re3.content, 'html.parser')
        massiv_op = str(soup3)  # тут преобразуем бэтифулсуп в строку. будем доставать данные об оплатах
        slovar_op = json.loads(massiv_op)  # тут преобразуем строку в словарь

        if slovar_op["event"]["apartment_id"] == 97363 and slovar_op["event"]["begin_date"] == gotov_date2[:10]:  # ЭТО УСЛОВИЕ НА ПОИСК БАРА
            if slovar_op["event"]["short_notes"] != "":
                traty = slovar_op["event"]["short_notes"].split()
            if slovar_op["event"]["event_calendar_payments"] != []:
                for j in slovar_op["event"]["event_calendar_payments"]:  # ТУТ ПРОХОДИМСЯ ПО КАЖДОЙ ПРОДАЖЕ В БАРЕ
                    if j["date"] > gotov_date2 and j["date"] < gotov_date3:  # ЕСЛИ ДАТА ОПЛАТЫ СЕГОДНЯ
                        if j["invoice_name"] == "касса КАПОТНЯ" and "нал" in j["note"]:
                            nal += j["amount"]
                            bar += j["amount"]
                        elif j["invoice_name"] == "Эквайринг Капотня":
                            terminal += j["amount"]
                            bar += j["amount"]
                        elif j["invoice_name"] == "касса КАПОТНЯ" and "пере" in j["note"]:
                            perevod_karta += j["amount"]
                            bar += j["amount"]
            continue

        if slovar_op["event"]["event_calendar_payments"] != []:  # ЕСЛИ У ЧЕЛОВЕКА ЕСТЬ ОПЛАТЫ
            for j in slovar_op["event"]["event_calendar_payments"]:  # ТУТ ПРОХОДИМСЯ ПО КАЖДОЙ ЕГО ОПЛАТЕ
                if j["date"] > gotov_date2 and j["date"] < gotov_date3:  # ЕСЛИ ДАТА ОПЛАТЫ СЕГОДНЯ
                    if j["invoice_name"] == "касса КАПОТНЯ" and "нал" in j["note"]:
                        nal += j["amount"]
                    elif j["invoice_name"] == "Эквайринг Капотня":
                        terminal += j["amount"]
                    elif j["invoice_name"] == "Расчет.Счет ИП (Тинькофф)":
                        rs_tink += j["amount"]
                    elif j["invoice_name"] == "касса КАПОТНЯ" and "пере" in j["note"]:
                        perevod_karta += j["amount"]
                    elif j["invoice_name"] == "Букинг Капотня":
                        book += j["amount"]

    file = open("C:\\Users\\Дмитрий\\Desktop\\начало\\otchet.txt", encoding="UTF-8")
    file4 = open("C:\\Users\\Дмитрий\\Desktop\\начало\\otchet3.txt", "w", encoding="UTF-8")
    stroki = [i.rstrip() for i in file]

    for h in stroki:
        file4.write(h + "\n")

    stroka_data = stroki[0].split()
    stroka_data[2] = gotov_date
    stroki[0] = " ".join(stroka_data)
    vup = 0
    file.close()
    file4.close()
    for i in range(len(stroki)):
            if "Наличные" in stroki[i] and i == 2:
                chernovik = stroki[i].split()
                if len(chernovik) == 1:
                    chernovik.append(str(nal) + "p")
                    stroki[i] = " ".join(chernovik)
                elif len(chernovik) > 1:
                    chernovik[-1] = str(nal) + "p"
                    stroki[i] = " ".join(chernovik)

            elif "Перевод" in stroki[i] and i == 4:
                chernovik = stroki[i].split()
                if len(chernovik) == 1:
                    chernovik.append(str(perevod_karta) + "p")
                    stroki[i] = " ".join(chernovik)
                elif len(chernovik) > 1:
                    chernovik[-1] = str(perevod_karta) + "p"
                    stroki[i] = " ".join(chernovik)

            elif "Терминал" in stroki[i] and i == 6:
                chernovik = stroki[i].split()
                if len(chernovik) == 1:
                    chernovik.append(str(terminal) + "p")
                    stroki[i] = " ".join(chernovik)
                elif len(chernovik) > 1:
                    chernovik[-1] = str(terminal) + "p"
                    stroki[i] = " ".join(chernovik)

            elif "РС(тинькофф)" in stroki[i] and i == 8:
                chernovik = stroki[i].split()
                if len(chernovik) == 1:
                    chernovik.append(str(rs_tink) + "p")
                    stroki[i] = " ".join(chernovik)
                elif len(chernovik) > 1:
                    chernovik[-1] = str(rs_tink) + "p"
                    stroki[i] = " ".join(chernovik)

            elif "Букинг(островок)" in stroki[i] and i == 10:
                chernovik = stroki[i].split()
                if len(chernovik) == 1:
                    chernovik.append(str(book) + "p")
                    stroki[i] = " ".join(chernovik)
                elif len(chernovik) > 1:
                    chernovik[-1] = str(book) + "p"
                    stroki[i] = " ".join(chernovik)

            elif "ВЫРУЧКА" in stroki[i] and i == 12:
                chernovik = stroki[i].split()
                chernovik[-1] = str(nal + perevod_karta + terminal + rs_tink + book) + "p"
                stroki[i] = " ".join(chernovik)

            elif "НАЛ:" in stroki[i] and i == 15:
                chernovik = stroki[i].split()

                if len(chernovik) > 7:
                    for k in chernovik:
                        if k == "=":
                            index = chernovik.index("=")
                            del chernovik[1:index + 1]
                if "." in chernovik[1]:
                    chernovik[1] = bez_tochka_and_p(chernovik[1])

                chernovik[1] = chernovik[1] + nal
                chernovik[1] = str(tochka(chernovik[1]))
                stroki[i] = " ".join(chernovik)

            elif "КАРТЕ:" in stroki[i] and i == 16:
                chernovik = stroki[i].split()
                if "." in chernovik[2] and len(chernovik) > 1:
                    chernovik[2] = bez_tochka_and_p(chernovik[2])

                chernovik[2] = chernovik[2] + perevod_karta
                chernovik[2] = str(tochka(chernovik[2]))
                stroki[i] = " ".join(chernovik)

            elif "ТЕРМИНАЛ:" in stroki[i] and i == 17:
                chernovik = stroki[i].split()
                if "." in chernovik[1] and len(chernovik) > 0:
                    chernovik[1] = bez_tochka_and_p(chernovik[1])

                chernovik[1] = chernovik[1] + terminal
                chernovik[1] = str(tochka(chernovik[1]))
                stroki[i] = " ".join(chernovik)

            elif "РС(тинькофф):" in stroki[i] and i == 18:
                chernovik = stroki[i].split()
                if "." in chernovik[1] or "p" in chernovik[1] or "р" in chernovik[1]:
                    chernovik[1] = bez_tochka_and_p(chernovik[1])

                chernovik[1] = chernovik[1] + rs_tink
                chernovik[1] = str(tochka(chernovik[1]))
                stroki[i] = " ".join(chernovik)

            elif "Букинг:" in stroki[i] and i == 19:
                chernovik = stroki[i].split()
                if "." in chernovik[1] or "p" in chernovik[1] or "р" in chernovik[1]:
                    chernovik[1] = bez_tochka_and_p(chernovik[1])

                chernovik[1] = chernovik[1] + book
                chernovik[1] = str(tochka(chernovik[1]))
                stroki[i] = " ".join(chernovik)

            elif "Хоз" in stroki[i] and i == 22:
                chernovik = stroki[i].split()
                if len(chernovik) > 2 or "." in chernovik[2]:
                    chernovik[2] = bez_tochka_and_p(chernovik[2])

                arr11 = []
                arr22 = []
                for o in range(len(traty)):  # РАЗБИВАЕМ ТРАТЫ ПО МАССИВАМ
                    if o == 0:
                        if traty[o].isdigit() and not(traty[o + 1].isdigit()):
                            arr11.append(traty[o].lower())
                            continue
                    if o > 0:
                        if o == len(traty) - 1:
                            if not(traty[o].isdigit()):
                                arr11.append(traty[o].lower())
                                arr22.append(arr11)
                                arr11 = []
                                break
                        if not(traty[o].isdigit()) and traty[o - 1].isdigit() and not(traty[o + 1].isdigit()):
                            arr11.append(traty[o].lower())
                            continue
                        if traty[o].isdigit() and not(traty[o + 1].isdigit()) and not(traty[o - 1].isdigit()):
                            arr11.append(traty[o].lower())
                            continue
                        if not(traty[o].isdigit()) and traty[o + 1].isdigit():
                            arr11.append(traty[o].lower())
                            arr22.append(arr11)
                            arr11 = []
                            continue
                        # ТУТ У НАС ПОЛУЧАЕТСЯ МАТРИЦА ИЗ ТРАТ ДВУМЕРНАЯ arr22
                
                for g in arr22:
                    if not("вода" in g):
                        traty_int += int(g[0])
                    else:
                        traty_water += int(g[0])
                
                traty_obche = traty_int + traty_water

                trata_voda = stroki[23].split()
                trata_voda[1] = str(traty_water + int(trata_voda[1]))
                stroki[23] = " ".join(trata_voda)


                if traty_obche > 0:
                    dlya_vucheta_trat = stroki[15].split()  # тут строка: сколько денег в кассе НАЛ
                    if "." in dlya_vucheta_trat[1]:  # этот if преобразует число с точкой, в число без точки
                        dlya_vucheta_trat[1] = bez_tochka_and_p((dlya_vucheta_trat[1]))

                    sum_minus_traty = dlya_vucheta_trat[1] - traty_obche
                    dlya_vucheta_trat[1] = tochka(dlya_vucheta_trat[1])
                    dlya_vucheta_trat.insert(2, "-")
                    dlya_vucheta_trat.insert(3, str(tochka(traty_obche)))
                    dlya_vucheta_trat.insert(4, "(хоз нужды) = {}".format(tochka(sum_minus_traty), ))
                    if dlya_vucheta_trat[5] == "-":
                        del dlya_vucheta_trat[5:9]
                    stroki[15] = " ".join(dlya_vucheta_trat)

                chernovik[2] = chernovik[2] + traty_int
                chernovik[2] = str(tochka(chernovik[2]))
                stroki[i] = " ".join(chernovik)

            elif "Выполнено" in stroki[i] and i == 26:
                chernovik = stroki[i].split()
                if "." in chernovik[1]:
                    chernovik[1] = bez_tochka_and_p(chernovik[1])

                chernovik[1] = int(chernovik[1]) + nal + perevod_karta + terminal + rs_tink + book
                vup = chernovik[1]
                chernovik[1] = str(tochka(chernovik[1]))
                stroki[i] = " ".join(chernovik)

            elif "Нужно" in stroki[i] and i == 28:
                chernovik = stroki[i].split()
                if "." in chernovik[3]:
                    chernovik[3] = bez_tochka_and_p(chernovik[3])  # нужно в сутки chernovik[3]

                chernovik_1 = stroki[i - 3].split()
                if "." in chernovik_1[1]:
                    chernovik_1[1] = bez_tochka_and_p(chernovik_1[1])  # план chernovik_1[1]

                chernovik[3] = (int(chernovik_1[1]) - vup) // dney_ostalos()
                chernovik[3] = str(tochka(chernovik[3]))
                stroki[i] = " ".join(chernovik)

            elif "Бар" in stroki[i] and i == 30:
                chernovik = stroki[i].split()
                if "." in chernovik[1] or "p" in chernovik[1] or "р" in chernovik[1]:
                    chernovik[1] = bez_tochka_and_p(chernovik[1])  # нужно в сутки chernovik[3]

                chernovik[1] = int(chernovik[1]) + bar
                chernovik[1] = str(tochka(chernovik[1]))
                stroki[i] = " ".join(chernovik)

    text_bot = ""

    for rt in stroki:
        text_bot += rt + "\n"

    file3 = open("C:\\Users\\Дмитрий\\Desktop\\начало\\otchet2.txt", "w", encoding="UTF-8")
    file3.write(text_bot)
    file3.close()

    file1 = open("C:\\Users\\Дмитрий\\Desktop\\начало\\otchet.txt", "w", encoding="UTF-8")
    file1.write(text_bot)
    file1.close()


    return text_bot



bot = telebot.TeleBot("5241092362:AAFfm7iV1IHtweeZv2ZM0Aex_HdBjvlyUe0")


@bot.message_handler(commands=['start'])
def start(message):
    
    markap_inline = types.InlineKeyboardMarkup()
    item_vchera = types.InlineKeyboardButton(text = "ОТЧЕТЫ", callback_data = "tomorro")

    markap_inline.add(item_vchera)
    bot.send_message(message.chat.id, "Привет, нажми на кнопку 'ОТЧЕТЫ'",
        reply_markup = markap_inline
    )


@bot.callback_query_handler(func = lambda call: True)
def answer(call):
    if call.data == "tomorro":
        markup_replay = types.ReplyKeyboardMarkup(resize_keyboard=True)
        item_vchera_1 = types.KeyboardButton("НОВЫЙ")
        item_prosh_1 = types.KeyboardButton("ПРОШЛЫЙ")
        item_gotov_1 = types.KeyboardButton("ГОТОВЫЙ")

        markup_replay.add(item_vchera_1, item_prosh_1, item_gotov_1)
        bot.send_message(call.message.chat.id, "Выбери, то что тебе нужно!",
            reply_markup = markup_replay
        )

    
@bot.message_handler(content_types=['text'])
def get_text(message):
    if message.text == "НОВЫЙ":
        file = open("C:\\Users\\Дмитрий\\Desktop\\начало\\otchet.txt", encoding="UTF-8")
        stroki1 = file.readline().split()
        file.close()
        data_file = stroki1[2].split(".")[::-1]
        today = date.today()
        current_time = time(6)
        qwe = int(today.day) - int(data_file[-1])
    
        if qwe == 2: 
            mess2 = "Новый отчет готовится, нужно немного подождать!"
            bot.send_message(message.chat.id,  mess2, parse_mode='html')    
            mess = f"Привет, {message.from_user.first_name}"
            bot.send_message(message.chat.id, mess + "\n" + othet(), parse_mode='html')
        else:
            mess = f"Привет, {message.from_user.first_name} , для отчета еще рановато! \nОтчет за вчерашний день ты уже делал!\nНажми на кнопку ГОТОВЫЙ и ты его получишь"
            bot.send_message(message.chat.id, mess , parse_mode='html')
        
    elif message.text == "ПРОШЛЫЙ":
        file = open("C:\\Users\\Дмитрий\\Desktop\\начало\\otchet3.txt", encoding="UTF-8")
        strt = ""
        for i in file:
            strt += i
        bot.send_message(message.chat.id, strt , parse_mode='html')

    elif message.text == "ГОТОВЫЙ":
        file = open("C:\\Users\\Дмитрий\\Desktop\\начало\\otchet2.txt", encoding="UTF-8")
        strt = ""
        for i in file:
            strt += i
        bot.send_message(message.chat.id, strt , parse_mode='html')


bot.polling(none_stop=True)




