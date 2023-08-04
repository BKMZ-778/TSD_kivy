# Импорт всех классов
from kivy.app import App
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.boxlayout import BoxLayout
from kivy.core.window import Window

# Глобальные настройки
Window.size = (250, 200)
Window.clearcolor = (255 / 255, 186 / 255, 3 / 255, 1)
Window.title = "ТРЕК:"

class MyApp(App):

    # Создание всех виджетов (объектов)
    def __init__(self):
        super().__init__()
        self.label = Label(text='СКАНЕР')
        self.treck = Label(text='Трек')
        self.input_data = TextInput(hint_text='Сканируй:', multiline=False)
        self.input_data.bind(text=self.on_text)  # Добавляем обработчик события

    # Получаем данные и производит их конвертацию
    def on_text(self, *args):
        data = self.input_data.text
        self.treck.text = 'Трек: ' + str(data)

    # Основной метод для построения программы
    def build(self):
        # Все объекты будем помещать в один общий слой
        box = BoxLayout(orientation='vertical')
        box.add_widget(self.label)
        box.add_widget(self.input_data)
        box.add_widget(self.treck)

        return box


# Запуск проекта
if __name__ == "__main__":
    MyApp().run()