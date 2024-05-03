import pandas as pd
import os
import google_sheet_handler

def save_data(players, matches, db_file):
    if not os.path.isdir('data'):
        os.mkdir('data')
    with pd.ExcelWriter('./data/' + db_file, engine='xlsxwriter') as writer:
        players.to_excel(writer, sheet_name='Players', index=False)
        matches.to_excel(writer, sheet_name='Games', index=False)

    google_sheet_handler.upload_db()