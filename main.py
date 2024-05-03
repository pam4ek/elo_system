import streamlit as st
import hashlib
from data_handler import load_data, add_player, add_match
from elo_calculator import calculate_elo, calculate_elo_with_history
from visualization import display_ratings, display_match_history
from csv_manager import save_data


login = '21232f297a57a5a743894a0e4a801fc3'
password = '0192023a7bbd73250516f069df18b500'
db_file = 'EloRatingDB.xlsx'

google_api = "AIzaSyAMQq7jUNpkBc2PtQWajZevt5d8huft_Bk"


# Load data
players, matches = load_data()

# User interface to add players and matches
st.title('Elo Rating System')

# Create tabs
tab_ratings, tab_personal_rating, tab_match_history, tab_add_match, tab_add_player, tab_admin = st.tabs(["Рейтинг", "Персональные результаты", "История матчей", "Добавить матч", "Добавить игрока", "Админка"])

# Rating tab
with tab_ratings:
    if not players.empty:
        display_ratings(players)
        # Добавление кнопки для обновления рейтинга
        if st.button('Обновить рейтинг'):
            players = calculate_elo(players, matches)
            save_data(players, matches, db_file)
            # st.success("Рейтинг обновлен.")
            # Обновляем DataFrame players в интерфейсе Streamlit
            #tab_ratings.dataframe(players[['name', 'rating']].sort_values('rating', ascending=False), width=500)
    else:
        st.write("Нет данных о рейтинге.")
        if st.button('Обновить рейтинг'):
            pass

# Personal Results tab
with tab_personal_rating:
    if not players.empty:
        players, players_history = calculate_elo_with_history(players, matches)
        selected_player = st.selectbox('Выберите игрока:', players['name'])
        if st.button('Получить результаты'):
            player_id = players.loc[players['name'] == selected_player, 'id'].values[0]
            player_matches_with_names = players_history[player_id]
            st.dataframe(player_matches_with_names)
    else:
        st.write("Нет игроков для выбора.")

# Match History tab
with tab_match_history:
    if not matches.empty:
        # Добавляем столбцы "id матча", "игрок 1", "игрок 2", "результат матча" и "время матча"
        display_match_history(matches, players)        
        # Добавление кнопки для обновления истории матчей
        if st.button('Обновить историю матчей'):
            pass
            # Здесь можно добавить логику для обновления истории матчей, если это необходимо
            # st.success("История матчей обновлена.")
    else:
        st.write("История матчей пуста.")
        if st.button('Обновить историю матчей'):
            pass

# Add Player tab
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
                save_data(players, matches, db_file)
                st.success("Игрок успешно добавлен.")
                # Обновляем DataFrame players в интерфейсе Streamlit
                #tab_ratings.dataframe(players[['name', 'rating']].sort_values('rating', ascending=False), width=500)

# Add Match tab
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
                    if winner_id == loser_id:
                        st.error("Игрок победитель и игрок проигравший не могут быть одним и тем же игроком.")
                    else:
                        matches = add_match(matches, winner_id, loser_id)
                        save_data(players, matches, db_file)
                        st.success("Матч успешно добавлен.")
                        # Обновляем DataFrame matches в интерфейсе Streamlit
                        #tab_match_history.dataframe(display_match_history(matches, players), width=1000)

def check_login(login_text, password_text):
    if hashlib.md5(login_text.encode()).hexdigest() == login and hashlib.md5(password_text.encode()).hexdigest() == password:
        return True
    return False

# Инициализируем состояние входа
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
            # Изменяем историю матчей
            players, matches = load_data()
            st.subheader('Игроки')
            players_admin = st.data_editor(players, num_rows='dynamic')
            st.subheader('История матчей')
            matches_admin = st.data_editor(matches, num_rows='dynamic')
            edit = st.form_submit_button('Изменить')
            if edit:
                try:
                    save_data(players_admin, matches_admin, db_file)
                    st.success("Изменения сохранены.")
                    players = players_admin
                    matches = matches_admin
                except:
                    st.error("Не удалось сохранить изменения.")
                                                
        # Добавляем кнопку для выхода
        if st.button('Выйти'):
            st.session_state.login_status = False
            st.info("Вы вышли из системы.")
                                                
                                

# Recalculate Elo ratings after adding matches
if not matches.empty:
    players = calculate_elo(players, matches)

# Save data
save_data(players, matches, db_file)