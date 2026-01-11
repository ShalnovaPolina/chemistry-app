# auth_system_gsheets.py
import streamlit as st
import gspread
from google.oauth2.service_account import Credentials
import hashlib
from datetime import datetime
import json

# ==================== НАСТРОЙКА GOOGLE SHEETS ====================

# 1. Области доступа (разрешения)
SCOPE = [
    "https://www.googleapis.com/auth/spreadsheets",  # Доступ к таблицам
    "https://www.googleapis.com/auth/drive.file"     # Доступ к файлам
]

# 2. ID вашей Google таблицы (ЗАМЕНИТЕ НА СВОЙ!)
# Как найти: откройте таблицу → адресная строка → часть между /d/ и /edit
SPREADSHEET_ID = "16eAX7om2gzcttvDGUMKa_xwOSwsowOq7QOiLH01zI2k"

# 3. Название листа (вкладки) в таблице
SHEET_NAME = "Пользователи"

# ==================== ФУНКЦИИ ДЛЯ РАБОТЫ С GOOGLE SHEETS ====================

def get_gsheet_client():
    """Подключение к Google Sheets"""
    try:
        # Способ 1: Чтение из Streamlit Secrets (для облачного хостинга)
        if 'google_credentials' in st.secrets:
            creds_dict = dict(st.secrets["google_credentials"])
            credentials = Credentials.from_service_account_info(creds_dict, scopes=SCOPE)
        
        # Способ 2: Чтение из файла (для локальной разработки)
        else:
            credentials = Credentials.from_service_account_file(
                "credentials.json", 
                scopes=SCOPE
            )
        
        return gspread.authorize(credentials)
    
    except Exception as e:
        st.error(f"❌ Ошибка подключения к Google Sheets: {e}")
        st.info("""
        🔧 **Решение проблемы:**
        1. Для локального теста: положите файл `credentials.json` в папку проекта
        2. Для Streamlit Cloud: добавьте credentials в Secrets
        3. Убедитесь, что дали доступ сервисному аккаунту к таблице
        """)
        return None

def init_google_sheet():
    """Инициализация Google таблицы (создаёт, если нет)"""
    try:
        client = get_gsheet_client()
        if not client:
            return False
        
        # Открываем таблицу
        spreadsheet = client.open_by_key(SPREADSHEET_ID)
        
        # Проверяем, есть ли нужный лист
        try:
            sheet = spreadsheet.worksheet(SHEET_NAME)
        except:
            # Создаём новый лист
            sheet = spreadsheet.add_worksheet(title=SHEET_NAME, rows=1000, cols=20)
            
            # Создаём заголовки
            headers = [
                "username", "password_hash", "email", "created_at", 
                "last_login", "role", "tests_completed", 
                "correct_answers", "total_questions"
            ]
            sheet.append_row(headers)
        
        return True
    
    except Exception as e:
        st.error(f"❌ Ошибка инициализации таблицы: {e}")
        return False

# ==================== ОСНОВНЫЕ ФУНКЦИИ АУТЕНТИФИКАЦИИ ====================

def hash_password(password):
    """Хеширование пароля для безопасного хранения"""
    return hashlib.sha256(password.encode()).hexdigest()

def load_users():
    """Загрузка всех пользователей из Google Sheets"""
    try:
        client = get_gsheet_client()
        if not client:
            return {}
        
        spreadsheet = client.open_by_key(SPREADSHEET_ID)
        sheet = spreadsheet.worksheet(SHEET_NAME)
        
        # Получаем все данные
        records = sheet.get_all_records()
        
        users = {}
        for record in records:
            username = record.get('username', '')
            if username:  # Проверяем, что username не пустой
                users[username] = {
                    "password_hash": record.get('password_hash', ''),
                    "email": record.get('email', ''),
                    "created_at": record.get('created_at', ''),
                    "last_login": record.get('last_login', ''),
                    "role": record.get('role', 'student'),
                    "stats": {
                        "tests_completed": int(record.get('tests_completed', 0)),
                        "correct_answers": int(record.get('correct_answers', 0)),
                        "total_questions": int(record.get('total_questions', 0))
                    }
                }
        
        return users
    
    except Exception as e:
        st.error(f"❌ Ошибка загрузки пользователей: {e}")
        return {}

