import pandas as pd
import os
from datetime import datetime

def load_data():
    players_file = 'data/players.csv'
    matches_file = 'data/matches.csv'
    
    if os.path.isfile(players_file) and os.path.isfile(matches_file):
        players = pd.read_csv(players_file)
        matches = pd.read_csv(matches_file)
    else:
        players = pd.DataFrame(columns=['id', 'name', 'rating'])
        matches = pd.DataFrame(columns=['match_id', 'winner_id', 'loser_id', 'datetime'])
    
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