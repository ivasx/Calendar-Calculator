import datetime
import dateparser
import re
import warnings
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.togglebutton import ToggleButton
from kivy.uix.popup import Popup
from kivy.uix.scrollview import ScrollView
from kivy.clock import Clock
from kivy.graphics import Color, RoundedRectangle
from kivy.uix.widget import Widget


def validate_date(date_str):
    date_str = date_str.strip()
    current_year = datetime.datetime.now().year

    def has_year_in_string(s):
        if re.search(r'\b\d{4}\b', s):
            return True
        parts = re.split(r'[ .-/]', s)
        if parts and re.match(r'^\d{2}$', parts[-1]) and len(parts) == 3:
            return True
        return False

    has_year = has_year_in_string(date_str)

    parsed = None
    if has_year:
        try:
            with warnings.catch_warnings():
                warnings.simplefilter("ignore", DeprecationWarning)
                parsed = dateparser.parse(date_str, languages=['uk'])
        except Exception:
            parsed = None

    if parsed:
        return parsed

    # Формат: цифра.цифра.цифра (день.місяць.рік або рік.місяць.день)
    match3 = re.match(r'^(\d{1,4})[ .-/](\d{1,2})[ .-/](\d{1,4})$', date_str)
    if match3:
        a, b, c = int(match3.group(1)), int(match3.group(2)), int(match3.group(3))

        if a > 31 and c <= 31:
            year, month, day = a, b, c
        elif c > 31 and a <= 31:
            day, month, year = a, b, c
        else:
            day, month, year = a, b, c

        if year < 100:
            year += 2000

        try:
            return datetime.datetime(year, month, day)
        except ValueError:
            try:
                return datetime.datetime(year, day, month)
            except ValueError:
                return None

    # Формат: день.місяць (без року)
    match2 = re.match(r'^(\d{1,2})[ .-/](\d{1,2})$', date_str)
    if match2:
        a, b = int(match2.group(1)), int(match2.group(2))

        if a > 12:
            day, month = a, b
        elif b > 12:
            day, month = b, a
        else:
            day, month = a, b

        year = current_year

        try:
            return datetime.datetime(year, month, day)
        except ValueError:
            return None

    # Формат: тільки день
    match1 = re.match(r'^(\d{1,2})$', date_str)
    if match1:
        day = int(match1.group(1))
        month = datetime.datetime.now().month
        year = current_year

        try:
            return datetime.datetime(year, month, day)
        except ValueError:
            return None

    # Остання спроба — через dateparser
    try:
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", DeprecationWarning)
            parsed = dateparser.parse(date_str, languages=['uk'])
            if parsed:
                return parsed
    except Exception:
        pass

    return None


def calculate_days_between(date1_str, date2_str):
    """Обчислює різницю в днях між двома датами"""
    date1 = validate_date(date1_str)
    date2 = validate_date(date2_str)

    if date1 and date2:
        diff = abs((date2 - date1).days)
        return f"{diff} днів"
    return "❌ Неправильні дати"


def get_weekday(date_str):
    """Повертає день тижня для заданої дати"""
    date = validate_date(date_str)
    if date:
        weekdays = ['Понеділок', 'Вівторок', 'Середа', 'Четвер', 'П\'ятниця', 'Субота', 'Неділя']
        return weekdays[date.weekday()]
    return "❌ Неправильна дата"


