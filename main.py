import kivy
from kivy.app import App
from kivy.lang import Builder
from kivy.clock import Clock
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.screenmanager import ScreenManager, Screen
import sqlite3 as sl
from kivy.uix.button import Button
from kivy.uix.dropdown import DropDown
from kivy.base import runTouchApp
from kivy.uix.textinput import TextInput
import requests
import ssl

from kivy.uix.popup import Popup
from kivy.core.audio import SoundLoader

ssl._create_default_https_context = ssl.create_default_context()

Builder.load_string('''
<ScreenTwo>:
    text_in: text_in
    memberStatus: memberStatus
    BoxLayout:
        orientation: 'vertical'
        Label: 
            id: memberStatus
            text_size: self.width, None
            size_hint: 1, None
            height: self.texture_size[1]
            bold: True
            canvas.before: 
                Rectangle:
                    size: self.size
                    pos: self.pos
                    source: 'button_normal.png'
        TextInput:
            id: text_in
            multiline: False
            bold: True
            size_hint: 1, 0.4
            on_text_validate:
                root.process_barcode()  
        Button:
            text: 'Настройки'
            font_size: 40
            halign: 'right'
            color: 0,0,0,1
            on_press:
                root.manager.transition.direction = 'left'
                root.manager.current = 'settings'
        Button:
            text: 'Подгрузить решения'
            font_size: 40
            halign: 'right'
            color: 0,0,0,1
            on_release:
                root.test_API()
        
<SettingsScreen>:
    BoxLayout:
        orientation: 'vertical'
        Button:
            text: 'Сервер'
            font_size: 40
            halign: 'right'
            background_normal: 'Lable3.png'
        Button:
            text: 'Сканер'
            font_size: 40
            halign: 'right'
            background_normal: 'Lable3.png'
            on_press:
                root.manager.transition.direction = 'right'
                root.manager.current = 'screen_two' 
<Button>:
    background_normal: 'Lable10.png'  # Eg. A black button
    background_down: 'button1 prbutton_down.png'  # Eg. A white button
# Adding Label, Button to popup

    
<Popups>:
      
    Label:
        text: "ЗАГРУЖЕННО"
        size_hint: 0.6, 0.2
        pos_hint: {"x":0.2, "top":1}
        
<CustomDropDown>:
    Button:
        text: 'My first Item'
        size_hint_y: None
        height: 44
        on_release: root.select('item1')
    Label:
        text: 'Unselectable item'
        size_hint_y: None
        height: 44
    Button:
        text: 'My second Item'
        size_hint_y: None
        height: 44
        on_release: root.select('item2')
  
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

class CustomDropDown(DropDown):
    pass
class ScreenTwo(Screen):
    def process_barcode(self):
        global parcel_numb
        self.memberStatus.text = self.text_in.text
        self.text_in.text = ""
        #self.memberStatus.keyboard_mode = 'managed'
        #self.memberStatus.font_size = 60
        self.memberStatus.color = (1, 0, 0, 1)
        self.memberStatus.background_color = (1, 0, 0, 1)
        con = sl.connect('BAZA-TSD.db')
        parcel_numb = self.memberStatus.text
        try:
            with con:
                data = con.execute(
                    f"Select party_numb, custom_status_short, parcel_plomb_numb from baza where parcel_numb = '{parcel_numb}'").fetchone()
                print(data)
                party_numb = data[0]
                custom_status_short = data[1]
                parcel_plomb_numb = data[2]
                baza = con.execute("select count(*) from sqlite_master where type='table' and name='plomb_working'")
                for row in baza:
                    # если таких таблиц нет
                    if row[0] == 0:
                        # создаём таблицу
                        with con:
                            con.execute("""
                                                                    CREATE TABLE plomb_working (
                                                                    ID INTEGER PRIMARY KEY AUTOINCREMENT,
                                                                    party_numb VARCHAR(20),
                                                                    parcel_numb VARCHAR(20) NOT NULL UNIQUE ON CONFLICT REPLACE,
                                                                    parcel_plomb_numb VARCHAR(20),
                                                                    parcel_weight FLOAT,
                                                                    custom_status_short VARCHAR(8),
                                                                    goods,
                                                                    working_status
                                                                    );
                                                                """)
                row_isalready_in_plombsplomb_working = con.execute(
                    f"Select parcel_plomb_numb from plomb_working where parcel_plomb_numb = '{parcel_plomb_numb}'").fetchone()
                print(row_isalready_in_plombsplomb_working)
                if row_isalready_in_plombsplomb_working is None:
                    sqlite_plomb_query = """INSERT OR REPLACE INTO plomb_working (party_numb, parcel_numb, parcel_plomb_numb, parcel_weight, custom_status_short, goods) 
                                         SELECT party_numb, parcel_numb, parcel_plomb_numb, parcel_weight, custom_status_short, goods
                                         FROM baza
                                         WHERE parcel_plomb_numb = ? AND custom_status_short = ?"""
                    con.execute(sqlite_plomb_query, (parcel_plomb_numb, 'ИЗЪЯТИЕ'))
                else:
                    pass

                if custom_status_short is None:
                    self.memberStatus.text = "Посылка \nне найдена"
                    sound = SoundLoader.load('Snd_CancelIssue.wav')
                    sound.play()
                if custom_status_short == 'ВЫПУСК':
                    self.memberStatus.font_size = 55
                    self.memberStatus.color = (0, 1, 0, 1)
                    self.memberStatus.background_color = (1, 1, 0, 1)
                data_test_refus = con.execute(
                    "Select parcel_plomb_numb from plomb_working where working_status = ? and parcel_plomb_numb = ?",
                    ('Found', parcel_plomb_numb)).fetchall()
                print(data_test_refus)
                data_test_refus_all = con.execute(
                    "Select parcel_plomb_numb from plomb_working where parcel_plomb_numb = ?",
                    (parcel_plomb_numb,)).fetchall()
                print(data_test_refus_all)
                quont_done_refus = len(data_test_refus)
                quont_all_refus = len(data_test_refus_all)
                if custom_status_short == 'ИЗЪЯТИЕ':
                    con.execute("Update plomb_working set working_status = 'Found' where parcel_numb = ?", (parcel_numb,))
                    sound = SoundLoader.load('Snd_CancelIssue.wav')
                    sound.play()
                    data_test_refus = con.execute(
                        "Select parcel_plomb_numb from plomb_working where working_status = ? and parcel_plomb_numb = ?",
                        ('Found', parcel_plomb_numb)).fetchall()
                    quont_done_refus = len(data_test_refus)
                    self.memberStatus.font_size = 55
                    self.memberStatus.color = (1, 0, 0, 1)
                    if quont_done_refus == quont_all_refus:
                        sound = SoundLoader.load('ll_refuse_find.wav')
                        sound.play()
                self.memberStatus.text = 'Плм:' + parcel_plomb_numb + '\n' + parcel_numb + '\n' + custom_status_short + '\n' + '(' + str(quont_done_refus) + '-' + str(quont_all_refus) + ')'
        except Exception as e:
            sound = SoundLoader.load('Snd_CancelIssue.wav')
            sound.play()
            #self.memberStatus.font_size = 30
            self.memberStatus.text = f"{parcel_numb} \nПосылка \nне найдена {e}"
        Clock.schedule_once(lambda *args: setattr(self.text_in, 'focus', True))  #(self.text_in, 'focus', True

    def test_API(self):
        global parcel_numb
        try:
            body = {'parcel_numb': f'{parcel_numb}'}
            print(body)
            response = requests.post('http://164.132.182.145:5001/api/get_decisions_TSD',
                                     json=body)  # http://127.0.0.1:5001  # 'http://164.132.182.145:5001/api/get_decisions_TSD'

            sound = SoundLoader.load('otvet_poluchen.wav')
            sound.play()
            con = sl.connect('BAZA-TSD.db')
            try:
                json_decisions = response.json()
                print(json_decisions)
                #data = json.load(json_decisions)
                with con:
                    for item in json_decisions:
                        con.execute("INSERT INTO baza (party_numb, parcel_numb, parcel_plomb_numb, custom_status_short,"
                                    "custom_status, decision_date, refuse_reason) "
                                    "VALUES (?, ?, ?, ?, ?, ?, ?)",
                                     (item["party_numb"], item["parcel_numb"], item["parcel_plomb_numb"],
                                      item["custom_status_short"], item["custom_status"], item["decision_date"],
                                      item["refuse_reason"]))
                show_popup('Готово!')
                sound = SoundLoader.load('esheniya_zagruzhenu.wav')
                sound.play()
            except Exception as e:
                sound = SoundLoader.load('Ne_udalos_zagruzit.wav')
                sound.play()
                print(e)
        except Exception as e:
            sound = SoundLoader.load('net_otveta_ot_servera.wav')
            sound.play()
            print(e)
class Popups(BoxLayout):
    pass

class SettingsScreen(Screen):
    pass
def show_popup(msg):
    show = Popups()

    popupWindow = Popup(title=msg, content=show,
                        size_hint=(None, None), size=(200, 200))

    # open popup window
    popupWindow.open()

dropdown = CustomDropDown()
mainbutton = Button(text='Hello', size_hint=(None, None))
mainbutton.bind(on_release=dropdown.open)
dropdown.bind(on_select=lambda instance, x: setattr(mainbutton, 'text', x))

class MyApp(App):
    def test_API(self, instance):
        global parcel_numb
        try:
            body = {'parcel_numb': f'{parcel_numb}'}
            print(body)
            response = requests.post('http://164.132.182.145:5001/api/get_decisions_TSD',
                                     json=body)  # http://127.0.0.1:5001  # 'http://164.132.182.145:5001/api/get_decisions_TSD'

            sound = SoundLoader.load('otvet_poluchen.wav')
            sound.play()
            con = sl.connect('BAZA-TSD.db')
            try:
                json_decisions = response.json()
                print(json_decisions)
                #data = json.load(json_decisions)
                with con:
                    for item in json_decisions:
                        con.execute("INSERT INTO baza (party_numb, parcel_numb, parcel_plomb_numb, custom_status_short,"
                                    "custom_status, decision_date, refuse_reason) "
                                    "VALUES (?, ?, ?, ?, ?, ?, ?)",
                                     (item["party_numb"], item["parcel_numb"], item["parcel_plomb_numb"],
                                      item["custom_status_short"], item["custom_status"], item["decision_date"],
                                      item["refuse_reason"]))
                show_popup('Готово!')
                sound = SoundLoader.load('esheniya_zagruzhenu.wav')
                sound.play()
            except Exception as e:
                sound = SoundLoader.load('Ne_udalos_zagruzit.wav')
                sound.play()
                print(e)
        except Exception as e:
            sound = SoundLoader.load('net_otveta_ot_servera.wav')
            sound.play()
            print(e)
    def build(self):
        sm = ScreenManager()
        sm.add_widget(ScreenTwo(name="screen_two"))
        bl = BoxLayout(orientation='vertical')
        gl = GridLayout(cols=2, size_hint=(1, .2))
        bl.add_widget(ScreenTwo(name="screen_two"))
        gl.add_widget(Button(text='Подгрузить решения',
                             on_release=self.test_API,
                             size_hint=(.6, .3),
                             font_size=20,
                             halign='right'))

        #gl.add_widget(TextInput(size_hint=(.3, .3), multiline=False, on_text_validate=self.test_API))
        bl.add_widget(gl)
        bl.add_widget(mainbutton)
        sm.add_widget(SettingsScreen(name='settings'))
        return bl and sm



if __name__ == '__main__':
    MyApp().run()