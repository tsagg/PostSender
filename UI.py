from tkinter import *
import tkinter.messagebox as mb
from logic import *


def on_key_release(event):
    ctrl = (event.state & 0x4) != 0
    if event.keycode == 88 and ctrl and event.keysym.lower() != "x":
        event.widget.event_generate("<<Cut>>")

    if event.keycode == 86 and ctrl and event.keysym.lower() != "v":
        event.widget.event_generate("<<Paste>>")

    if event.keycode == 67 and ctrl and event.keysym.lower() != "c":
        event.widget.event_generate("<<Copy>>")


class MainWindow(Tk):

    def __init__(self):
        super().__init__()
        self.title("Бот постер")
        self.geometry('360x610')
        self.resizable(width=False, height=False)
        self.bind_all("<Key>", on_key_release, "+")
        self.edit_channel_button = Button(self, text="Редактировать целевой канал", width=27, height=1,
                                          font=('Arial', 16), command=self.open_channel_edit)
        self.edit_channel_button.pack(pady=5)
        self.edit_keywords_button = Button(self, text="Редактировать ключевые слова", width=27, height=1,
                                           font=('Arial', 16), command=self.open_keywords_edit)
        self.edit_keywords_button.pack(pady=5)
        self.edit_groups_button = Button(self, text="Редактировать ссылки на группы", width=27, height=1,
                                         font=('Arial', 16), command=self.open_groups_edit)
        self.edit_groups_button.pack(pady=5)
        self.info_label = Label(self, text="Двуфакторная авторизация\nна аккаунте должна быть\nвыключена!",
                                font=('Arial', 16), fg='#ff0000')
        self.info_label.pack(pady=5)
        self.login_label = Label(self, text="Логин Вконтакте:", font=('Arial', 16))
        self.login_label.pack(pady=5)
        self.login_entry = Entry(self, font=('Arial', 16))
        self.login_entry.pack(pady=5)
        account = read_file('Account.txt')
        self.password_label = Label(self, text="Пароль Вконтакте:", font=('Arial', 16))
        self.password_label.pack(pady=5)
        self.password_entry = Entry(self, font=('Arial', 16))
        self.password_entry.pack(pady=5)
        if len(account) > 1:
            self.login_entry.insert(END, account[0].strip())
            self.password_entry.insert(END, account[1].strip())
        self.token_label = Label(self, text="Токен телеграм:", font=('Arial', 16))
        self.token_label.pack(pady=5)
        self.token_entry = Entry(self, width=58, font=('Arial', 8))
        self.token_entry.pack(pady=5)
        token = read_file('TgToken.txt')
        if len(token) > 0:
            self.token_entry.insert(END, token[0].strip())
        self.count_label = Label(self, text="Сколько постов собирать:", font=('Arial', 16))
        self.count_label.pack(pady=5)
        self.count_entry = Entry(self, font=('Arial', 16))
        self.count_entry.pack(pady=5)
        self.start_button = Button(self, text="Запуск", width=27, height=1, font=('Arial', 16),
                                   command=lambda: start_bot(self.login_entry.get(), self.password_entry.get(),
                                                             self.token_entry.get(), self.count_entry.get()))
        self.start_button.pack(pady=5)

    def open_channel_edit(self):
        channel_edit = ChannelEdit(self)
        channel_edit.grab_set()

    def open_keywords_edit(self):
        keywords_edit = KeywordsEdit(self)
        keywords_edit.grab_set()

    def open_groups_edit(self):
        groups_edit = GroupsEdit(self)
        groups_edit.grab_set()


