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
            google_sheet_handler.download_db()
            db = pd.read_excel(db_file, sheet_name=None)
            if 'Players' not in db:
                db['Players'] = pd.DataFrame(columns=['id', 'name', 'rating'])
                with pd.ExcelWriter(db_file, engine='xlsxwriter') as writer:
                    db['Players'].to_excel(writer, sheet_name='Players', index=False)
   
            if 'Games' not in db:
                db['Games'] = pd.DataFrame(columns=['match_id', 'winner_id', 'loser_id', 'datetime'])
                with pd.ExcelWriter(db_file, engine='xlsxwriter') as writer:
                        db['Games'].to_excel(writer, sheet_name='Games', index=False)
                                                
    return players, matches

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