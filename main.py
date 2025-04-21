import flet as ft
import matplotlib.pyplot as plt
import numpy as np
from io import BytesIO
import math
import base64

def main(page: ft.Page):
    page.title = "Калькулятор"
    page.window_width = 600
    page.window_height = 700
    page.padding = 20

    # Вкладки
    def change_tab(e):
        tab_content.content = tabs[tabs_view.selected_index]
        tab_content.update()

    tabs_view = ft.Tabs(
        selected_index=0,
        on_change=change_tab,
        tabs=[
            ft.Tab(text="Калькулятор"),
            ft.Tab(text="Уравнения"),
            ft.Tab(text="Графики"),
        ],
        expand=1,
    )

    # 1. Вкладка калькулятора
    def calculate(e):
        try:
            num1 = float(num1_field.value)
            num2 = float(num2_field.value)
            operation = operation_selector.value

            if operation == '+':
                result = num1 + num2
            elif operation == '-':
                result = num1 - num2
            elif operation == '*':
                result = num1 * num2
            elif operation == '/':
                if num2 == 0:
                    result = "Ошибка: деление на ноль"
                else:
                    result = num1 / num2

            calc_result.value = f"Результат: {result}"
            calc_result.color = ft.colors.GREEN
        except ValueError:
            calc_result.value = "Ошибка: введите числа"
            calc_result.color = ft.colors.RED
        calc_result.update()

    num1_field = ft.TextField(label="Первое число", width=200)
    num2_field = ft.TextField(label="Второе число", width=200)
    operation_selector = ft.Dropdown(    #выбор знака
        width=100,
        options=[
            ft.dropdown.Option("+"),
            ft.dropdown.Option("-"),
            ft.dropdown.Option("*"),
            ft.dropdown.Option("/"),
        ],
        value="+", # по умолчанию
    )
    calc_button = ft.ElevatedButton("Вычислить", on_click=calculate)
    calc_result = ft.Text("", size=20)

    calc_tab = ft.Column([
        ft.Row([num1_field, operation_selector, num2_field], alignment=ft.MainAxisAlignment.CENTER),
        ft.Row([calc_button], alignment=ft.MainAxisAlignment.CENTER),
        ft.Row([calc_result], alignment=ft.MainAxisAlignment.CENTER),
    ], spacing=20)

    # 2. Вкладка уравнений
    def solve_equation(e):
        try:
            if equation_type.value == "l":
                a = float(a_field.value)
                b = float(b_field.value)
                result = solve_linear(a, b)
            else:
                a = float(a_field.value)
                b = float(b_field.value)
                c = float(c_field.value)
                result = solve_quadratic(a, b, c)

            equation_result.value = f"Результат: {format_equation_result(result)}"
            equation_result.color = ft.colors.GREEN
        except ValueError:
            equation_result.value = "Ошибка: введите числа"
            equation_result.color = ft.colors.RED
        equation_result.update()

    def equation_type_changed(e):
        if equation_type.value == "l":
            c_field.visible = False
        else:
            c_field.visible = True
        page.update()  #обнова чтобы заработал квадрат

    def format_equation_result(result):
        type, roots = result
        if type == 'beskonechnost':
            return "Бесконечное количество решений"
        elif type == 'none':
            return "Нет решений"
        elif type == 'odin':
            return f"Один корень: {roots[0]}"
        else:
            return f"Два корня: {roots[0]} и {roots[1]}"

    equation_type = ft.Dropdown(
        width=150,
        options=[
            ft.dropdown.Option("l", text="Линейное"), #vubor
            ft.dropdown.Option("q", text="Квадратное"),
        ],
        value="l",
        on_change=equation_type_changed, #kvadrat
    )
    a_field = ft.TextField(label="Коэффициент a", width=150)
    b_field = ft.TextField(label="Коэффициент b", width=150)
    c_field = ft.TextField(label="Коэффициент c", width=150, visible=False)
    solve_button = ft.ElevatedButton("Решить", on_click=solve_equation)
    equation_result = ft.Text("", size=20)

    equation_tab = ft.Column([
        ft.Row([equation_type], alignment=ft.MainAxisAlignment.CENTER),
        ft.Row([a_field, b_field, c_field], alignment=ft.MainAxisAlignment.CENTER),
        ft.Row([solve_button], alignment=ft.MainAxisAlignment.CENTER),
        ft.Row([equation_result], alignment=ft.MainAxisAlignment.CENTER),
    ], spacing=20)

    # 3. Вкладка графиков
    # 3. Вкладка графиков
    def draw_function(e):
        try:
            func_text = function_field.value
            if not func_text:
                raise ValueError("Пустая функция")
            #СЛОВАРЬ МАТ ФУНКЦИЙ
            safe_dict = {
                'x': None,
            'np': np,  # Добавляем numpy как np
            'sin': np.sin,
            'cos': np.cos,
            'tan': np.tan,
            'asin': np.arcsin,
            'acos': np.arccos,
            'atan': np.arctan,
            'sinh': np.sinh,
            'cosh': np.cosh,
            'tanh': np.tanh,
            'log': np.log,
            'log10': np.log10,
            'log2': np.log2,
            'sqrt': np.sqrt,
            'exp': np.exp,
            'pi': np.pi,
            'e': np.e,
            'abs': np.abs,# модуль
            'ceil': np.ceil, #округление в <
            'floor': np.floor,#округление в >
            'degrees': np.degrees,
            'radians': np.radians,
            }
            func_text = func_text.replace('^', '**')
            # Безопасная проверка функции
            allowed_chars = set("x0123456789.+-*/^ (),:abcdefghijklmnopqrstuvwxyz_")
            if not all(c in allowed_chars for c in func_text):
                raise ValueError("Недопустимые символы в функции")

            # Создаем функцию
            def func(x):
                safe_dict['x'] = x
                return eval(func_text, {"__builtins__": None}, safe_dict) #преобразование строчки конвертироваться в лог. цепочку

            # Рисуем график
            fig, ax = plt.subplots()
            x = np.linspace(-10, 10, 100)
            y = func(x)
            ax.plot(x, y)
            ax.grid()
            ax.set_title(f"График функции: {func_text}")

            # Сохраняем в буфер
            buf = BytesIO()
            plt.savefig(buf, format="png", dpi=100)
            buf.seek(0)
            plt.close()

            # Отображаем изображение
            graph_image.src_base64 = base64.b64encode(buf.read()).decode("utf-8")
            graph_result.value = ""
            graph_result.color = ft.colors.GREEN
        except Exception as ex:
            graph_result.value = f"Ошибка: {str(ex)}"
            graph_result.color = ft.colors.RED
            graph_image.src_base64 = None
        finally:
            graph_result.update()
            graph_image.update()
    function_field = ft.TextField(label="Функция (например, x^2)", width=300)
    draw_button = ft.ElevatedButton("Нарисовать", on_click=draw_function)
    graph_result = ft.Text("", size=20)
    graph_image = ft.Image(width=500, height=400)

    graph_tab = ft.Column([
        ft.Row([function_field], alignment=ft.MainAxisAlignment.CENTER),
        ft.Row([draw_button], alignment=ft.MainAxisAlignment.CENTER),
        ft.Row([graph_result], alignment=ft.MainAxisAlignment.CENTER),
        ft.Row([graph_image], alignment=ft.MainAxisAlignment.CENTER),
    ], spacing=20, scroll=ft.ScrollMode.AUTO)

    def solve_linear(a, b):
        if a == 0:
            if b == 0:
                return ('beskonechnost', None)
            else:
                return ('none', None)
        else:
            return ('odin', [-b / a])

    def solve_quadratic(a, b, c):
        if a == 0:
            return solve_linear(b, c)
        discriminant = b ** 2 - 4 * a * c
        if discriminant < 0:
            return ('none', None)
        elif discriminant == 0:
            return ('odin', [-b / (2 * a)])
        D = discriminant ** 0.5
        return ('dva', sorted([(-b - D) / (2 * a), (-b + D) / (2 * a)]))

    # Содержимое вкладок
    tabs = [calc_tab, equation_tab, graph_tab]
    tab_content = ft.Container(content=calc_tab)

    # Основной интерфейс
    page.add(
        ft.Column([
            tabs_view,
            tab_content,
        ], spacing=20)
    )


# Запуск приложения
ft.app(main)