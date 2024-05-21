import pandas as pd
import os
from csv_manager import save_data
import google_sheet_handler
import logging
from datetime import datetime, timedelta

logging.basicConfig(level=logging.INFO)

DB_FILE = './data/EloRatingDB.xlsx'
SYNC_TIMESTAMP_FILE = './data/last_sync.txt'

def load_data():
    """
    Загрузка данных игроков и матчей из локального файла базы данных.
    Если данных нет, выполняется синхронизация с Google Sheets.
    """
    if not os.path.exists(DB_FILE):
        logging.warning(f"Файл базы данных {DB_FILE} не найден, выполняется синхронизация.")
        sinchronize_data(None, None)
    
    try:
        players = pd.read_excel(DB_FILE, sheet_name='Players')
        matches = pd.read_excel(DB_FILE, sheet_name='Games')
    except Exception as e:
        logging.error(f"Ошибка при загрузке данных: {e}")
        sinchronize_data(None, None)
        players = pd.read_excel(DB_FILE, sheet_name='Players')
        matches = pd.read_excel(DB_FILE, sheet_name='Games')
    
    return players, matches

def save_last_sync_time():
    """
    Сохранение метки времени последней синхронизации.
    """
    directory = os.path.dirname(SYNC_TIMESTAMP_FILE)
    if directory and not os.path.exists(directory):
        os.makedirs(directory)
    with open(SYNC_TIMESTAMP_FILE, 'w') as f:
        f.write(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

def load_last_sync_time():
    """
    Загрузка метки времени последней синхронизации.
    """
    if os.path.exists(SYNC_TIMESTAMP_FILE):
        with open(SYNC_TIMESTAMP_FILE, 'r') as f:
            return datetime.strptime(f.read().strip(), "%Y-%m-%d %H:%M:%S")
    return None

def is_sync_needed():
    """
    Проверка необходимости синхронизации данных.
    """
    last_sync_time = load_last_sync_time()
    if last_sync_time is None:
        return True
    return datetime.now() - last_sync_time > timedelta(minutes=5)

def sinchronize_data(players, matches):
    """
    Синхронизация данных между локальной базой данных и Google Sheets.
    Если данные отсутствуют, они загружаются из Google Sheets.
    Если данные имеются, они загружаются в Google Sheets.
    """
    if players is None or matches is None:
        logging.info("Загрузка данных из Google Sheets.")
        google_sheet_handler.download_db()
    else:
        logging.info("Выгрузка данных в Google Sheets.")
        google_sheet_handler.upload_db()
    
    save_last_sync_time()

def add_player(players, name):
    """
    Добавление нового игрока.
    """
    new_id = 1 if players.empty else players['id'].max() + 1
    new_player = pd.DataFrame({'id': [new_id], 'name': [name], 'rating': [1000]})
    players = pd.concat([players, new_player], ignore_index=True)
    return players

def add_match(matches, winner_id, loser_id):
    """
    Добавление нового матча.
    """
    new_match_id = 1 if matches.empty else matches['match_id'].max() + 1
    new_match = pd.DataFrame({
        'match_id': [new_match_id],
        'winner_id': [winner_id],
        'loser_id': [loser_id],
        'datetime': [datetime.now().strftime("%Y-%m-%d %H:%M:%S")]
    })
    matches = pd.concat([matches, new_match], ignore_index=True)
    return matches

def merge_data(local_players, local_matches, remote_players, remote_matches):
    """
    Объединение данных локального хранилища и сервера.
    """
    # Объединяем данные игроков
    merged_players = pd.concat([local_players, remote_players]).drop_duplicates(subset='id', keep='last').reset_index(drop=True)

    # Объединяем данные матчей
    merged_matches = pd.concat([local_matches, remote_matches]).drop_duplicates(subset='match_id', keep='last').reset_index(drop=True)

    return merged_players, merged_matches

def sync_data():
    """
    Пассивная синхронизация данных.
    """
    if not is_sync_needed():
        logging.info("Синхронизация не требуется.")
        return

    logging.info("Выполняется синхронизация данных...")
    
    local_players, local_matches = load_data()
    google_sheet_handler.download_db()
    remote_players = pd.read_excel(DB_FILE, sheet_name='Players')
    remote_matches = pd.read_excel(DB_FILE, sheet_name='Games')
    
    if not local_players.empty and not local_matches.empty:
        local_last_update = local_matches['datetime'].max()
        remote_last_update = remote_matches['datetime'].max()
        
        if local_last_update > remote_last_update:
            logging.info("Локальные данные новее, выгружаем на сервер.")
            sinchronize_data(local_players, local_matches)
        else:
            logging.info("Серверные данные новее, загружаем с сервера.")
            players, matches = merge_data(local_players, local_matches, remote_players, remote_matches)
            save_data(players, matches, DB_FILE)
    else:
        logging.info("Нет локальных данных, загружаем с сервера.")
        save_data(remote_players, remote_matches, DB_FILE)
    
    save_last_sync_time()
