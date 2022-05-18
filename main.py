from tkinter import *
from tkinter import ttk, messagebox, Scrollbar
import pymysql
import runpy
import datetime


def clear():
    userentry.delete(0, END)
    passentry.delete(0, END)


def close():
    win.destroy()


def login():
    if user_name.get() == "" or password.get() == "":
        messagebox.showerror("Error", "Введите имя пользователя и пароль", parent=win)
    else:
        try:
            con = pymysql.connect(host="localhost", user="root", password="root", database="test2")
            cur = con.cursor()

            cur.execute("select * from user_information where username=%s and password = %s",
                        (user_name.get(), password.get()))
            row = cur.fetchone()

            if row == None:
                messagebox.showerror("Ошибка", "Неправильные имя пользователя/пароль", parent=win)

            else:
                cur.execute(
                    "update settings set value = %s where id = 1",
                    (
                        row[0]
                    ))
                con.commit()
                runpy.run_module(mod_name="recognizer2")
                cur.execute("select * from settings where id = 2")
                enter = cur.fetchone()
                if (enter[2] == 0):
                    raise Exception('Неуспешная авторизация')
                cur.execute("update settings set value = 0 where id = 2")
                con.commit()
                runpy.run_module(mod_name="real_time_video2")
                cur.execute("select * from settings where id = 2")
                enter = cur.fetchone()
                if (enter[2] == 0):
                    raise Exception('Неуспешная авторизация')
                cur.execute("update settings set value = 0 where id = 2")
                con.commit()
                cur.execute("update settings set value = 0 where id = 1")
                con.commit()
                cur.execute("insert into enters(user_id,datetime,action) values(%s,%s,%s)",
                            (row[0], datetime.datetime.now(), 'Вход в систему'))
                con.commit()
                close()
                deshboard()
            con.close()
        except Exception as es:
            messagebox.showerror("Ошибка", f"{str(es)}", parent=win)


def deshboard():
    def getList():
        con = pymysql.connect(host="localhost", user="root", password="root", database="test2")
        cur = con.cursor()

        cur.execute("select * from enters order by id desc")
        rows = cur.fetchall()
        con.commit()
        con.close()

        window = Tk()
        window.title('Список')
        window.geometry('510x235')

        game_frame = Frame(window)
        game_frame.pack()

        scrollbar = Scrollbar(window)
        scrollbar.pack(side="right", fill="y")

        my_game = ttk.Treeview(game_frame)

        my_game['columns'] = ('id', 'name', 'action', 'datetime')

        my_game.column("#0", width=0, stretch=NO)
        my_game.column("id", width=40)
        my_game.column("name", width=80)
        my_game.column("action", width=240)
        my_game.column("datetime", width=150)

        my_game.heading("#0", text="")
        my_game.heading("id", text="Id")
        my_game.heading("name", text="Имя")
        my_game.heading("action", text="Действие")
        my_game.heading("datetime", text="Время")

        for data in rows:
            con = pymysql.connect(host="localhost", user="root", password="root", database="test2")
            cur = con.cursor()
            cur.execute("select * from user_information where id = " + str(data[1]))
            user = cur.fetchone()
            my_game.insert(parent='', index='end', iid=data[0], text='',
                           values=(str(data[0]), str(user[1]), str(data[3]), str(data[2])))

        my_game.pack()

        window.mainloop()

    def emotion():
        runpy.run_module(mod_name="real_time_video")

    def recognition():
        runpy.run_module(mod_name="recognizer")

    des = Tk()
    des.title("Панель пользователя")
    des.maxsize(width=800, height=260)
    des.minsize(width=800, height=260)

    heading = Label(des, text=f"Имя пользователя: {user_name.get()}", font='Verdana 20 bold')
    heading.place(x=220, y=30)

    con = pymysql.connect(host="localhost", user="root", password="root", database="test2")
    cur = con.cursor()

    cur.execute("select * from user_information where username ='" + user_name.get() + "'")
    row = cur.fetchall()

    for data in row:
        first_name = Label(des, text=f"Имя : {data[1]}", font='Verdana 10 bold')
        first_name.place(x=20, y=100)

        last_name = Label(des, text=f"Фамилия : {data[2]}", font='Verdana 10 bold')
        last_name.place(x=20, y=130)

        age = Label(des, text=f"Возраст : {data[3]}", font='Verdana 10 bold')
        age.place(x=20, y=160)

        gender = Label(des, text=f"ID : {data[0]}", font='Verdana 10 bold')
        gender.place(x=250, y=100)

        city = Label(des, text=f"Город : {data[5]}", font='Verdana 10 bold')
        city.place(x=250, y=130)

        add = Label(des, text=f"Адрес : {data[6]}", font='Verdana 10 bold')
        add.place(x=250, y=160)

        btn = Button(des, text="Идентификация", font='Verdana 10 bold', width=20, command=recognition)
        btn.place(x=550, y=100)

        btn = Button(des, text="Распознавание эмоций", font='Verdana 10 bold', width=20, command=emotion)
        btn.place(x=550, y=130)

        btn = Button(des, text="Список действий", font='Verdana 10 bold', width=20, command=getList)
        btn.place(x=550, y=160)