def save_user(username, user_data):
    """Сохранение или обновление пользователя в Google Sheets"""
    try:
        client = get_gsheet_client()
        if not client:
            return False
        
        spreadsheet = client.open_by_key(SPREADSHEET_ID)
        sheet = spreadsheet.worksheet(SHEET_NAME)
        
        # Получаем все данные для поиска пользователя
        records = sheet.get_all_records()
        user_found = False
        row_index = None
        
        # Ищем пользователя
        for i, record in enumerate(records, start=2):  # start=2 потому что строка 1 - заголовки
            if record.get('username') == username:
                user_found = True
                row_index = i
                break
        
        # Подготавливаем данные для записи
        row_data = [
            username,
            user_data.get("password_hash", ""),
            user_data.get("email", ""),
            user_data.get("created_at", ""),
            user_data.get("last_login", ""),
            user_data.get("role", "student"),
            str(user_data.get("stats", {}).get("tests_completed", 0)),
            str(user_data.get("stats", {}).get("correct_answers", 0)),
            str(user_data.get("stats", {}).get("total_questions", 0))
        ]
        
        if user_found and row_index:
            # Обновляем существующего пользователя
            sheet.update(f"A{row_index}:I{row_index}", [row_data])
        else:
            # Добавляем нового пользователя
            sheet.append_row(row_data)
        
        return True
    
    except Exception as e:
        st.error(f"❌ Ошибка сохранения пользователя: {e}")
        return False

def register_user(username, password, email=""):
    """Регистрация нового пользователя"""
    # Инициализируем таблицу при первой регистрации
    if not init_google_sheet():
        return False, "Не удалось инициализировать базу данных"
    
    users = load_users()
    
    # Проверки
    if username in users:
        return False, "Пользователь с таким именем уже существует"
    
    if len(username) < 3:
        return False, "Имя пользователя должно содержать минимум 3 символа"
    
    if len(password) < 6:
        return False, "Пароль должен содержать минимум 6 символов"
    
    # Создаём запись пользователя
    user_data = {
        "password_hash": hash_password(password),
        "email": email,
        "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "last_login": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "role": "student",
        "stats": {
            "tests_completed": 0,
            "correct_answers": 0,
            "total_questions": 0
        }
    }
    
    # Сохраняем в Google Sheets
    if save_user(username, user_data):
        return True, "Регистрация успешна!"
    else:
        return False, "Ошибка при сохранении пользователя"