class ChannelEdit(Toplevel):

    def __init__(self, parent):
        super().__init__(parent)
        self.protocol("WM_DELETE_WINDOW", self.confirm_delete)
        self.title("Изменение целевого канала")
        self.geometry('360x140')
        self.resizable(width=False, height=False)
        self.chat_label = Label(self, text="Id чата телеграм:", font=('Arial', 16))
        self.chat_label.pack(pady=5)
        self.chat_entry = Entry(self, width=20, font=('Arial', 16))
        self.chat_entry.pack(pady=5)
        chat_id = read_file('TgChatId.txt')
        if len(chat_id) > 0:
            self.chat_entry.insert(END, chat_id[0].strip())
        self.save_button = Button(self, text="Сохранить", width=27, height=1, font=('Arial', 16),
                                  command=lambda: self.save(self.chat_entry.get()))
        self.save_button.pack(pady=5)

    def save(self, text):
        text = text.strip()
        if edit_file('TgChatId.txt', text):
            showinfo(title="Успешно!", message="Сохранение прошло успешно!")
            self.destroy()

    def confirm_delete(self):
        message = "Вы уверены, что хотите закрыть это окно? Несохраненные данные будут утеряны!"
        if mb.askyesno(message=message, parent=self):
            self.destroy()


class KeywordsEdit(Toplevel):

    def __init__(self, parent):
        super().__init__(parent)
        self.protocol("WM_DELETE_WINDOW", self.confirm_delete)
        self.title("Изменение ключевых слов")
        self.geometry('360x500')
        self.resizable(width=False, height=False)
        self.info_label = Label(self, text="Введите ключевые слова. Каждое новое слово с новой строки.",
                                font=('Arial', 8), fg='#ff0000')
        self.info_label.pack(pady=5)
        self.keywords_label = Label(self, text="Ключевые слова:", font=('Arial', 16))
        self.keywords_label.pack(pady=5)
        self.keywords_text = Text(self, width=36, height=20, font=('Arial', 12))
        self.keywords_text.pack(pady=5)
        self.keywords_text.insert("1.0", ''.join(read_file('Keywords.txt')))
        self.save_button = Button(self, text="Сохранить", width=27, height=1, font=('Arial', 16),
                                  command=lambda: self.save(self.keywords_text.get("1.0", END)))
        self.save_button.pack(pady=5)

    def save(self, text):
        text = text.strip()
        if edit_file('Keywords.txt', text):
            showinfo(title="Успешно!", message="Сохранение прошло успешно!")
            self.destroy()

    def confirm_delete(self):
        message = "Вы уверены, что хотите закрыть это окно? Несохраненные данные будут утеряны!"
        if mb.askyesno(message=message, parent=self):
            self.destroy()


class GroupsEdit(Toplevel):

    def __init__(self, parent):
        super().__init__(parent)
        self.label = Label(self, text="Это всплывающее окно")
        self.protocol("WM_DELETE_WINDOW", self.confirm_delete)
        self.title("Изменение ссылок на группы")
        self.geometry('360x530')
        self.resizable(width=False, height=False)
        self.info_label = Label(self, text="Введите ссылки на группы. Каждая новая ссылка с новой строки.\n "
                                           "Ссылки должны быть в формате:\nhttps://vk.com/club1234, "
                                           "vk.com/club1234 или vk.com/public1234",
                                font=('Arial', 8), fg='#ff0000')
        self.info_label.pack(pady=5)
        self.groups_label = Label(self, text="Ссылки на группы:", font=('Arial', 12))
        self.groups_label.pack(pady=5)
        self.groups_text = Text(self, width=36, height=20, font=('Arial', 12))
        self.groups_text.pack(pady=5)
        self.groups_text.insert("1.0", ''.join(read_file('Groups.txt')))
        self.save_button = Button(self, text="Сохранить", width=27, height=1, font=('Arial', 16),
                                  command=lambda: self.save(self.groups_text.get("1.0", END)))
        self.save_button.pack(pady=5)

    def save(self, text):
        text = text.strip()
        if edit_file('Groups.txt', text):
            showinfo(title="Успешно!", message="Сохранение прошло успешно!")
            self.destroy()

    def confirm_delete(self):
        message = "Вы уверены, что хотите закрыть это окно? Несохраненные данные будут утеряны!"
        if mb.askyesno(message=message, parent=self):
            self.destroy()