def signup():
    def action():
        if first_name.get() == "" or last_name.get() == "" or age.get() == "" or city.get() == "" or add.get() == "" or user_name.get() == "" or password.get() == "" or very_pass.get() == "":
            messagebox.showerror("Ошибка", "Все поля обязательны", parent=winsignup)
        elif password.get() != very_pass.get():
            messagebox.showerror("Ошибка", "Пароль и подтверждение пароля должны быть одинаковы", parent=winsignup)
        else:
            try:
                con = pymysql.connect(host="localhost", user="root", password="root", database="test2")
                cur = con.cursor()
                cur.execute("select * from user_information where username=%s", user_name.get())
                row = cur.fetchone()
                if row != None:
                    messagebox.showerror("Ошибка", "Такой пользователь уже существует", parent=winsignup)
                else:
                    cur.execute(
                        "insert into user_information(first_name,last_name,age,gender,city,address,username,password) values(%s,%s,%s,%s,%s,%s,%s,%s)",
                        (
                            first_name.get(),
                            last_name.get(),
                            age.get(),
                            var.get(),
                            city.get(),
                            add.get(),
                            user_name.get(),
                            password.get()
                        ))
                    con.commit()
                    con.close()
                    runpy.run_module(mod_name="dataset2")
                    runpy.run_module(mod_name="trainer")
                    clear()
                    switch()

            except Exception as es:
                messagebox.showerror("Ошибка", f"Ошибка: {str(es)}", parent=winsignup)

    def switch():
        winsignup.destroy()

    def clear():
        first_name.delete(0, END)
        last_name.delete(0, END)
        age.delete(0, END)
        var.set("Male")
        city.delete(0, END)
        add.delete(0, END)
        user_name.delete(0, END)
        password.delete(0, END)
        very_pass.delete(0, END)

    winsignup = Tk()
    winsignup.title("Регистрация")
    winsignup.maxsize(width=500, height=600)
    winsignup.minsize(width=500, height=600)

    heading = Label(winsignup, text="Регистрация", font='Verdana 20 bold')
    heading.place(x=10, y=60)

    first_name = Label(winsignup, text="Имя :", font='Verdana 10 bold')
    first_name.place(x=10, y=130)

    last_name = Label(winsignup, text="Фамилия :", font='Verdana 10 bold')
    last_name.place(x=10, y=160)

    age = Label(winsignup, text="Возраст :", font='Verdana 10 bold')
    age.place(x=10, y=190)

    Gender = Label(winsignup, text="Пол :", font='Verdana 10 bold')
    Gender.place(x=10, y=220)

    city = Label(winsignup, text="Город :", font='Verdana 10 bold')
    city.place(x=10, y=260)

    add = Label(winsignup, text="Адрес :", font='Verdana 10 bold')
    add.place(x=10, y=290)

    user_name = Label(winsignup, text="Имя пользователя :", font='Verdana 10 bold')
    user_name.place(x=10, y=320)

    password = Label(winsignup, text="Пароль :", font='Verdana 10 bold')
    password.place(x=10, y=350)

    very_pass = Label(winsignup, text="Подтверждение пароля :", font='Verdana 10 bold')
    very_pass.place(x=10, y=380)

    first_name = StringVar()
    last_name = StringVar()
    age = IntVar(winsignup, value='0')
    var = StringVar()
    city = StringVar()
    add = StringVar()
    user_name = StringVar()
    password = StringVar()
    very_pass = StringVar()

    first_name = Entry(winsignup, width=40, textvariable=first_name)
    first_name.place(x=200, y=133)

    last_name = Entry(winsignup, width=40, textvariable=last_name)
    last_name.place(x=200, y=163)

    age = Entry(winsignup, width=40, textvariable=age)
    age.place(x=200, y=193)

    Radio_button_male = ttk.Radiobutton(winsignup, text='М', value="М", variable=var).place(x=200, y=220)
    Radio_button_female = ttk.Radiobutton(winsignup, text='Ж', value="Ж", variable=var).place(x=200, y=238)

    city = Entry(winsignup, width=40, textvariable=city)
    city.place(x=200, y=263)

    add = Entry(winsignup, width=40, textvariable=add)
    add.place(x=200, y=293)

    user_name = Entry(winsignup, width=40, textvariable=user_name)
    user_name.place(x=200, y=323)

    password = Entry(winsignup, width=40, textvariable=password)
    password.place(x=200, y=353)

    very_pass = Entry(winsignup, width=40, show="*", textvariable=very_pass)
    very_pass.place(x=200, y=383)

    btn_signup = Button(winsignup, text="Регистрация", font='Verdana 10 bold', command=action)
    btn_signup.place(x=200, y=413)

    btn_login = Button(winsignup, text="Очистить", font='Verdana 10 bold', command=clear)
    btn_login.place(x=200, y=453)

    sign_up_btn = Button(winsignup, text="Перейти к авторизации", command=switch)
    sign_up_btn.place(x=350, y=20)

    winsignup.mainloop()


win = Tk()
win.title("Авторизация")
win.maxsize(width=500, height=500)
win.minsize(width=500, height=500)

heading = Label(win, text="Авторизация", font='Verdana 25 bold')
heading.place(x=80, y=150)

username = Label(win, text="Имя пользователя :", font='Verdana 10 bold')
username.place(x=80, y=220)

userpass = Label(win, text="Пароль :", font='Verdana 10 bold')
userpass.place(x=80, y=260)

user_name = StringVar()
password = StringVar()

userentry = Entry(win, width=40, textvariable=user_name)
userentry.focus()
userentry.place(x=235, y=223)

passentry = Entry(win, width=40, show="*", textvariable=password)
passentry.place(x=235, y=260)

btn_login = Button(win, text="Авторизация", font='Verdana 10 bold', command=login)
btn_login.place(x=235, y=293)

btn_login = Button(win, text="Очистить", font='Verdana 10 bold', command=clear)
btn_login.place(x=235, y=333)

sign_up_btn = Button(win, text="Перейти к регистрации", command=signup)
sign_up_btn.place(x=350, y=20)

win.mainloop()
