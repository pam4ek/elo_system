import pandas as pd
import os

def save_data(players, matches, players_file, matches_file):
    if not os.path.isdir('data'):
        os.mkdir('data')
    players.to_csv('data/' + players_file, index=False)
    matches.to_csv('data/' + matches_file, index=False)