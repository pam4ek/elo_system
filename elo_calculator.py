import warnings
warnings.simplefilter(action='ignore', category=FutureWarning)
import pandas as pd

def calculate_elo(players, matches, k_factor=32):
    # Инициализируем рейтинг для всех игроков
    players['rating'] = 1000
    
    # Пересчитываем рейтинг для каждого матча
    for index, match in matches.iterrows():
        winner_id = match['winner_id']
        loser_id = match['loser_id']
        
        winner_rating = players.loc[players['id'] == winner_id, 'rating'].values[0]
        loser_rating = players.loc[players['id'] == loser_id, 'rating'].values[0]
        
        expected_winner = 1 / (1 + 10 ** ((loser_rating - winner_rating) / 400))
        expected_loser = 1 / (1 + 10 ** ((winner_rating - loser_rating) / 400))
        
        players.loc[players['id'] == winner_id, 'rating'] = winner_rating + round(k_factor * (1 - expected_winner))
        players.loc[players['id'] == loser_id, 'rating'] = loser_rating + round(k_factor * (0 - expected_loser))
    
    return players

def calculate_elo_with_history(players, matches, k_factor=32):
    # Инициализируем рейтинг для всех игроков
    players['rating'] = 1000
    # Словарь для хранения истории рейтинга по каждому игроку
    player_history = {player_id: pd.DataFrame(columns=['match_id', 'opponent', 'result', 'rating_change', 'rating_new', 'datetime']) for player_id in players['id']}
    
    # Пересчитываем рейтинг для каждого матча
    for index, match in matches.iterrows():
        winner_id = match['winner_id']
        loser_id = match['loser_id']
        
        winner_rating = players.loc[players['id'] == winner_id, 'rating'].values[0]
        loser_rating = players.loc[players['id'] == loser_id, 'rating'].values[0]
        
        expected_winner = 1 / (1 + 10 ** ((loser_rating - winner_rating) / 400))
        expected_loser = 1 / (1 + 10 ** ((winner_rating - loser_rating) / 400))
        
        # Изменение рейтинга для победителя и проигравшего
        rating_change_winner = round(k_factor * (1 - expected_winner))
        rating_change_loser = round(k_factor * (0 - expected_loser))
        
        # Обновляем рейтинг для победителя и проигравшего
        players.loc[players['id'] == winner_id, 'rating'] += rating_change_winner
        players.loc[players['id'] == loser_id, 'rating'] += rating_change_loser
        
        # Добавляем запись в историю рейтинга для победителя и проигравшего
        new_row_winner = pd.DataFrame({
            'match_id': [match['match_id']],
            'opponent': [players.loc[players['id'] == loser_id, 'name'].values[0]],
            'result': ['Победа'],
            'rating_change': [rating_change_winner],
            'rating_new': [players.loc[players['id'] == winner_id, 'rating'].values[0]],
            'datetime': [match['datetime']]
        })
        player_history[winner_id] = pd.concat([player_history[winner_id], new_row_winner], ignore_index=True)
        
        new_row_loser = pd.DataFrame({
            'match_id': [match['match_id']],
            'opponent': [players.loc[players['id'] == winner_id, 'name'].values[0]],
            'result': ['Поражение'],
            'rating_change': [rating_change_loser],
            'rating_new': [players.loc[players['id'] == loser_id, 'rating'].values[0]],
            'datetime': [match['datetime']]
        })
        player_history[loser_id] = pd.concat([player_history[loser_id], new_row_loser], ignore_index=True)
    
    return players, player_history