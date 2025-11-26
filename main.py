import streamlit as st
import json
import random

# Настройка страницы
st.set_page_config(
    page_title="Химический справочник",
    page_icon="🧪",
    layout="wide",
    initial_sidebar_state="expanded"
)


# Загрузка данных элементов
@st.cache_data
def load_elements():
    try:
        with open('chemical_elements.json', 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        st.error("❌ Файл chemical_elements.json не найден!")
        return {}


# Функция для определения цвета элемента
def get_element_color(element_type, symbol, number):
    colors = {
        "Неметалл": "#FFE4E1",
        "Благородный газ": "#E6E6FA",
        "Металл": "#F0FFF0",
        "Щелочной металл": "#FFF0F5",
        "Щелочноземельный металл": "#F5F5DC",
        "Переходный металл": "#F0F8FF",
        "Полуметалл": "#FFFACD",
        "Лантаноид": "#E6FFE6",
        "Актиноид": "#FFE6E6",
        "Постпереходный металл": "#F0F0FF"
    }

    if symbol == "H":
        return "#E0FFFF"
    elif 57 <= number <= 71:  # Лантаноиды
        return colors.get("Лантаноид", "#E6FFE6")
    elif 89 <= number <= 103:  # Актиноиды
        return colors.get("Актиноид", "#FFE6E6")
    return colors.get(element_type, "#F8F8FF")


# Создание таблицы Менделеева - ИСПРАВЛЕННАЯ ВЕРСИЯ
def create_periodic_table_layout(elements_data):
    # Создаем таблицу 10x18 (основная + лантаноиды/актиноиды)
    table = [[None for _ in range(18)] for _ in range(10)]

    # Позиции элементов в таблице
    positions = {
        # Период 1
        1: (0, 0), 2: (0, 17),
        # Период 2
        3: (1, 0), 4: (1, 1), 5: (1, 12), 6: (1, 13), 7: (1, 14),
        8: (1, 15), 9: (1, 16), 10: (1, 17),
        # Период 3
        11: (2, 0), 12: (2, 1), 13: (2, 12), 14: (2, 13), 15: (2, 14),
        16: (2, 15), 17: (2, 16), 18: (2, 17),
        # Период 4
        19: (3, 0), 20: (3, 1), 21: (3, 2), 22: (3, 3), 23: (3, 4),
        24: (3, 5), 25: (3, 6), 26: (3, 7), 27: (3, 8), 28: (3, 9),
        29: (3, 10), 30: (3, 11), 31: (3, 12), 32: (3, 13), 33: (3, 14),
        34: (3, 15), 35: (3, 16), 36: (3, 17),
        # Период 5
        37: (4, 0), 38: (4, 1), 39: (4, 2), 40: (4, 3), 41: (4, 4),
        42: (4, 5), 43: (4, 6), 44: (4, 7), 45: (4, 8), 46: (4, 9),
        47: (4, 10), 48: (4, 11), 49: (4, 12), 50: (4, 13), 51: (4, 14),
        52: (4, 15), 53: (4, 16), 54: (4, 17),
        # Период 6
        55: (5, 0), 56: (5, 1),
        # Лантаноиды (отдельная строка)
        57: (8, 2), 58: (8, 3), 59: (8, 4), 60: (8, 5), 61: (8, 6),
        62: (8, 7), 63: (8, 8), 64: (8, 9), 65: (8, 10), 66: (8, 11),
        67: (8, 12), 68: (8, 13), 69: (8, 14), 70: (8, 15), 71: (8, 16),
        # Продолжение периода 6
        72: (5, 2), 73: (5, 3), 74: (5, 4), 75: (5, 5), 76: (5, 6),
        77: (5, 7), 78: (5, 8), 79: (5, 9), 80: (5, 10), 81: (5, 11),
        82: (5, 12), 83: (5, 13), 84: (5, 14), 85: (5, 15), 86: (5, 16),
        # Период 7
        87: (6, 0), 88: (6, 1),
        # Актиноиды (отдельная строка)
        89: (9, 2), 90: (9, 3), 91: (9, 4), 92: (9, 5), 93: (9, 6),
        94: (9, 7), 95: (9, 8), 96: (9, 9), 97: (9, 10), 98: (9, 11),
        99: (9, 12), 100: (9, 13), 101: (9, 14), 102: (9, 15), 103: (9, 16),
        # Продолжение периода 7
        104: (6, 2), 105: (6, 3), 106: (6, 4), 107: (6, 5), 108: (6, 6),
        109: (6, 7), 110: (6, 8), 111: (6, 9), 112: (6, 10), 113: (6, 11),
        114: (6, 12), 115: (6, 13), 116: (6, 14), 117: (6, 15), 118: (6, 16)
    }

    # Заполняем таблицу
    for symbol, element_data in elements_data.items():
        number = element_data["Порядковый номер"]
        if number in positions:
            period, group = positions[number]
            if period < len(table) and group < len(table[period]):
                table[period][group] = symbol

    return table


# Отображение таблицы с кликабельными ячейками
def show_periodic_table(elements_data):
    table = create_periodic_table_layout(elements_data)

    # Основная таблица (периоды 0-6)
    for period in range(7):  # 0-6 периоды
        cols = st.columns(18)
        for group in range(18):
            with cols[group]:
                element_symbol = table[period][group] if period < len(table) and group < len(table[period]) else None
                if element_symbol and element_symbol in elements_data:
                    element = elements_data[element_symbol]
                    color = get_element_color(element["Тип элемента"], element_symbol, element["Порядковый номер"])

                    # Создаем кликабельную ячейку
                    button_html = f"""
                    <div style="background-color: {color}; padding: 8px; margin: 2px; 
                             border-radius: 8px; text-align: center; cursor: pointer;
                             border: 2px solid #ccc; min-height: 70px; display: flex; 
                             flex-direction: column; justify-content: center; transition: all 0.2s;"
                         onmouseover="this.style.transform='scale(1.05)'; this.style.borderColor='#666';"
                         onmouseout="this.style.transform='scale(1)'; this.style.borderColor='#ccc';">
                        <div style="font-weight: bold; font-size: 18px;">{element_symbol}</div>
                        <div style="font-size: 11px; color: #666;">{element['Порядковый номер']}</div>
                        <div style="font-size: 10px; color: #888; margin-top: 2px;">{element['Название'][:10]}{'...' if len(element['Название']) > 10 else ''}</div>
                    </div>
                    """

                    if st.button(" ", key=f"btn_{element_symbol}_{period}_{group}",
                                 help=f"Нажмите для информации о {element['Название']}",
                                 use_container_width=True):
                        st.session_state.selected_element = element_symbol

                    st.markdown(button_html, unsafe_allow_html=True)
                else:
                    st.write("")

    # Лантаноиды (отдельная строка)
    st.markdown("---")
    st.write("**Лантаноиды:**")
    lanthanoid_cols = st.columns(15)
    for i in range(15):  # 15 лантаноидов
        with lanthanoid_cols[i]:
            element_symbol = table[8][i + 2] if 8 < len(table) and i + 2 < len(table[8]) else None
            if element_symbol and element_symbol in elements_data:
                element = elements_data[element_symbol]
                color = get_element_color(element["Тип элемента"], element_symbol, element["Порядковый номер"])

                button_html = f"""
                <div style="background-color: {color}; padding: 8px; margin: 2px; 
                         border-radius: 8px; text-align: center; cursor: pointer;
                         border: 2px solid #ccc; min-height: 70px; display: flex; 
                         flex-direction: column; justify-content: center; transition: all 0.2s;"
                     onmouseover="this.style.transform='scale(1.05)'; this.style.borderColor='#666';"
                     onmouseout="this.style.transform='scale(1)'; this.style.borderColor='#ccc';">
                    <div style="font-weight: bold; font-size: 18px;">{element_symbol}</div>
                    <div style="font-size: 11px; color: #666;">{element['Порядковый номер']}</div>
                    <div style="font-size: 10px; color: #888; margin-top: 2px;">{element['Название'][:10]}{'...' if len(element['Название']) > 10 else ''}</div>
                </div>
                """

                if st.button(" ", key=f"lanth_{element_symbol}",
                             help=f"Нажмите для информации о {element['Название']}",
                             use_container_width=True):
                    st.session_state.selected_element = element_symbol

                st.markdown(button_html, unsafe_allow_html=True)

    # Актиноиды (отдельная строка)
    st.write("**Актиноиды:**")
    actinoid_cols = st.columns(15)
    for i in range(15):  # 15 актиноидов
        with actinoid_cols[i]:
            element_symbol = table[9][i + 2] if 9 < len(table) and i + 2 < len(table[9]) else None
            if element_symbol and element_symbol in elements_data:
                element = elements_data[element_symbol]
                color = get_element_color(element["Тип элемента"], element_symbol, element["Порядковый номер"])

                button_html = f"""
                <div style="background-color: {color}; padding: 8px; margin: 2px; 
                         border-radius: 8px; text-align: center; cursor: pointer;
                         border: 2px solid #ccc; min-height: 70px; display: flex; 
                         flex-direction: column; justify-content: center; transition: all 0.2s;"
                     onmouseover="this.style.transform='scale(1.05)'; this.style.borderColor='#666';"
                     onmouseout="this.style.transform='scale(1)'; this.style.borderColor='#ccc';">
                    <div style="font-weight: bold; font-size: 18px;">{element_symbol}</div>
                    <div style="font-size: 11px; color: #666;">{element['Порядковый номер']}</div>
                    <div style="font-size: 10px; color: #888; margin-top: 2px;">{element['Название'][:10]}{'...' if len(element['Название']) > 10 else ''}</div>
                </div>
                """

                if st.button(" ", key=f"actin_{element_symbol}",
                             help=f"Нажмите для информации о {element['Название']}",
                             use_container_width=True):
                    st.session_state.selected_element = element_symbol

                st.markdown(button_html, unsafe_allow_html=True)


# Отображение информации об элементе
def show_element_info(element_symbol, elements_data):
    if element_symbol not in elements_data:
        return

    element = elements_data[element_symbol]

    st.markdown("---")
    col1, col2 = st.columns([1, 2])

    with col1:
        st.markdown(f"# {element_symbol}")
        st.markdown(f"## {element['Название']}")

        st.metric("Порядковый номер", element["Порядковый номер"])
        st.metric("Атомная масса", f"{element['Атомная масса']:.3f}")
        st.metric("Тип элемента", element["Тип элемента"])

    with col2:
        st.subheader("📊 Свойства элемента")

        info_cols = st.columns(2)
        with info_cols[0]:
            st.write(f"**🔹 Валентность:** {', '.join(map(str, element['Валентность']))}")
            st.write(f"**🔹 Агрегатное состояние:** {element['Агрегатное состояние']}")
            st.write(f"**🔹 Внешний вид:** {element['Внешний вид']}")

        with info_cols[1]:
            st.write(f"**🔹 Степень окисления:** {', '.join(element['Степень окисления'])}")
            st.write(f"**🔹 Характер оксида:** {element['Характер оксида']}")

        st.write(f"**🔹 Электронная конфигурация:** `{element['Электронная конфигурация']}`")


# Режим тестирования
def show_test_mode(elements_data):
    st.header("🎯 Проверь свои знания")

    if 'test_data' not in st.session_state:
        st.session_state.test_data = {
            'score': 0,
            'total': 0,
            'current_question': None
        }

    level = st.radio(
        "**Выберите уровень сложности:**",
        ["🟢 Лёгкий", "🟡 Средний", "🔴 Сложный"],
        horizontal=True
    )

    level_key = level.split()[1]

    col1, col2 = st.columns([1, 3])
    with col1:
        if st.button("🎲 Новый вопрос", use_container_width=True):
            element_symbol = random.choice(list(elements_data.keys()))
            element = elements_data[element_symbol]

            if level_key == "Лёгкий":
                question = f"Какой символ у элемента **{element['Название']}**?"
                other_elements = [k for k in elements_data.keys() if k != element_symbol]
                options = [element_symbol] + random.sample(other_elements, 3)
                correct_answer = element_symbol

            elif level_key == "Средний":
                question = f"Какая **валентность** у элемента **{element_symbol}**?"
                all_valencies = ['I', 'II', 'III', 'IV', 'V', 'VI', 'VII', '0']
                element_valencies = [str(v) for v in element['Валентность']]
                other_valencies = [v for v in all_valencies if v not in element_valencies]
                options = element_valencies + random.sample(other_valencies, 4 - len(element_valencies))
                correct_answer = element_valencies[0] if element_valencies else '0'

            else:
                question = f"Какая **электронная конфигурация** у **{element_symbol}**?"
                other_elements = [k for k in elements_data.keys() if k != element_symbol]
                options = [element['Электронная конфигурация']] + [
                    elements_data[random.choice(other_elements)]['Электронная конфигурация']
                    for _ in range(3)
                ]
                correct_answer = element['Электронная конфигурация']

            random.shuffle(options)
            st.session_state.test_data['current_question'] = {
                'question': question,
                'options': options,
                'correct': correct_answer,
                'element': element_symbol
            }

    if st.session_state.test_data['current_question']:
        question_data = st.session_state.test_data['current_question']

        st.markdown(f"### ❓ {question_data['question']}")

        selected_option = st.radio(
            "**Выберите ответ:**",
            question_data['options'],
            key="current_options"
        )

        col1, col2 = st.columns(2)
        with col1:
            if st.button("✅ Проверить ответ", use_container_width=True):
                st.session_state.test_data['total'] += 1

                if selected_option == question_data['correct']:
                    st.success("🎉 **Правильно!** Молодец!")
                    st.session_state.test_data['score'] += 1
                    st.balloons()
                else:
                    st.error(f"❌ **Неправильно!** Правильный ответ: **{question_data['correct']}**")

                st.markdown("---")
                show_element_info(question_data['element'], elements_data)

        with col2:
            if st.button("➡️ Следующий вопрос", use_container_width=True):
                st.session_state.test_data['current_question'] = None
                st.rerun()

    if st.session_state.test_data['total'] > 0:
        st.markdown("---")
        st.subheader("📈 Статистика")

        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Правильных ответов", st.session_state.test_data['score'])
        with col2:
            st.metric("Всего вопросов", st.session_state.test_data['total'])
        with col3:
            percentage = (st.session_state.test_data['score'] / st.session_state.test_data['total']) * 100
            st.metric("Успеваемость", f"{percentage:.1f}%")

        if st.button("🔄 Сбросить статистику"):
            st.session_state.test_data = {
                'score': 0,
                'total': 0,
                'current_question': None
            }
            st.rerun()


# Основная функция
def main():
    elements_data = load_elements()

    if not elements_data:
        st.stop()

    st.title("🧪 Химический справочник")
    st.markdown("**Интерактивная таблица Менделеева со всеми 118 элементами**")

    with st.sidebar:
        st.header("🧭 Навигация")
        app_mode = st.radio(
            "**Выберите режим:**",
            ["📚 Изучение таблицы", "🎯 Проверка знаний"]
        )

        st.markdown("---")
        st.header("ℹ️ О проекте")
        st.markdown("""
        Полная таблица Менделеева:
        - 📚 Изучение свойств
        - 🎯 Проверка знаний  
        - 🎨 Кликабельные ячейки
        - 📱 Адаптивный дизайн
        """)

        total_elements = len(elements_data)
        st.metric("Элементов в базе", total_elements)

    if app_mode == "📚 Изучение таблицы":
        show_periodic_table(elements_data)

        if 'selected_element' in st.session_state and st.session_state.selected_element:
            show_element_info(st.session_state.selected_element, elements_data)
        else:
            st.info("👆 **Нажмите на любой элемент в таблице, чтобы увидеть его свойства**")

    else:
        show_test_mode(elements_data)


if __name__ == "__main__":
    main()