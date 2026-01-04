# auth_system.py
import streamlit as st
import json
import hashlib
import os
from datetime import datetime

# Путь к файлу с пользователями
USERS_FILE = "users_info.json"

def load_users():
    """Загрузка данных пользователей из JSON файла"""
    if os.path.exists(USERS_FILE):
        try:
            with open(USERS_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return {}
    return {}

def save_users(users_data):
    """Сохранение данных пользователей в JSON файл"""
    with open(USERS_FILE, 'w', encoding='utf-8') as f:
        json.dump(users_data, f, ensure_ascii=False, indent=2)

def hash_password(password):
    """Хеширование пароля"""
    return hashlib.sha256(password.encode()).hexdigest()

def register_user(username, password, email=""):
    """Регистрация нового пользователя"""
    users = load_users()
    
    if username in users:
        return False, "Пользователь с таким именем уже существует"
    
    if len(username) < 3:
        return False, "Имя пользователя должно содержать минимум 3 символа"
    
    if len(password) < 6:
        return False, "Пароль должен содержать минимум 6 символов"
    
    users[username] = {
        "password_hash": hash_password(password),
        "email": email,
        "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "last_login": None,
        "role": "student",  # student, teacher, admin
        "preferences": {
            "theme": "light",
            "test_level": "medium",
            "show_hints": True
        },
        "stats": {
            "tests_completed": 0,
            "correct_answers": 0,
            "total_questions": 0
        }
    }
    
    save_users(users)
    return True, "Регистрация успешна!"

def login_user(username, password):
    """Авторизация пользователя"""
    users = load_users()
    
    if username not in users:
        return False, "Пользователь не найден"
    
    if users[username]["password_hash"] != hash_password(password):
        return False, "Неверный пароль"
    
    # Обновляем время последнего входа
    users[username]["last_login"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    save_users(users)
    
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
        save_users(users)

def show_login_page():
    """Отображение страницы входа/регистрации"""
    st.title("🔐 Химический справочник")
    st.markdown("### Войдите или зарегистрируйтесь")
    
    tab1, tab2, tab3 = st.tabs(["📝 Войти", "✨ Зарегистрироваться", "👤 Гость"])
    
    with tab1:
        st.subheader("Вход в аккаунт")
        login_username = st.text_input("Имя пользователя", key="login_user")
        login_password = st.text_input("Пароль", type="password", key="login_pass")
        
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
    """Отображение профиля пользователя"""
    if "username" not in st.session_state:
        return
    
    with st.sidebar:
        st.markdown("---")
        st.subheader(f"👤 {st.session_state['username']}")
        
        if st.session_state["username"] != "Гость":
            users = load_users()
            user_data = users.get(st.session_state["username"], {})
            stats = user_data.get("stats", {})
            
            st.caption(f"Роль: {user_data.get('role', 'student')}")
            st.caption(f"Зарегистрирован: {user_data.get('created_at', 'Неизвестно')}")
            
            st.markdown("**📊 Статистика:**")
            if stats["total_questions"] > 0:
                percentage = (stats["correct_answers"] / stats["total_questions"]) * 100
                st.metric("Правильных ответов", f"{stats['correct_answers']}/{stats['total_questions']}")
                st.metric("Успеваемость", f"{percentage:.1f}%")
                st.metric("Тестов пройдено", stats["tests_completed"])
            else:
                st.info("Статистика пока недоступна")
        
        if st.button("🚪 Выйти"):
            for key in ["logged_in", "username", "user_role"]:
                if key in st.session_state:
                    del st.session_state[key]
            st.rerun()
