import pandas as pd
import os
from datetime import datetime
import google_sheet_handler

def load_data():

    db_file = 'data/EloRatingDB.xlsx'
    
    players = None
    matches = None


    while players is None or matches is None:
        try:
            players = pd.read_excel(db_file, sheet_name='Players')
            matches = pd.read_excel(db_file, sheet_name='Games')
        except:
            sinchronize_data(players, matches)
                                                
    return players, matches


def sinchronize_data(players, matches):
    # Если данных нет, то скачиваем
    # Если данные есть, то загружаем в диск

    if players is None or matches is None:
        google_sheet_handler.download_db()
        # players, matches = load_data()
    else:
        google_sheet_handler.upload_db()
    return





def add_player(players, name):
    if players.empty:
        new_id = 1
    else:
        new_id = players['id'].max() + 1
    new_player = pd.DataFrame({'id': [new_id], 'name': [name], 'rating': [1000]})
    players = pd.concat([players, new_player], ignore_index=True)
    return players

def add_match(matches, winner_id, loser_id):
    if matches.empty:
        new_match_id = 1
    else:
        new_match_id = matches['match_id'].max() + 1
    new_match = pd.DataFrame({'match_id': [new_match_id], 'winner_id': [winner_id], 'loser_id': [loser_id], 'datetime': [datetime.now().strftime("%d-%m-%Y %H:%M:%S")]})
    matches = pd.concat([matches, new_match], ignore_index=True)
    return matches