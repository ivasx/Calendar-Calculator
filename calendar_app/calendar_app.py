import datetime
import dateparser
import re
import warnings
from decorators import *


@format_date
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
            # Прибираємо warning для dateparser
            with warnings.catch_warnings():
                warnings.simplefilter("ignore", DeprecationWarning)
                parsed = dateparser.parse(date_str, languages=['uk'])
        except Exception:
            parsed = None

    if parsed:
        return parsed

    # Формат: цифра цифра цифра (наприклад: 2025 12 12, 12 12 2025, тощо)
    match3 = re.match(r'^(\d{1,4})[ .-/](\d{1,2})[ .-/](\d{1,4})$', date_str)
    # Формат: цифра цифра (наприклад: 12 25)
    match2 = re.match(r'^(\d{1,2})[ .-/](\d{1,2})$', date_str)
    # Формат: одна цифра (наприклад: 15)
    match1 = re.match(r'^(\d{1,2})$', date_str)

    if match3:
        a, b, c = int(match3.group(1)), int(match3.group(2)), int(match3.group(3))

        # Логіка визначення року, місяця, дня
        if a > 31 and (c <= 31):
            year = a
            day = c
            month = b
        elif c > 31 and (a <= 31):
            year = c
            day = a
            month = b
        elif a > 12 and c > 12:  # обидва можуть бути днями
            # беремо середнє як місяць
            if b <= 12:
                day = a if a <= 31 else c
                month = b
                year = c if c > a else current_year
            else:
                return None
        else:
            # стандартний порядок день-місяць-рік
            day, month, year = a, b, c

        if year < 100:
            year += 2000

    elif match2:
        a, b = int(match2.group(1)), int(match2.group(2))

        # Якщо перше число > 12, то це день
        if a > 12:
            day, month, year = a, b, current_year
        # Якщо друге число > 12, то це день
        elif b > 12:
            day, month, year = b, a, current_year
        else:
            # обидва <= 12, припускаємо день-місяць
            day, month, year = a, b, current_year

    elif match1:
        # Одна цифра - припускаємо що це день поточного місяця
        day = int(match1.group(1))
        month = datetime.datetime.now().month
        year = current_year

    else:
        # Якщо нічого не підійшло, спробуємо dateparser без року
        try:
            with warnings.catch_warnings():
                warnings.simplefilter("ignore", DeprecationWarning)
                parsed = dateparser.parse(date_str, languages=['uk'])
                if parsed:
                    return parsed
        except Exception:
            pass

        return None

    # Перевіряємо валідність дати
    try:
        return datetime.datetime(year, month, day)
    except ValueError:
        # Якщо дата неправильна, спробуємо поміняти день і місяць місцями
        try:
            return datetime.datetime(year, day, month)
        except ValueError:
            return None


def calculate(expression):
    """
    Виконує обчислення з датами та числами.
    Приклади:
    - "15.09 + 10" -> додає 10 днів до 15 вересня
    - "15.09 - 5" -> віднімає 5 днів від 15 вересня
    - "5 + 3" -> звичайне додавання чисел
    """
    try:
        # Розділяємо вираз на частини
        parts = expression.split()
        if len(parts) != 3:
            return "Помилка: неправильний формат. Використовуйте формат: 'дата/число операція число'"

        first_part, operation, second_part = parts

        # Перевіряємо, чи перша частина є датою
        parsed_date = validate_date(first_part)

        if parsed_date:
            # Якщо перша частина - дата, друга має бути числом
            try:
                days = int(second_part)
            except ValueError:
                return "Помилка: другий операнд має бути числом"

            # Отримуємо datetime об'єкт (без форматування)
            date_obj = validate_date.__wrapped__(first_part)  # викликаємо оригінальну функцію без декоратора
            if not date_obj:
                return "Помилка: неправильна дата"

            if operation == '+':
                result_date = date_obj + datetime.timedelta(days=days)
                return result_date.strftime('%d.%m.%Y')
            elif operation == '-':
                result_date = date_obj - datetime.timedelta(days=days)
                return result_date.strftime('%d.%m.%Y')
            else:
                return "Помилка: підтримуються тільки операції + та -"

        else:
            # Якщо перша частина не дата, виконуємо звичайні математичні операції
            try:
                first_number = float(first_part)
                second_number = float(second_part)
            except ValueError:
                return "Помилка: неправильні числа або дата"

            if operation == '+':
                return first_number + second_number
            elif operation == '-':
                return first_number - second_number
            else:
                return "Помилка: підтримуються тільки операції + та -"

    except Exception as e:
        return f"Помилка: {str(e)}"


if __name__ == '__main__':
    print("Календарний калькулятор")
    print("Приклади використання:")
    print("- 15.09 + 10 (додати 10 днів до 15 вересня)")
    print("- 15.09 - 5 (відняти 5 днів від 15 вересня)")
    print("- 5 + 3 (звичайне додавання)")
    print("Введіть 'exit' для виходу\n")

    while True:
        try:
            user_input = input("Введіть вираз: ").strip()
            if user_input.lower() == 'exit':
                break
            if user_input:
                result = calculate(user_input)
                print(f"Результат: {result}")
        except KeyboardInterrupt:
            print("\nВихід...")
            break
        except EOFError:
            break