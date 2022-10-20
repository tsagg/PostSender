import vk, time, openpyxl, telebot

token = "07bdf86bf2bd2e8d4e44ed19001555d4ed641657f954312a9446be8cceb2ef71388da7d12e800dec9fd17"
telegram_token = "1366807667:AAG-KmsqP7vTDsplcQDI9r56OI38CXqbCS8"
session = vk.Session(access_token=token)
api = vk.API(session, v='5.85')
bot = telebot.TeleBot(telegram_token)
print('Started')

def wallPars():

    # Read groups from txt
    print('Reading groups...')

    with open("Groups.txt", "r") as file:
        groups = file.readlines()

    # Read keywords from txt
    print('Reading keywords...')

    with open("Keywords.txt", "r") as file:
        keywords = file.readlines()

    for i in range(len(keywords)):
        keywords[i] = keywords[i].strip()

    # Links modification
    print('Preparing for parsing...')

    wb = openpyxl.load_workbook('posts.xlsx')
    sheet = wb.active

    count = 0

    for group in groups:
        i = 1
        exist = False
        while sheet.cell(row=i, column=1).value is not None:
            count += 1
            if group == str(sheet.cell(row=i, column=1).value):
                exist = True
                i += 1
                break
            else:
                i += 1
        if not exist:
            sheet.cell(row=count+1, column=1).value = group
            sheet.cell(row=count+1, column=2).value = "0"
            wb.save('posts.xlsx')

    # Parsing
    print('Parsing...')

    i = 1
    data = []

    for group in groups:
        i = 1
        while sheet.cell(row=i, column=1).value is not None:
            if group == str(sheet.cell(row=i, column=1).value):
                if str(sheet.cell(row=i, column=2).value) == "0":
                    if group.find("club") != -1:
                        group = "-" + group[(group.rfind("b") + 1):].strip()
                    elif group.find("public") != -1:
                        group = "-" + group[(group.rfind("c") + 1):].strip()
                    wall = api.wall.get(owner_id=group, count=100)
                    sheet.cell(row=i, column=2).value = "1"
                    wb.save('posts.xlsx')
                    if wall["count"] != 0:
                        data.append(wall["items"])
                        sheet.cell(row=i, column=3).value = data[i-1][0]['id']
                        wb.save('posts.xlsx')

                    i += 1
                elif str(sheet.cell(row=i, column=2).value) == "1":
                    if group.find("club") != -1:
                        group = "-" + group[(group.rfind("b") + 1):].strip()
                    elif group.find("public") != -1:
                        group = "-" + group[(group.rfind("c") + 1):].strip()
                    wall = api.wall.get(owner_id=group, count=1)
                    if wall["count"] != 0:
                        if str(wall["items"][0]["id"]) != str(sheet.cell(row=i, column=3).value):
                            data.append(wall["items"])

                    i += 1
            else:
                i += 1

    print('Parsed!')

    # Message sending
    print('Sending message...')

    for i in range(len(data)):
        for j in range(len(data[i])):
            for keyword in keywords:
                if data[i][j]["text"].find(keyword) != -1:
                    bot.send_message(470391929, "vk.com/club" + str(data[i][j]['owner_id'])[1:len(str(data[i][j]["owner_id"]))] + "?w=wall" + str(data[i][j]["owner_id"]) + "_" + str(data[i][j]["id"]))
                    bot.send_message(180329010, "vk.com/club" + str(data[i][j]['owner_id'])[1:len(str(data[i][j]["owner_id"]))] + "?w=wall" + str(data[i][j]["owner_id"]) + "_" + str(data[i][j]["id"]))

    print('Sent!')

while True:
    time.sleep(600)
    wallPars()