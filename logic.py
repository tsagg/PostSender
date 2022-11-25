import vk_api, json, telebot, os
from tkinter.messagebox import showerror, showwarning


def start_bot(login, password, token, count):
    if not login or not password or not token or not count:
        showerror(title="Ошибка!", message="Заполните пустые поля!")
        return

    if not count.isdigit():
        showerror(title="Ошибка!", message="Кол-во постов для сбора должно быть числом!")
        return

    edit_file("Account.txt", login + "\n" + password)
    edit_file("TgToken.txt", token)

    wall_parsing(count)


def auth_vk_password():
    try:
        account = read_file('Account.txt')
    except BaseException as BE:
        showerror(title="Ошибка!", message="Ошибка чтения файла данных аккаунта ВК!")
        return
    try:
        session = vk_api.VkApi(app_id=51470437, login=account[0], password=account[1], scope='wall')
        session.auth()
        vk = session.get_api()
    except BaseException as BE:
        showerror(title="Ошибка!", message="Ошибка авторизации в ВК!")
        return
    return vk


def read_file(path):
    try:
        with open(path, "r", encoding="utf-8") as file:
            return file.readlines()
    except BaseException as BE:
        showerror(title="Ошибка!", message="Ошибка при чтении файла!")


def edit_file(path, text):
    if not text or text == '\n':
        showerror(title="Ошибка!", message="Нечего сохранять!")
        return False
    try:
        with open(path, "w", encoding="utf-8") as file:
            file.writelines(text)
        return True
    except BaseException as BE:
        showerror(title="Ошибка!", message="Ошибка при сохранении данных!")
        return False


def send_posts():
    with open("data.json") as data_file:
        data = json.load(data_file)
    keywords = read_file('Keywords.txt')
    if not keywords:
        showerror(title="Ошибка!", message="Список ключевых слов пуст!")
        return
    token = read_file('TgToken.txt')
    if not token:
        showerror(title="Ошибка!", message="Токен телеграм пуст!")
        return
    chat_id = read_file('TgChatId.txt')
    if not chat_id:
        showerror(title="Ошибка!", message="Целевой канал не задан!")
        return
    bot = telebot.TeleBot(token[0])
    founded = False
    for i in range(len(data)):
        for keyword in keywords:
            if data[i]["text"].find(keyword) != -1:
                founded = True
                if len(data[i]["attachments"]) > 0:
                    medias = []
                    for j in range(len(data[i]["attachments"])):
                        if data[i]["attachments"][j]["type"] == "photo":
                            medias.append(telebot.types.InputMediaPhoto(
                                data[i]["attachments"][j]["photo"]["sizes"][len(data[i]["attachments"][j]["photo"]["sizes"]) - 1]["url"],
                                caption=data[i]["text"] if j == 0 else ''))
                    bot.send_media_group(int(chat_id[0]), medias)
                else:
                    bot.send_message(int(chat_id[0]), data[i]["text"])

    if not founded:
        showwarning(title="Внимание!", message="Не удалось найти ни одного поста по заданным критериям.")

    if os.path.isfile('data.json'):
        os.remove('data.json')


def wall_parsing(count):
    data = []
    groups = read_file('Groups.txt')
    if not groups:
        showerror(title="Ошибка!", message="Список групп пуст!")
        return

    chat_id = read_file('TgChatId.txt')
    if not chat_id:
        showerror(title="Ошибка!", message="Целевой канал не задан!")
        return

    try:
        with open("db" + chat_id[0] + ".json") as db_file:
            db = json.load(db_file)
    except FileNotFoundError as er:
        db = []

    if len(db) > 0:
        for i in range(len(db)):
            db[i][1] = -100
        for group in groups:
            exist = False
            for i in range(len(db)):
                if group == db[i][0]:
                    exist = True
                    db[i][1] = -1
                    break
            if not exist:
                db.append([group, -1, "0"])
    else:
        for group in groups:
            db.append([group, -1, "0"])

    db = [db_record for db_record in db if db_record[1] != -100]

    api = auth_vk_password()

    for i in range(len(db)):
        if db[i][0].find("club") != -1 and db[i][2] == "0":
            db[i][2] = "-" + db[i][0][(db[i][0].rfind("b") + 1):].strip()
        elif group.find("public") != -1 and db[i][2] == "0":
            db[i][2] = "-" + db[i][0][(db[i][0].rfind("c") + 1):].strip()
        try:
            wall = api.wall.get(owner_id=int(db[i][2]), count=count)
        except vk_api.ApiError:
            showerror(title="Ошибка!", message="Аккаунт вк заблокирован!")
            return
        if wall["count"] != 0:
            for j in range(len(wall["items"])):
                try:
                    db[i].index(wall["items"][j]['id'])
                except ValueError as er:
                    db[i].append(wall["items"][j]['id'])
                    data.append(wall["items"][j])

    with open("db" + chat_id[0] + ".json", "w") as db_file:
        json.dump(db, db_file)
    if len(data) > 0:
        with open("data.json", "w") as data_file:
            json.dump(data, data_file)
        send_posts()
    else:
        showwarning(title="Внимание!", message="Не удалось найти ни одного нового поста.")
