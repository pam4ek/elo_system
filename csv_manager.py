import pandas as pd
import os

def save_data(players, matches, db_file):
    directory = os.path.dirname(db_file)
    if directory and not os.path.exists(directory):
        os.makedirs(directory)
    with pd.ExcelWriter(db_file, engine='xlsxwriter') as writer:
        players.to_excel(writer, sheet_name='Players', index=False)
        matches.to_excel(writer, sheet_name='Games', index=False)
