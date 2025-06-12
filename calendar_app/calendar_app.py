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

    match3 = re.match(r'^(\d{1,4})[ .-/](\d{1,2})[ .-/](\d{1,4})$', date_str)
    match2 = re.match(r'^(\d{1,2})[ .-/](\d{1,2})$', date_str)
    match1 = re.match(r'^(\d{1,2})$', date_str)

    if match3:
        a, b, c = int(match3.group(1)), int(match3.group(2)), int(match3.group(3))
        if a > 31 and (c <= 31):
            year, day, month = a, c, b
        elif c > 31 and (a <= 31):
            year, day, month = c, a, b
        elif a > 12 and c > 12:
            if b <= 12:
                day = a if a <= 31 else c
                month = b
                year = c if c > a else current_year
            else:
                return None
        else:
            day, month, year = a, b, c

        if year < 100:
            year += 2000

    elif match2:
        a, b = int(match2.group(1)), int(match2.group(2))
        if a > 12:
            day, month, year = a, b, current_year
        elif b > 12:
            day, month, year = b, a, current_year
        else:
            day, month, year = a, b, current_year

    elif match1:
        day = int(match1.group(1))
        month = datetime.datetime.now().month
        year = current_year

    else:
        try:
            with warnings.catch_warnings():
                warnings.simplefilter("ignore", DeprecationWarning)
                parsed = dateparser.parse(date_str, languages=['uk'])
                if parsed:
                    return parsed
        except Exception:
            pass
        return None

    try:
        return datetime.datetime(year, month, day)
    except ValueError:
        try:
            return datetime.datetime(year, day, month)
        except ValueError:
            return None


def calculate(expression):
    try:
        # Додаємо пробіли навколо оператора
        expression = re.sub(r'(\d)([+-])(\d)', r'\1 \2 \3', expression)
        expression = re.sub(r'([/.])', r' \1 ', expression)
        expression = re.sub(r'\s+', ' ', expression).strip()

        # Визначаємо частини виразу
        match = re.match(r'^(.+?)\s*([+-])\s*(\d+)$', expression)
        if not match:
            return "❌ Формат: дата + число / число + число"

        first_part, operation, second_part = match.groups()

        parsed_date = validate_date(first_part.strip())

        if parsed_date:
            try:
                days = int(second_part)
            except ValueError:
                return "❌ Другий операнд має бути числом"

            if operation == '+':
                result_date = parsed_date + datetime.timedelta(days=days)
                return result_date.strftime('%d.%m.%Y')
            elif operation == '-':
                result_date = parsed_date - datetime.timedelta(days=days)
                return result_date.strftime('%d.%m.%Y')
            else:
                return "❌ Підтримуються лише '+' або '-'"

        else:
            try:
                first_number = float(first_part)
                second_number = float(second_part)
            except ValueError:
                return "❌ Неправильні числа або дата"

            if operation == '+':
                return str(first_number + second_number)
            elif operation == '-':
                return str(first_number - second_number)
            else:
                return "❌ Підтримуються лише '+' або '-'"

    except Exception as e:
        return f"❌ Помилка: {str(e)}"


class CalculatorLayout(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(orientation='vertical', padding=10, spacing=10, **kwargs)

        self.input = TextInput(hint_text='Введіть вираз', multiline=False, readonly=True, font_size=24)
        self.result = Label(text='Результат: ', font_size=20, size_hint=(1, 0.3))

        self.add_widget(self.input)
        self.add_widget(self.result)

        self.keyboard = GridLayout(cols=4, spacing=5, size_hint=(1, 2))
        buttons = [
            '7', '8', '9', '+',
            '4', '5', '6', '-',
            '1', '2', '3', '.',
            '0', '/', ' ', 'C',
            '←', '=', '-', ' '
        ]

        for label in buttons:
            if label.strip():
                btn = Button(text=label, font_size=24, on_press=self.on_button_press)
            else:
                btn = Label()
            self.keyboard.add_widget(btn)

        self.add_widget(self.keyboard)

    def on_button_press(self, instance):
        text = instance.text
        if text == 'C':
            self.input.text = ''
            self.result.text = 'Результат: '
        elif text == '←':
            self.input.text = self.input.text[:-1]
        elif text == '=':
            result = calculate(self.input.text.strip())
            self.result.text = f'Результат: {result}'
        else:
            self.input.text += text


class DateCalculatorApp(App):
    def build(self):
        return CalculatorLayout()


if __name__ == '__main__':
    DateCalculatorApp().run()