def calculate(expression):
    try:
        # Перевіряємо чи це обчислення різниці між датами
        if ' - ' in expression and expression.count(' - ') == 1 and not re.search(r'\d+\s*-\s*\d+$', expression):
            parts = expression.split(' - ')
            if len(parts) == 2:
                return calculate_days_between(parts[0].strip(), parts[1].strip())

        # Перевіряємо чи це запит дня тижня
        if expression.startswith('день:') or expression.startswith('day:'):
            date_part = expression.split(':', 1)[1].strip()
            return get_weekday(date_part)

        # Звичайне обчислення дат та чисел
        expression = re.sub(r'(\d)([+*/-])(\d)', r'\1 \2 \3', expression)
        expression = re.sub(r'([/.])', r' \1 ', expression)
        expression = re.sub(r'\s+', ' ', expression).strip()

        # Підтримка множення та ділення
        match = re.match(r'^(.+?)\s*([+\-*/])\s*(\d+(?:\.\d+)?)$', expression)
        if not match:
            return "❌ Формат: дата ± число / число ± число / дата1 - дата2"

        first_part, operation, second_part = match.groups()
        parsed_date = validate_date(first_part.strip())

        if parsed_date:
            try:
                days = float(second_part)
            except ValueError:
                return "❌ Другий операнд має бути числом"

            if operation == '+':
                result_date = parsed_date + datetime.timedelta(days=int(days))
                return result_date.strftime('%d.%m.%Y')
            elif operation == '-':
                result_date = parsed_date - datetime.timedelta(days=int(days))
                return result_date.strftime('%d.%m.%Y')
            else:
                return "❌ Для дат підтримуються лише '+' або '-'"
        else:
            try:
                first_number = float(first_part)
                second_number = float(second_part)
            except ValueError:
                return "❌ Неправильні числа або дата"

            if operation == '+':
                result = first_number + second_number
            elif operation == '-':
                result = first_number - second_number
            elif operation == '*':
                result = first_number * second_number
            elif operation == '/':
                if second_number == 0:
                    return "❌ Ділення на нуль"
                result = first_number / second_number
            else:
                return "❌ Невідомий оператор"

            # Форматуємо результат
            if result == int(result):
                return str(int(result))
            else:
                return f"{result:.2f}"

    except Exception as e:
        return f"❌ Помилка: {str(e)}"


class RoundedButton(Button):
    def __init__(self, bg_color=(0.2, 0.6, 1, 1), **kwargs):
        super().__init__(**kwargs)
        self.bg_color = bg_color
        self.bind(size=self.update_graphics, pos=self.update_graphics)

    def update_graphics(self, *args):
        self.canvas.before.clear()
        with self.canvas.before:
            Color(*self.bg_color)
            RoundedRectangle(pos=self.pos, size=self.size, radius=[10])


class HelpPopup(Popup):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.title = 'Допомога'
        self.size_hint = (0.9, 0.8)

        help_text = """
📅 КАЛЕНДАР-КАЛЬКУЛЯТОР

🔢 ОСНОВНІ ОПЕРАЦІЇ:
• Додавання/віднімання чисел: 5 + 3, 10 - 4
• Множення/ділення: 6 * 2, 15 / 3

📅 ОПЕРАЦІЇ З ДАТАМИ:
• Додати дні до дати: 15.12.2024 + 30
• Відняти дні від дати: 01.01.2025 - 10
• Різниця між датами: 25.12.2024 - 01.01.2024

🗓️ ФОРМАТИ ДАТ:
• Повна дата: 15.12.2024, 15/12/2024
• Без року: 15.12 (поточний рік)
• Тільки день: 15 (поточний місяць)

📍 ДОДАТКОВІ ФУНКЦІЇ:
• День тижня: день:15.12.2024
• Швидкі дати: Сьогодні, Завтра, Вчора

⏰ ПОТОЧНИЙ ЧАС відображається зверху

💡 ПРИКЛАДИ:
• сьогодні + 7 → дата через тиждень
• 01.01.2025 - 25.12.2024 → кількість днів
• день:25.12.2024 → день тижня
        """

        scroll = ScrollView()
        label = Label(text=help_text, text_size=(None, None), halign='left', valign='top')
        scroll.add_widget(label)
        self.content = scroll


