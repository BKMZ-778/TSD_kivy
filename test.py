import kivy
from kivy.app import App
from kivy.lang import Builder
from kivy.clock import Clock
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.screenmanager import ScreenManager, Screen
import sqlite3 as sl
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
import requests
from kivy.uix.popup import Popup

Builder.load_string('''
<ScreenTwo>:
    text_in: text_in
    memberStatus: memberStatus
    BoxLayout:
        orientation: 'vertical'
        Label: 
            id: memberStatus
            font_size: 60
        TextInput:
            id: text_in
            multiline: False
            size_hint: 1, 0.1
            on_text_validate:
                root.process_barcode()   

# Adding Label, Button to popup
<Popups>:

    Label:
        text: "ЗАГРУЖЕННО"
        size_hint: 0.6, 0.2
        pos_hint: {"x":0.2, "top":1}

    ''')
con = sl.connect('BAZA-TSD.db')
with con:
    baza = con.execute("select count(*) from sqlite_master where type='table' and name='baza'")
    for row in baza:
        # если таких таблиц нет
        if row[0] == 0:
            # создаём таблицу
            with con:
                con.execute("""
                                                        CREATE TABLE baza (
                                                        ID INTEGER PRIMARY KEY AUTOINCREMENT,
                                                        registration_numb VARCHAR(25),
                                                        party_numb VARCHAR(20),
                                                        parcel_numb VARCHAR(20) NOT NULL UNIQUE ON CONFLICT REPLACE,
                                                        parcel_plomb_numb VARCHAR(20),
                                                        parcel_weight FLOAT,
                                                        custom_status VARCHAR(400),
                                                        custom_status_short VARCHAR(8),
                                                        decision_date VARCHAR(20),
                                                        refuse_reason VARCHAR(400),
                                                        pallet VARCHAR(10),
                                                        zone VARCHAR(5),
                                                        VH_status VARCHAR(10),
                                                        goods
                                                        );
                                                    """)
    sqlite_insert_query = """INSERT INTO baza
                              (party_numb, parcel_numb, parcel_plomb_numb, custom_status_short)
                              VALUES
                              ('8700508-OZON-24', 'CEL7000012859CD', '6600012937', 'ВЫПУСК');"""
    con.execute(sqlite_insert_query)
    sqlite_insert_query = """INSERT INTO baza
                                              (party_numb, parcel_numb, parcel_plomb_numb, custom_status_short)
                                              VALUES
                                              ('8060108-CEL-82', '72773098-0005-1', '2200019062', 'ИЗЪЯТИЕ');"""
    con.execute(sqlite_insert_query)


class ScreenTwo(Screen):
    def process_barcode(self):
        global parcel_numb
        self.memberStatus.text = self.text_in.text
        self.text_in.text = ""
        # self.memberStatus.keyboard_mode = 'managed'
        self.memberStatus.font_size = 60
        self.memberStatus.color = (1, 0, 0, 1)
        self.memberStatus.background_color = (1, 0, 0, 1)
        con = sl.connect('BAZA-TSD.db')
        parcel_numb = self.memberStatus.text
        try:
            with con:
                data = con.execute(
                    f"Select custom_status_short from baza where parcel_numb = '{parcel_numb}'").fetchone()
                for row in data:
                    self.memberStatus.text = parcel_numb + '\n' + row
                if row is None:
                    self.memberStatus.text = "Посылка \nне найдена"
                if row == 'ВЫПУСК':
                    self.memberStatus.font_size = 50
                    self.memberStatus.color = (0, 1, 0, 1)
                    self.memberStatus.background_color = (1, 1, 0, 1)
                if row == 'ИЗЪЯТИЕ':
                    self.memberStatus.font_size = 50
                    self.memberStatus.color = (1, 0, 0, 1)
        except:
            self.memberStatus.text = f"{parcel_numb} \nПосылка \nне найдена"
        Clock.schedule_once(lambda *args: setattr(self.text_in, 'focus', True))  # (self.text_in, 'focus', True


class Popups(BoxLayout):
    pass


def show_popup():
    show = Popups()

    popupWindow = Popup(title="Popup Window", content=show,
                        size_hint=(None, None), size=(200, 200))

    # open popup window
    popupWindow.open()


class MyApp(App):

    def test_API(self, instance):
        global parcel_numb
        body = {'parcel_numb': f'{parcel_numb}'}
        print(body)
        response = requests.post('http://127.0.0.1:5001/api/get_decisions_TSD',
                                 json=body)  # http://127.0.0.1:5000  # 'http://164.132.182.145:5001/api/get_decisions_TSD'
        con = sl.connect('BAZA-TSD.db')
        try:
            json_decisions = response.json()
            print(json_decisions)
            # data = json.load(json_decisions)
            print(json_decisions)
            with con:
                for item in json_decisions:
                    con.execute("INSERT INTO baza (party_numb, parcel_numb, parcel_plomb_numb, custom_status_short,"
                                "custom_status, decision_date, refuse_reason) "
                                "VALUES (?, ?, ?, ?, ?, ?, ?)",
                                (item["party_numb"], item["parcel_numb"], item["parcel_plomb_numb"],
                                 item["custom_status_short"], item["custom_status"], item["decision_date"],
                                 item["refuse_reason"]))
            show_popup()

        except:
            print(response)

    def build(self):
        sm = ScreenManager()
        # sm.add_widget(ScreenTwo(name="screen_two"))
        bl = BoxLayout(orientation='vertical')
        gl = GridLayout(cols=2, size_hint=(1, .2))
        bl.add_widget(ScreenTwo(name="screen_two"))
        gl.add_widget(Button(text='Подгрузить решения',
                             on_press=self.test_API,
                             size_hint=(.3, .3),
                             font_size=20,
                             halign='right'))
        # gl.add_widget(TextInput(size_hint=(.3, .3), multiline=False, on_text_validate=self.test_API))
        bl.add_widget(gl)
        return bl


if __name__ == '__main__':
    MyApp().run()