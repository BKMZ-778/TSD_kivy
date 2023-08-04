import kivy
from kivy.app import App
from kivy.lang import Builder
from kivy.clock import Clock
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.screenmanager import ScreenManager, Screen

Builder.load_string('''
<ScreenTwo>:
    text_in: text_in
    memberStatus: memberStatus
    BoxLayout:
        orientation: 'vertical'
        Label: 
            id: memberStatus
        TextInput:
            id: text_in
            multiline: False
            on_text_validate:
                root.process_barcode()
    ''')

class ScreenTwo(Screen):
    def process_barcode(self):
        self.memberStatus.text = self.text_in.text
        self.text_in.text = ""
        Clock.schedule_once(lambda *args: setattr(self.text_in, 'focus', True))

class MyApp(App):
    def build(self):
        sm = ScreenManager()
        sm.add_widget(ScreenTwo(name="screen_two"))
        return sm

if __name__ == '__main__':
    MyApp().run()