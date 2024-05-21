import hashlib
import streamlit as st
from data_handler import DB_FILE, get_current_sprint_start, get_matches_for_current_sprint, load_data, add_player, add_match, sinchronize_data, sync_data
from elo_calculator import calculate_elo, calculate_elo_with_history
from google_sheet_handler import upload_db
from visualization import display_ratings, display_match_history
from csv_manager import save_data
import plotly.express as px
import pandas as pd
import json
import os
import datetime

login = st.secrets['admin_login']
password = st.secrets['admin_pass']


# Инициализация и проверка необходимости синхронизации данных
sync_data()

# Загрузка данных
players, matches = load_data()

# Пользовательский интерфейс
st.title('Elo Rating System')

# Создание вкладок
tab_ratings, tab_sprint_rating, tab_personal_rating, tab_match_history, tab_add_match, tab_add_player, tab_admin = st.tabs(
    ["Рейтинг", "Рейтинг спринта", "Персональные результаты", "История матчей", "Добавить матч", "Добавить игрока", "Админка"])

# Вкладка рейтинга
with tab_ratings:
    if not players.empty:
        display_ratings(players)
        if st.button('Обновить рейтинг'):
            players = calculate_elo(players, matches)
            save_data(players, matches, DB_FILE)
            # sinchronize_data(players, matches)
    else:
        st.write("Нет данных о рейтинге.")

# Вкладка рейтинга спринта
with tab_sprint_rating:
    st.header('Рейтинг текущего спринта')
    
    current_sprint_start = get_current_sprint_start()
    st.write(f"Текущий спринт начался {current_sprint_start} и закончится {current_sprint_start + datetime.timedelta(weeks=2)}.")
    
    sprint_matches = get_matches_for_current_sprint(matches)
    if not sprint_matches.empty:
        st.write("Матчи текущего спринта:")
        display_match_history(sprint_matches, players)
        
        sprint_players = players.copy()
        sprint_players = calculate_elo(sprint_players, sprint_matches)
        
        st.write("Рейтинг игроков в текущем спринте:")
        display_ratings(sprint_players)
    else:
        st.write("Нет матчей в текущем спринте.")
    
    # Отображение победителей предыдущих спринтов
    # st.header('Победители предыдущих спринтов')
    # Логика для получения и отображения победителей предыдущих спринтов
    # Например, можно хранить победителей в отдельном файле или базе данных

# Вкладка персональных результатов
with tab_personal_rating:
    if not players.empty:
        players, players_history = calculate_elo_with_history(players, matches)
        selected_player = st.selectbox('Выберите игрока:', players['name'])
        if st.button('Получить результаты'):
            player_id = players.loc[players['name'] == selected_player, 'id'].values[0]
            player_matches_with_names = players_history[player_id]
            st.dataframe(player_matches_with_names)
            
            # График изменений рейтинга
            player_matches_with_names['datetime'] = pd.to_datetime(player_matches_with_names['datetime'])
            fig = px.line(player_matches_with_names, x='datetime', y='rating_new', title='История изменений рейтинга')
            st.plotly_chart(fig)
            
            # Расчет винрейта
            total_matches = len(player_matches_with_names)
            wins = len(player_matches_with_names[player_matches_with_names['result'] == 'Победа'])
            winrate = (wins / total_matches) * 100 if total_matches > 0 else 0
            st.metric(label='Общий винрейт', value=f'{winrate:.2f}%')
    else:
        st.write("Нет игроков для выбора.")

# Вкладка истории матчей
with tab_match_history:
    if not matches.empty:
        display_match_history(matches, players)
    else:
        st.write("История матчей пуста.")

# Вкладка добавления игрока
with tab_add_player:
    st.header('Добавить игрока')
    with st.form('add_player'):
        new_player_name = st.text_input('Имя игрока')
        submitted = st.form_submit_button('Добавить игрока')
        if submitted:
            if not new_player_name.strip():
                st.error("Имя игрока не может быть пустым.")
            else:
                players = add_player(players, new_player_name)
                save_data(players, matches, DB_FILE)
                st.success("Игрок успешно добавлен.")

# Вкладка добавления матча
with tab_add_match:
    st.header('Добавить матч')
    with st.form('add_match'):
        if players.empty:
            st.error("Нет игроков для создания матча.")
        else:
            player1_name = st.selectbox('Игрок 1', players['name'])
            player2_name = st.selectbox('Игрок 2', players['name'])
            winner = st.radio('Победитель:', ['Игрок 1', 'Игрок 2'])
            submitted = st.form_submit_button('Добавить матч')
            if submitted:
                if player1_name == player2_name:
                    st.error("Игрок 1 и Игрок 2 не могут быть одним и тем же игроком.")
                else:
                    winner_id = players[players['name'] == player1_name]['id'].values[0] if winner == 'Игрок 1' else players[players['name'] == player2_name]['id'].values[0]
                    loser_id = players[players['name'] == player2_name]['id'].values[0] if winner == 'Игрок 1' else players[players['name'] == player1_name]['id'].values[0]
                    matches = add_match(matches, winner_id, loser_id)
                    save_data(players, matches, DB_FILE)
                    st.success("Матч успешно добавлен.")
                    # Обновляем рейтинги после добавления матча
                    players = calculate_elo(players, matches)
                    save_data(players, matches, DB_FILE)

def check_login(login_text, password_text):
    if hashlib.md5(login_text.encode()).hexdigest() == login and hashlib.md5(password_text.encode()).hexdigest() == password:
        return True
    return False

# Инициализация состояния входа
if 'login_status' not in st.session_state:
    st.session_state.login_status = False

with tab_admin:
    st.header('Админка')
    if not st.session_state.login_status:
        with st.form('admin'):
            login_form = st.text_input('Имя пользователя')
            password_form = st.text_input('Пароль')
            submitted = st.form_submit_button('Вход')
            if submitted:
                if check_login(login_form, password_form):
                    st.success("Вход выполнен.")
                    st.session_state.login_status = True
                else:
                    st.error("Неверный логин или пароль.")
    else:
        with st.form('dataedit'):
            players, matches = load_data()
            st.subheader('Игроки')
            players_admin = st.data_editor(players, num_rows='dynamic')
            st.subheader('История матчей')
            matches_admin = st.data_editor(matches, num_rows='dynamic')
            edit = st.form_submit_button('Изменить')
            if edit:
                try:
                    save_data(players_admin, matches_admin, DB_FILE)
                    st.success("Изменения сохранены.")
                    players = players_admin
                    matches = matches_admin
                    upload_db()
                except:
                    st.error("Не удалось сохранить изменения.")
        if st.button('Выйти'):
            st.session_state.login_status = False
            st.info("Вы вышли из системы.")
