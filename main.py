import streamlit as st
import json
import random
from auth_system_gsheets import show_login_page, show_user_profile, update_user_stats, get_user_stats

#Настройка страницы
st.set_page_config(
    page_title="Химический справочник",
    page_icon="🧪",
    layout="wide",
    initial_sidebar_state="expanded"
)

#Загрузка данных элементов
@st.cache_data
def load_elements():
    try:
        with open('chemical_elements.json', 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        st.error("❌ Файл chemical_elements.json не найден!")
        return {}

#Функция для определения цвета элемента 
def get_element_color(element_type, symbol, number):
    if symbol == "H":
        return "#E0FFFF"  #Голубо для неметаллов

    if symbol in ["He", "Ne", "Ar", "Kr", "Xe", "Rn", "Og"]:
        return "#E0FFFF"  #голубой для неметаллов

    metal_types = ["Металл", "Щелочной металл", "Щелочноземельный металл", 
                   "Переходный металл", "Лантаноид", "Актиноид", "Постпереходный металл"]
    
    if element_type in metal_types:
        return "#FFE4CC"  #Персиковый для металлов
    else:
        return "#E0FFFF"  #Голубой для неметаллов

# Упрощенная таблица Менделеева с компактными ячейками
def create_periodic_table_layout():
    positions = {
        #пр 1
        (0, 0): "H", (0, 17): "He",
        #пр 2
        (1, 0): "Li", (1, 1): "Be", (1, 12): "B", (1, 13): "C", (1, 14): "N",
        (1, 15): "O", (1, 16): "F", (1, 17): "Ne",
        #пр 3
        (2, 0): "Na", (2, 1): "Mg", (2, 12): "Al", (2, 13): "Si", (2, 14): "P",
        (2, 15): "S", (2, 16): "Cl", (2, 17): "Ar",
        #пр 4
        (3, 0): "K", (3, 1): "Ca", (3, 2): "Sc", (3, 3): "Ti", (3, 4): "V",
        (3, 5): "Cr", (3, 6): "Mn", (3, 7): "Fe", (3, 8): "Co", (3, 9): "Ni",
        (3, 10): "Cu", (3, 11): "Zn", (3, 12): "Ga", (3, 13): "Ge", (3, 14): "As",
        (3, 15): "Se", (3, 16): "Br", (3, 17): "Kr",
        #пр 5
        (4, 0): "Rb", (4, 1): "Sr", (4, 2): "Y", (4, 3): "Zr", (4, 4): "Nb",
        (4, 5): "Mo", (4, 6): "Tc", (4, 7): "Ru", (4, 8): "Rh", (4, 9): "Pd",
        (4, 10): "Ag", (4, 11): "Cd", (4, 12): "In", (4, 13): "Sn", (4, 14): "Sb",
        (4, 15): "Te", (4, 16): "I", (4, 17): "Xe",
        # Period 6
        (5, 0): "Cs", (5, 1): "Ba", 
        #латиноиды
        (5, 2): "Lu", (5, 3): "Hf", (5, 4): "Ta", (5, 5): "W", (5, 6): "Re",
        (5, 7): "Os", (5, 8): "Ir", (5, 9): "Pt", (5, 10): "Au", (5, 11): "Hg",
        (5, 12): "Tl", (5, 13): "Pb", (5, 14): "Bi", (5, 15): "Po", (5, 16): "At",
        (5, 17): "Rn",
        #пр 7
        (6, 0): "Fr", (6, 1): "Ra",
        #актиноиды
        (6, 2): "Lr", (6, 3): "Rf", (6, 4): "Db", (6, 5): "Sg", (6, 6): "Bh",
        (6, 7): "Hs", (6, 8): "Mt", (6, 9): "Ds", (6, 10): "Rg", (6, 11): "Cn",
        (6, 12): "Nh", (6, 13): "Fl", (6, 14): "Mc", (6, 15): "Lv", (6, 16): "Ts",
        (6, 17): "Og",
    }
    
    lanthanoids = ["La", "Ce", "Pr", "Nd", "Pm", "Sm", "Eu", "Gd", "Tb", "Dy", "Ho", "Er", "Tm", "Yb"]
    
    actinoids = ["Ac", "Th", "Pa", "U", "Np", "Pu", "Am", "Cm", "Bk", "Cf", "Es", "Fm", "Md", "No"]
    
    return positions, lanthanoids, actinoids

#Отображение компактной таблицы
def show_periodic_table(elements_data):
    positions, lanthanoids, actinoids = create_periodic_table_layout()
    
    #Основная таблица 7x18
    for period in range(7):
        cols = st.columns(18)
        for group in range(18):
            with cols[group]:
                if (period, group) in positions:
                    element_symbol = positions[(period, group)]
                    if element_symbol in elements_data:
                        element = elements_data[element_symbol]
                        #тип элемента больше не в структуре, используем словарь для цвета
                        element_type = "Неметалл"  # Базовое значение
                        #определяем тип для цвета на основе группы
                        if group in [0, 1]:  #щелочные и щелочноземельные металлы
                            element_type = "Металл"
                        elif 2 <= group <= 11:  #переходные металлы
                            element_type = "Переходный металл"
                        elif group >= 12 and element_symbol not in ["B", "C", "N", "O", "F", "Ne", "Si", "P", "S", "Cl", "Ar", "Ge", "As", "Se", "Br", "Kr"]:
                            element_type = "Металл"
                        
                        color = get_element_color(element_type, element_symbol, element["Порядковый номер"])
                        
                        #Создаем красивую ячейку с помощью HTML 
                        cell_html = f"""
                        <div style="
                            background-color: {color}; 
                            padding: 4px; 
                            margin: 1px; 
                            border-radius: 6px; 
                            text-align: center;
                            border: 1px solid #ccc; 
                            height: 65px; 
                            display: flex; 
                            flex-direction: column; 
                            justify-content: center;
                            transition: all 0.2s;">
                            <div style="font-weight: bold; font-size: 16px; line-height: 1.2;">{element_symbol}</div>
                            <div style="font-size: 10px; color: #666; line-height: 1.1;">{element['Порядковый номер']}</div>
                            <div style="font-size: 9px; color: #888; margin-top: 1px; line-height: 1.1;">
                                {element['Название'][:8]}{'...' if len(element['Название']) > 8 else ''}
                            </div>
                        </div>
                        """
                        
                        #Отображаем ячейку
                        st.markdown(cell_html, unsafe_allow_html=True)
                        
                        #Добавляю кнопку под ячейкой
                        if st.button(
                            " ",  #Пробел, чтобы кнопка была видимой, но минимальной
                            key=f"btn_{element_symbol}_{period}_{group}",
                            help=f"Нажмите для информации о {element['Название']}",
                            use_container_width=True
                        ):
                            st.session_state.selected_element = element_symbol
                            st.rerun()
                        
                        # Стилизую кнопку, чтобы она была аккуратной и невидимой
                        st.markdown(f"""
                        <style>
                        /* Стили для кнопки под ячейкой */
                        button[data-testid="baseButton-secondary"][aria-label="btn_{element_symbol}_{period}_{group}"] {{
                            background-color: white !important;
                            border: 1px solid #ddd !important;
                            color: transparent !important;
                            height: 25px !important;
                            min-height: 25px !important;
                            max-height: 25px !important;
                            padding: 0px 2px !important;
                            margin: 1px !important;
                            margin-top: 0px !important;
                            border-radius: 3px !important;
                            text-align: center !important;
                            font-size: 1px !important;
                            line-height: 1 !important;
                            transition: all 0.2s !important;
                            display: flex !important;
                            align-items: center !important;
                            justify-content: center !important;
                            opacity: 0.3 !important;
                        }}
                        
                        /* Hover эффект для кнопки становится немного заметнее */
                        button[data-testid="baseButton-secondary"][aria-label="btn_{element_symbol}_{period}_{group}"]:hover {{
                            opacity: 0.5 !important;
                            border-color: #999 !important;
                            background-color: #f8f8f8 !important;
                            transform: translateY(-1px) !important;
                            box-shadow: 0 1px 3px rgba(0,0,0,0.1) !important;
                        }}
                        
                        /* Активное состояние кнопки */
                        button[data-testid="baseButton-secondary"][aria-label="btn_{element_symbol}_{period}_{group}"]:active {{
                            transform: translateY(0px) !important;
                            box-shadow: none !important;
                            background-color: #eee !important;
                        }}
                        
                        /* Hover эффект для ячейки - меняется только при наведении на саму ячейку */
                        div[data-testid="column"]:nth-child({group+1}) div:first-child div:hover {{
                            transform: scale(1.03) !important;
                            border-color: #666 !important;
                            box-shadow: 0 0 5px rgba(0,0,0,0.1) !important;
                        }}
                        </style>
                        """, unsafe_allow_html=True)
                        
                    else:
                        st.write("")
                else:
                    # Пустая ячейка
                    st.markdown('<div style="height: 65px;"></div>', unsafe_allow_html=True)
    
    # Лантаноиды - компактный вид
    st.markdown("---")
    st.markdown("**Лантаноиды:**")
    lan_cols = st.columns(14)
    for i, symbol in enumerate(lanthanoids):
        with lan_cols[i]:
            if symbol in elements_data:
                element = elements_data[symbol]
                # Для лантаноидов используем цвет металлов
                color = get_element_color("Лантаноид", symbol, element["Порядковый номер"])
                
                # Создаем красивую ячейку для лантаноида
                cell_html = f"""
                <div style="
                    background-color: {color}; 
                    padding: 4px; 
                    margin: 1px; 
                    border-radius: 6px; 
                    text-align: center;
                    border: 1px solid #ccc; 
                    height: 65px; 
                    display: flex; 
                    flex-direction: column; 
                    justify-content: center;
                    transition: all 0.2s;">
                    <div style="font-weight: bold; font-size: 16px; line-height: 1.2;">{symbol}</div>
                    <div style="font-size: 10px; color: #666; line-height: 1.1;">{element['Порядковый номер']}</div>
                    <div style="font-size: 9px; color: #888; margin-top: 1px; line-height: 1.1;">
                        {element['Название'][:8]}{'...' if len(element['Название']) > 8 else ''}
                    </div>
                </div>
                """
                
                # Отображаем ячейку
                st.markdown(cell_html, unsafe_allow_html=True)
                
                # Добавляем аккуратную невидимую кнопку под ячейкой
                if st.button(
                    " ",
                    key=f"btn_lanth_{symbol}",
                    help=f"Нажмите для информации о {element['Название']}",
                    use_container_width=True
                ):
                    st.session_state.selected_element = symbol
                    st.rerun()
                
                # Стилизуем кнопку
                st.markdown(f"""
                <style>
                /* Стили для кнопки под ячейкой лантаноида */
                button[data-testid="baseButton-secondary"][aria-label="btn_lanth_{symbol}"] {{
                    background-color: white !important;
                    border: 1px solid #ddd !important;
                    color: transparent !important;
                    height: 25px !important;
                    min-height: 25px !important;
                    max-height: 25px !important;
                    padding: 0px 2px !important;
                    margin: 1px !important;
                    margin-top: 0px !important;
                    border-radius: 3px !important;
                    text-align: center !important;
                    font-size: 1px !important;
                    line-height: 1 !important;
                    transition: all 0.2s !important;
                    display: flex !important;
                    align-items: center !important;
                    justify-content: center !important;
                    opacity: 0.3 !important;
                }}
                
                button[data-testid="baseButton-secondary"][aria-label="btn_lanth_{symbol}"]:hover {{
                    opacity: 0.5 !important;
                    border-color: #999 !important;
                    background-color: #f8f8f8 !important;
                    transform: translateY(-1px) !important;
                    box-shadow: 0 1px 3px rgba(0,0,0,0.1) !important;
                }}
                
                button[data-testid="baseButton-secondary"][aria-label="btn_lanth_{symbol}"]:active {{
                    transform: translateY(0px) !important;
                    box-shadow: none !important;
                    background-color: #eee !important;
                }}
                
                /* Hover эффект для ячейки лантаноида */
                div[data-testid="column"]:nth-child({i+1}) div:first-child div:hover {{
                    transform: scale(1.03) !important;
                    border-color: #666 !important;
                    box-shadow: 0 0 5px rgba(0,0,0,0.1) !important;
                }}
                </style>
                """, unsafe_allow_html=True)
    
    # Актиноиды - компактный вид
    st.markdown("**Актиноиды:**")
    act_cols = st.columns(14)
    for i, symbol in enumerate(actinoids):
        with act_cols[i]:
            if symbol in elements_data:
                element = elements_data[symbol]
                # Для актиноидов используем цвет металлов
                color = get_element_color("Актиноид", symbol, element["Порядковый номер"])
                
                # Создаем красивую ячейку для актиноида
                cell_html = f"""
                <div style="
                    background-color: {color}; 
                    padding: 4px; 
                    margin: 1px; 
                    border-radius: 6px; 
                    text-align: center;
                    border: 1px solid #ccc; 
                    height: 65px; 
                    display: flex; 
                    flex-direction: column; 
                    justify-content: center;
                    transition: all 0.2s;">
                    <div style="font-weight: bold; font-size: 16px; line-height: 1.2;">{symbol}</div>
                    <div style="font-size: 10px; color: #666; line-height: 1.1;">{element['Порядковый номер']}</div>
                    <div style="font-size: 9px; color: #888; margin-top: 1px; line-height: 1.1;">
                        {element['Название'][:8]}{'...' if len(element['Название']) > 8 else ''}
                    </div>
                </div>
                """
                
                # Отображаем ячейку
                st.markdown(cell_html, unsafe_allow_html=True)
                
                # Добавляем аккуратную невидимую кнопку под ячейкой
                if st.button(
                    " ",
                    key=f"btn_actin_{symbol}",
                    help=f"Нажмите для информации о {element['Название']}",
                    use_container_width=True
                ):
                    st.session_state.selected_element = symbol
                    st.rerun()
                
                # Стилизуем кнопку
                st.markdown(f"""
                <style>
                /* Стили для кнопки под ячейкой актиноида */
                button[data-testid="baseButton-secondary"][aria-label="btn_actin_{symbol}"] {{
                    background-color: white !important;
                    border: 1px solid #ddd !important;
                    color: transparent !important;
                    height: 25px !important;
                    min-height: 25px !important;
                    max-height: 25px !important;
                    padding: 0px 2px !important;
                    margin: 1px !important;
                    margin-top: 0px !important;
                    border-radius: 3px !important;
                    text-align: center !important;
                    font-size: 1px !important;
                    line-height: 1 !important;
                    transition: all 0.2s !important;
                    display: flex !important;
                    align-items: center !important;
                    justify-content: center !important;
                    opacity: 0.3 !important;
                }}
                
                button[data-testid="baseButton-secondary"][aria-label="btn_actin_{symbol}"]:hover {{
                    opacity: 0.5 !important;
                    border-color: #999 !important;
                    background-color: #f8f8f8 !important;
                    transform: translateY(-1px) !important;
                    box-shadow: 0 1px 3px rgba(0,0,0,0.1) !important;
                }}
                
                button[data-testid="baseButton-secondary"][aria-label="btn_actin_{symbol}"]:active {{
                    transform: translateY(0px) !important;
                    box-shadow: none !important;
                    background-color: #eee !important;
                }}
                
                /* Hover эффект для ячейки актиноида */
                div[data-testid="column"]:nth-child({i+1}) div:first-child div:hover {{
                    transform: scale(1.03) !important;
                    border-color: #666 !important;
                    box-shadow: 0 0 5px rgba(0,0,0,0.1) !important;
                }}
                </style>
                """, unsafe_allow_html=True)


def show_element_info(element_symbol, elements_data):
    if element_symbol not in elements_data:
        return

    element = elements_data[element_symbol]

    st.markdown("---")
    
    # Три колонки
    col1, col2, col3 = st.columns([1, 1, 1])

    with col1:
        st.markdown(f"# {element_symbol}")
        st.markdown(f"## {element['Название']}")
        st.markdown("---")

        # Порядковый номер с иконкой
        st.markdown(f"**🔢 Порядковый номер:** {element['Порядковый номер']}")
        
        # Атомная масса с округлением - ИЗМЕНЕНИЕ 3: добавляем скобочки с информацией об округлении
        atomic_mass = element['Атомная масса']
        if isinstance(atomic_mass, (int, float)):
            # Специальная обработка для хлора (всегда 35.5)
            if element_symbol == "Cl":
                mass_display = "35.5"
                round_info = " (всегда 35.5)"
            elif atomic_mass == int(atomic_mass):
                mass_display = f"{int(atomic_mass)}"
                round_info = " (целое число)"
            else:
                # Определяем сколько знаков после запятой
                mass_str = str(atomic_mass)
                if '.' in mass_str:
                    decimal_places = len(mass_str.split('.')[1])
                    if decimal_places <= 3:
                        mass_display = f"{atomic_mass:.{decimal_places}f}"
                        round_info = f" (округлено до {decimal_places} знаков)"
                    else:
                        mass_display = f"{atomic_mass:.3f}"
                        round_info = " (округлено до 3 знаков)"
                else:
                    mass_display = f"{atomic_mass}"
                    round_info = " (целое число)"
        else:
            mass_display = str(atomic_mass)
            round_info = ""
        
        st.markdown(f"**⚖️ Относительная атомная масса:** {mass_display}{round_info}")
        
        # Тип элемента - определяем на основе группы в таблице
        element_type = "Неизвестно"
        element_number = element['Порядковый номер']
        
        # Простое определение типа для отображения (не для цвета)
        if element_number <= 2:
            if element_symbol == "H":
                element_type = "Неметалл"
            else:
                element_type = "Благородный газ"
        elif 3 <= element_number <= 10:
            if element_symbol in ["B", "C", "N", "O", "F", "Ne"]:
                element_type = "Неметалл"
            elif element_symbol in ["Li", "Be"]:
                element_type = "Металл"
        elif 11 <= element_number <= 18:
            if element_symbol in ["Na", "Mg", "Al"]:
                element_type = "Металл"
            else:
                element_type = "Неметалл"
        else:
            # Более сложные элементы - упрощённо
            if element_symbol in ["He", "Ne", "Ar", "Kr", "Xe", "Rn"]:
                element_type = "Благородный газ"
            elif element_symbol in ["B", "C", "Si", "N", "P", "As", "O", "S", "Se", "Te", "F", "Cl", "Br", "I", "At"]:
                element_type = "Неметалл"
            else:
                element_type = "Металл"
        
        type_icon = "⚪"
        if "металл" in element_type.lower():
            if "благород" in element_type.lower():
                type_icon = "🟣"
            else:
                type_icon = "🟠"
        elif "неметалл" in element_type.lower():
            type_icon = "🟢"
        elif "благородный газ" in element_type.lower():
            type_icon = "🟣"
        
        st.markdown(f"**{type_icon} Тип элемента:** {element_type}")

    with col2:
        st.subheader("📊 Характеристика элемента")
        st.markdown("---")
        
        # Валентность с проверкой
        valency = element.get('Валентность', [])
        if valency and valency[0] not in ["-", "", "0", 0]:
            # Фильтруем некорректные значения
            valid_valencies = [str(v) for v in valency if v not in ["-", ""] and str(v).strip()]
            if valid_valencies:
                valency_str = ', '.join(valid_valencies)
                st.markdown(f"**🔸 Валентность:** {valency_str}")
            else:
                st.markdown("**🔸 Валентность:** не указана")
        else:
            if valency and valency[0] in ["0", 0]:
                st.markdown("**🔸 Валентность:** 0 (инертный)")
            else:
                st.markdown("**🔸 Валентность:** не указана")
        
        # Степень окисления с цветовой маркировкой
        oxidation = element.get('Степень окисления', [])
        if oxidation:
            # Разделяем на положительные и отрицательные
            positive = []
            negative = []
            neutral = []
            
            for ox in oxidation:
                ox_str = str(ox).strip()
                if ox_str.startswith('+'):
                    positive.append(ox_str)
                elif ox_str.startswith('-'):
                    negative.append(ox_str)
                elif ox_str == '0':
                    neutral.append(ox_str)
                else:
                    # Если нет знака, но число
                    try:
                        num = float(ox_str)
                        if num > 0:
                            positive.append(f"+{int(num) if num.is_integer() else num}")
                        elif num < 0:
                            negative.append(str(num))
                        else:
                            neutral.append("0")
                    except:
                        positive.append(ox_str)
            
            oxidation_display = []
            if negative:
                oxidation_display.append(f"<span style='color:red'>{', '.join(negative)}</span>")
            if positive:
                oxidation_display.append(f"<span style='color:blue'>{', '.join(positive)}</span>")
            if neutral:
                oxidation_display.append(f"<span style='color:green'>{', '.join(neutral)}</span>")
            
            if oxidation_display:
                st.markdown(f"**🔸 Степень окисления:** {'; '.join(oxidation_display)}", unsafe_allow_html=True)
            else:
                st.markdown(f"**🔸 Степень окисления:** {', '.join(oxidation)}")
        else:
            st.markdown("**🔸 Степень окисления:** не указана")
        
        # Электронная конфигурация с форматированием
        electron_config = element.get('Электронная конфигурация', '')
        if electron_config:
            st.markdown(f"**🔸 Электронная конфигурация:**")
            # Форматируем верхние индексы
            formatted_config = electron_config
            # Заменяем цифры в верхнем регистре на верхние индексы
            for i in range(10):
                formatted_config = formatted_config.replace(f"{i}", f"{i}")
            
            st.markdown(f"`{formatted_config}`", unsafe_allow_html=True)
        else:
            st.markdown("**🔸 Электронная конфигурация:** не указана")
    
    with col3:
        st.subheader("🧪 Свойства соединений")
        st.markdown("---")
        
        # Формула простого вещества
        simple_formula = element.get('Формула простого вещества', {})
        if simple_formula and isinstance(simple_formula, dict):
            formula = simple_formula.get('Формула', '')
            description = simple_formula.get('Описание', '')
            if formula and formula != "—":
                st.markdown(f"**🔹 Формула простого вещества:**")
                st.markdown(f"**{formula}**")
                if description:
                    st.markdown(f"*{description[:100]}...*" if len(description) > 100 else f"*{description}*")
        
        # Высший оксид
        higher_oxide = element.get('Высший оксид', {})
        if higher_oxide and isinstance(higher_oxide, dict):
            oxide_formula = higher_oxide.get('Формула', '')
            oxide_nature = higher_oxide.get('Характер', '')
            if oxide_formula and oxide_formula != "—":
                # Добавляем иконку в зависимости от характера оксида
                oxide_icon = "🧪"  # по умолчанию
                if oxide_nature:
                    if "кислот" in oxide_nature.lower():
                        oxide_icon = "🧪"
                    elif "основ" in oxide_nature.lower():
                        oxide_icon = "🛡️"
                    elif "амфотер" in oxide_nature.lower():
                        oxide_icon = "⚖️"
                    elif "не образует" in oxide_nature.lower():
                        oxide_icon = "🚫"
                
                st.markdown(f"**🔹 {oxide_icon} Высший оксид:**")
                st.markdown(f"**{oxide_formula}**")
                if oxide_nature:
                    st.markdown(f"*Характер: {oxide_nature}*")
        
        # Летучее водородное соединение
        volatile_hydrogen = element.get('Летучее водородное соединение', {})
        if volatile_hydrogen and isinstance(volatile_hydrogen, dict):
            vh_formula = volatile_hydrogen.get('Формула', '')
            vh_description = volatile_hydrogen.get('Описание', '')
            if vh_formula and vh_formula != "—":
                st.markdown(f"**🔹 Летучее водородное соединение:**")
                st.markdown(f"**{vh_formula}**")
                if vh_description:
                    st.markdown(f"*{vh_description[:100]}...*" if len(vh_description) > 100 else f"*{vh_description}*")
    
    # Дополнительная информация (если нужно)
    st.markdown("---")
    
    # Проверка согласованности данных
    higher_oxide = element.get('Высший оксид', {})
    if isinstance(higher_oxide, dict) and "предположительно" in higher_oxide.get('Характер', '').lower():
        st.info("💡 *Характер оксида предположительный, так как элемент синтетический или малоизучен*")
    
    # Особые случаи
    special_cases = {
        "O": "Кислород является компонентом оксидов, сам по себе не имеет характера оксида",
        "F": "Фтор образует только OF₂, который является нетипичным оксидом",
        "H": "Вода (H₂O) не является типичным оксидом",
        "Xe": "Ксенон может образовывать оксиды в исключительных условиях",
        "Rn": "Радон радиоактивен, его оксиды практически не изучены"
    }
    
    if element_symbol in special_cases:
        st.warning(f"📝 **Примечание:** {special_cases[element_symbol]}")


# Режим тестирования с сохранением статистики 
def show_test_mode(elements_data):
    st.header("🎯 Проверь свои знания")
    
    # Инициализация сессии для теста
    if 'test_data' not in st.session_state:
        st.session_state.test_data = {
            'score': 0,
            'total': 0,
            'current_question': None,
            'current_level': None,
            'selected_elements': "Все элементы"
        }
    
    # ИЗМЕНЕНИЕ 2: Выбор элементов для тестирования
    st.subheader("📋 Выберите элементы для изучения")
    
    selection_options = [
        "Все элементы",
        "Элементы 1-24",
        "Элементы 25-50",
        "Элементы 51-75",
        "Элементы 76-100",
        "Элементы 101-118",
        "Металлы",
        "Неметаллы"
    ]
    
    selected_elements = st.selectbox(
        "**Какие элементы вы хотите изучить?**",
        selection_options,
        index=selection_options.index(st.session_state.test_data['selected_elements']) 
               if st.session_state.test_data['selected_elements'] in selection_options else 0
    )
    
    st.session_state.test_data['selected_elements'] = selected_elements
    
    # Получаем список элементов в зависимости от выбора
    available_elements = []
    
    if selected_elements == "Все элементы":
        available_elements = list(elements_data.keys())
    
    elif selected_elements == "Элементы 1-24":
        available_elements = [sym for sym in elements_data.keys() 
                            if 1 <= elements_data[sym]["Порядковый номер"] <= 24]
    
    elif selected_elements == "Элементы 25-50":
        available_elements = [sym for sym in elements_data.keys() 
                            if 25 <= elements_data[sym]["Порядковый номер"] <= 50]
    
    elif selected_elements == "Элементы 51-75":
        available_elements = [sym for sym in elements_data.keys() 
                            if 51 <= elements_data[sym]["Порядковый номер"] <= 75]
    
    elif selected_elements == "Элементы 76-100":
        available_elements = [sym for sym in elements_data.keys() 
                            if 76 <= elements_data[sym]["Порядковый номер"] <= 100]
    
    elif selected_elements == "Элементы 101-118":
        available_elements = [sym for sym in elements_data.keys() 
                            if 101 <= elements_data[sym]["Порядковый номер"] <= 118]
    
    elif selected_elements == "Неметаллы":
        # Список известных неметаллов
        nonmetals = ["H", "He", "B", "C", "N", "O", "F", "Ne", 
                    "Si", "P", "S", "Cl", "Ar", "Ge", "As", 
                    "Se", "Br", "Kr", "Sb", "Te", "I", "Xe", 
                    "At", "Rn"]
        available_elements = [sym for sym in nonmetals if sym in elements_data]
    
    elif selected_elements == "Металлы":
        # Все элементы, кроме неметаллов и благородных газов
        nonmetals_and_noble = ["H", "He", "B", "C", "N", "O", "F", "Ne", 
                              "Si", "P", "S", "Cl", "Ar", "Ge", "As", 
                              "Se", "Br", "Kr", "Sb", "Te", "I", "Xe", 
                              "At", "Rn"]
        available_elements = [sym for sym in elements_data.keys() if sym not in nonmetals_and_noble]
    
    # Показываем статистику выбора
    col1, col2 = st.columns(2)
    with col1:
        st.info(f"**Выбрано элементов:** {len(available_elements)}")
    with col2:
        st.info(f"**Режим:** {selected_elements}")
    
    st.markdown("---")
    
    # Уровень сложности
    level = st.radio(
        "**Выберите уровень сложности:**",
        ["🟢 Лёгкий", "🟡 Средний", "🔴 Сложный"],
        horizontal=True
    )
    
    level_key = level.split()[1]
    st.session_state.test_data['current_level'] = level_key
    
    col1, col2 = st.columns([1, 3])
    with col1:
        if st.button("🎲 Новый вопрос", use_container_width=True):
            if not available_elements:
                st.error("❌ Нет доступных элементов для выбранного режима!")
                return
            
            element_symbol = random.choice(available_elements)
            element = elements_data[element_symbol]

            if level_key == "Лёгкий":
                question = f"Какой символ у элемента **{element['Название']}**?"
                # Используем только доступные элементы для вариантов ответов
                other_elements = [k for k in available_elements if k != element_symbol]
                if len(other_elements) >= 3:
                    options = [element_symbol] + random.sample(other_elements, 3)
                else:
                    # Если доступных элементов мало, дополняем случайными из всех
                    all_other = [k for k in elements_data.keys() if k != element_symbol]
                    options = [element_symbol] + random.sample(all_other, 3)
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
                # Используем только доступные элементы для вариантов ответов
                other_elements = [k for k in available_elements if k != element_symbol]
                if len(other_elements) >= 3:
                    other_configs = [elements_data[sym]['Электронная конфигурация'] for sym in random.sample(other_elements, 3)]
                else:
                    # Если доступных элементов мало, дополняем случайными из всех
                    all_other = [k for k in elements_data.keys() if k != element_symbol]
                    other_configs = [elements_data[sym]['Электронная конфигурация'] for sym in random.sample(all_other, 3)]
                
                options = [element['Электронная конфигурация']] + other_configs
                correct_answer = element['Электронная конфигурация']

            random.shuffle(options)
            st.session_state.test_data['current_question'] = {
                'question': question,
                'options': options,
                'correct': correct_answer,
                'element': element_symbol
            }
            st.rerun()
    
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
                    
                    # Сохраняем статистику для зарегистрированных пользователей
                    if st.session_state.get("username") and st.session_state["username"] != "Гость":
                        update_user_stats(st.session_state["username"], 1, 1)
                else:
                    st.error(f"❌ **Неправильно!** Правильный ответ: **{question_data['correct']}**")
                    
                    # Сохраняем статистику для зарегистрированных пользователей
                    if st.session_state.get("username") and st.session_state["username"] != "Гость":
                        update_user_stats(st.session_state["username"], 0, 1)
                
                st.markdown("---")
                show_element_info(question_data['element'], elements_data)
        
        with col2:
            if st.button("➡️ Следующий вопрос", use_container_width=True):
                st.session_state.test_data['current_question'] = None
                st.rerun()
    
    # Отображение статистики
    if st.session_state.test_data['total'] > 0:
        st.markdown("---")
        st.subheader("📈 Статистика текущей сессии")
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Правильных ответов", st.session_state.test_data['score'])
        with col2:
            st.metric("Всего вопросов", st.session_state.test_data['total'])
        with col3:
            percentage = (st.session_state.test_data['score'] / st.session_state.test_data['total']) * 100
            st.metric("Успеваемость", f"{percentage:.1f}%")
        
        # Дополнительная информация о режиме
        st.info(f"**Режим изучения:** {selected_elements} | **Уровень:** {level_key}")
        
        # Показать общую статистику пользователя, если он зарегистрирован
        if st.session_state.get("username") and st.session_state["username"] != "Гость":
            user_stats = get_user_stats(st.session_state["username"])
            if user_stats and user_stats["total_questions"] > 0:
                st.markdown("---")
                st.subheader("📊 Общая статистика аккаунта")
                
                total_percentage = (user_stats["correct_answers"] / user_stats["total_questions"]) * 100
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Всего правильных", user_stats["correct_answers"])
                with col2:
                    st.metric("Всего вопросов", user_stats["total_questions"])
                with col3:
                    st.metric("Общая успеваемость", f"{total_percentage:.1f}%")
        
        if st.button("🔄 Сбросить статистику сессии"):
            st.session_state.test_data = {
                'score': 0,
                'total': 0,
                'current_question': None,
                'current_level': None,
                'selected_elements': selected_elements
            }
            st.rerun()

# Основная функция
def main():
    # Проверка авторизации
    if "logged_in" not in st.session_state:
        show_login_page()
        return
    
    # Загрузка данных элементов
    elements_data = load_elements()
    
    if not elements_data:
        st.error("❌ Не удалось загрузить данные элементов")
        st.stop()
    
    # Отображение основного интерфейса
    st.title("🧪 Химический справочник")
    st.markdown(f"**Добро пожаловать, {st.session_state['username']}!**")
    
    # Показ профиля в сайдбаре
    show_user_profile()
    
    with st.sidebar:
        st.markdown("---")
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
        - 👤 Система пользователей
        - 📊 Сохранение статистики
        """)
        
        total_elements = len(elements_data)
        st.metric("Элементов в базе", total_elements)
        
        if st.session_state.get("username") == "Гость":
            st.warning("⚠️ Вы вошли как гость. Статистика не сохраняется.")
    
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