def login_user(username, password):
    """Авторизация пользователя"""
    users = load_users()
    
    if username not in users:
        return False, "Пользователь не найден"
    
    if users[username]["password_hash"] != hash_password(password):
        return False, "Неверный пароль"
    
    # Обновляем время последнего входа
    users[username]["last_login"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    save_user(username, users[username])
    
    return True, "Авторизация успешна"

def get_user_stats(username):
    """Получение статистики пользователя"""
    users = load_users()
    if username in users:
        return users[username]["stats"]
    return None

def update_user_stats(username, correct_answers, total_questions):
    """Обновление статистики пользователя"""
    users = load_users()
    if username in users:
        users[username]["stats"]["tests_completed"] += 1
        users[username]["stats"]["correct_answers"] += correct_answers
        users[username]["stats"]["total_questions"] += total_questions
        save_user(username, users[username])

# ==================== ИНТЕРФЕЙСНЫЕ ФУНКЦИИ ====================

def show_login_page():
    """Отображение страницы входа/регистрации"""
    st.title("🔐 Химический справочник")
    st.markdown("### Войдите или зарегистрируйтесь")
    
    # Предупреждение о Google Sheets
    with st.expander("ℹ️ Информация о системе", expanded=False):
        st.info("""
        **📊 Данные хранятся в Google Таблице**
        
        Ваша статистика и профиль сохраняются между сессиями.
        Для работы системы требуется подключение к интернету.
        
        **Тестовый аккаунт:** demo / demo
        """)
    
    tab1, tab2, tab3 = st.tabs(["📝 Войти", "✨ Зарегистрироваться", "👤 Гость"])
    
    with tab1:
        st.subheader("Вход в аккаунт")
        login_username = st.text_input("Имя пользователя", key="login_user")
        login_password = st.text_input("Пароль", type="password", key="login_pass")
        
        # Тестовый аккаунт
        if st.button("🧪 Быстрый вход (demo/demo)", use_container_width=True):
            login_username = "demo"
            login_password = "demo"
        
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            if st.button("🚪 Войти", use_container_width=True):
                if login_username and login_password:
                    success, message = login_user(login_username, login_password)
                    if success:
                        st.session_state["logged_in"] = True
                        st.session_state["username"] = login_username
                        st.session_state["user_role"] = load_users().get(login_username, {}).get("role", "student")
                        st.success(message)
                        st.rerun()
                    else:
                        st.error(message)
                else:
                    st.warning("Заполните все поля")
    
    with tab2:
        st.subheader("Создание аккаунта")
        reg_username = st.text_input("Имя пользователя", key="reg_user")
        reg_email = st.text_input("Email (необязательно)", key="reg_email")
        reg_password = st.text_input("Пароль", type="password", key="reg_pass")
        reg_password_confirm = st.text_input("Подтвердите пароль", type="password", key="reg_pass_confirm")
        
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            if st.button("📋 Зарегистрироваться", use_container_width=True):
                if reg_username and reg_password:
                    if reg_password == reg_password_confirm:
                        success, message = register_user(reg_username, reg_password, reg_email)
                        if success:
                            st.success(message)
                            st.info("Теперь войдите в свой аккаунт")
                        else:
                            st.error(message)
                    else:
                        st.error("Пароли не совпадают")
                else:
                    st.warning("Заполните обязательные поля")
    
    with tab3:
        st.subheader("Вход как гость")
        st.info("""
        Вы можете использовать приложение без регистрации.
        Однако статистика не будет сохраняться.
        """)
        
        if st.button("🎮 Продолжить как гость", use_container_width=True):
            st.session_state["logged_in"] = True
            st.session_state["username"] = "Гость"
            st.session_state["user_role"] = "guest"
            st.rerun()
    
    st.markdown("---")
    st.caption("""
    *Регистрация позволяет сохранять вашу статистику и прогресс в обучении.*
    *Все пароли надежно хешируются и хранятся в зашифрованном виде.*
    """)

def show_user_profile():
    """Отображение профиля пользователя в сайдбаре"""
    if "username" not in st.session_state:
        return
    
    with st.sidebar:
        st.markdown("---")
        st.subheader(f"👤 {st.session_state['username']}")
        
        if st.session_state["username"] != "Гость" and st.session_state["username"] != "demo":
            users = load_users()
            user_data = users.get(st.session_state["username"], {})
            stats = user_data.get("stats", {})
            
            if user_data:
                st.caption(f"Роль: {user_data.get('role', 'student')}")
                if user_data.get('created_at'):
                    st.caption(f"Зарегистрирован: {user_data['created_at'].split()[0]}")
                
                st.markdown("**📊 Статистика:**")
                if stats["total_questions"] > 0:
                    percentage = (stats["correct_answers"] / stats["total_questions"]) * 100
                    st.metric("Правильных ответов", f"{stats['correct_answers']}/{stats['total_questions']}")
                    st.metric("Успеваемость", f"{percentage:.1f}%")
                    st.metric("Тестов пройдено", stats["tests_completed"])
                else:
                    st.info("Статистика пока недоступна")
            else:
                st.info("Данные профиля загружаются...")
        
        elif st.session_state["username"] == "demo":
            st.warning("🧪 **Демо-режим**")
            st.info("Статистика не сохраняется")
        
        if st.button("🚪 Выйти"):
            for key in ["logged_in", "username", "user_role"]:
                if key in st.session_state:
                    del st.session_state[key]
            st.rerun()

# ==================== ИНИЦИАЛИЗАЦИЯ ДЕМО-ПОЛЬЗОВАТЕЛЯ ====================

def init_demo_user():
    """Создаёт демо-пользователя при первом запуске"""
    users = load_users()
    if "demo" not in users:
        demo_data = {
            "password_hash": hash_password("demo"),
            "email": "demo@chemistry-app.com",
            "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "last_login": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "role": "demo",
            "stats": {
                "tests_completed": 5,
                "correct_answers": 18,
                "total_questions": 25
            }
        }
        save_user("demo", demo_data)

# Инициализируем демо-пользователя при импорте модуля
init_demo_user()
