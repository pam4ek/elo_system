import streamlit as st
import pandas as pd

def display_ratings(players):
    st.subheader('Рейтинг игроков')
    st.dataframe(players[['name', 'rating']].sort_values('rating', ascending=False))

def display_match_history(matches, players):
    st.subheader('История матчей')
    # Преобразование matches в DataFrame с именами игроков вместо их идентификаторов
    matches_with_names = matches.merge(players[['id', 'name']], left_on='winner_id', right_on='id').drop('id', axis=1)
    matches_with_names = matches_with_names.merge(players[['id', 'name']], left_on='loser_id', right_on='id', suffixes=('_winner', '_loser'))\
        .drop(['id', 'loser_id', 'winner_id'], axis=1)
    st.dataframe(matches_with_names)