class CalculatorLayout(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(orientation='vertical', padding=15, spacing=15, **kwargs)

        # Поточний час
        self.time_label = Label(
            text=datetime.datetime.now().strftime('%H:%M:%S | %d.%m.%Y'),
            font_size=18,
            size_hint=(1, 0.1),
            color=(0.3, 0.3, 0.3, 1)
        )
        self.add_widget(self.time_label)

        # Оновлюємо час кожну секунду
        Clock.schedule_interval(self.update_time, 1)

        # Поле вводу
        self.input = TextInput(
            hint_text='Введіть вираз або дату...',
            multiline=False,
            readonly=True,
            font_size=22,
            size_hint=(1, 0.15),
            background_color=(0.95, 0.95, 0.95, 1)
        )
        self.add_widget(self.input)

        # Результат
        self.result = Label(
            text='Результат: ',
            font_size=20,
            size_hint=(1, 0.15),
            color=(0.2, 0.7, 0.2, 1),
            text_size=(None, None),
            halign='center'
        )
        self.add_widget(self.result)

        # Швидкі дати
        quick_dates_layout = BoxLayout(orientation='horizontal', size_hint=(1, 0.12), spacing=10)

        today_btn = RoundedButton(text='Сьогодні', bg_color=(0.2, 0.7, 0.2, 1))
        today_btn.bind(on_press=lambda x: self.add_quick_date('сьогодні'))

        tomorrow_btn = RoundedButton(text='Завтра', bg_color=(0.2, 0.5, 0.8, 1))
        tomorrow_btn.bind(on_press=lambda x: self.add_quick_date('завтра'))

        yesterday_btn = RoundedButton(text='Вчора', bg_color=(0.8, 0.5, 0.2, 1))
        yesterday_btn.bind(on_press=lambda x: self.add_quick_date('вчора'))

        quick_dates_layout.add_widget(today_btn)
        quick_dates_layout.add_widget(tomorrow_btn)
        quick_dates_layout.add_widget(yesterday_btn)
        self.add_widget(quick_dates_layout)

        # Основна клавіатура
        self.keyboard = GridLayout(cols=4, spacing=8, size_hint=(1, 1.5))

        # Кнопки калькулятора з кольорами
        buttons_config = [
            ('7', (0.4, 0.4, 0.4, 1)), ('8', (0.4, 0.4, 0.4, 1)), ('9', (0.4, 0.4, 0.4, 1)), ('+', (1, 0.6, 0.2, 1)),
            ('4', (0.4, 0.4, 0.4, 1)), ('5', (0.4, 0.4, 0.4, 1)), ('6', (0.4, 0.4, 0.4, 1)), ('-', (1, 0.6, 0.2, 1)),
            ('1', (0.4, 0.4, 0.4, 1)), ('2', (0.4, 0.4, 0.4, 1)), ('3', (0.4, 0.4, 0.4, 1)), ('*', (1, 0.6, 0.2, 1)),
            ('0', (0.4, 0.4, 0.4, 1)), ('.', (0.4, 0.4, 0.4, 1)), ('/', (1, 0.6, 0.2, 1)), ('=', (0.2, 0.8, 0.2, 1)),
        ]

        for text, color in buttons_config:
            btn = RoundedButton(text=text, font_size=24, bg_color=color)
            btn.bind(on_press=self.on_button_press)
            self.keyboard.add_widget(btn)

        self.add_widget(self.keyboard)

        # Додаткові функції
        extra_layout = BoxLayout(orientation='horizontal', size_hint=(1, 0.2), spacing=10)

        clear_btn = RoundedButton(text='C', bg_color=(0.8, 0.2, 0.2, 1), font_size=20)
        clear_btn.bind(on_press=self.clear_input)

        backspace_btn = RoundedButton(text='←', bg_color=(0.6, 0.6, 0.6, 1), font_size=20)
        backspace_btn.bind(on_press=self.backspace)

        day_btn = RoundedButton(text='День:', bg_color=(0.5, 0.3, 0.8, 1), font_size=16)
        day_btn.bind(on_press=lambda x: self.add_text('день:'))

        help_btn = RoundedButton(text='?', bg_color=(0.3, 0.6, 0.9, 1), font_size=20)
        help_btn.bind(on_press=self.show_help)

        extra_layout.add_widget(clear_btn)
        extra_layout.add_widget(backspace_btn)
        extra_layout.add_widget(day_btn)
        extra_layout.add_widget(help_btn)

        self.add_widget(extra_layout)

        # Історія обчислень
        self.history = []

    def update_time(self, dt):
        self.time_label.text = datetime.datetime.now().strftime('%H:%M:%S | %d.%m.%Y')

    def add_quick_date(self, date_type):
        self.input.text += date_type

    def add_text(self, text):
        self.input.text += text

    def on_button_press(self, instance):
        text = instance.text
        if text == '=':
            self.calculate_result()
        else:
            self.input.text += text

    def clear_input(self, instance):
        self.input.text = ''
        self.result.text = 'Результат: '

    def backspace(self, instance):
        self.input.text = self.input.text[:-1]

    def calculate_result(self):
        expression = self.input.text.strip()
        if not expression:
            return

        result = calculate(expression)
        self.result.text = f'Результат: {result}'

        # Додаємо до історії
        self.history.append(f"{expression} = {result}")
        if len(self.history) > 50:  # Обмежуємо історію
            self.history.pop(0)

    def show_help(self, instance):
        popup = HelpPopup()
        popup.open()


class DateCalculatorApp(App):
    def build(self):
        self.title = 'Календар-Калькулятор'
        return CalculatorLayout()


if __name__ == '__main__':
    DateCalculatorApp().run()