from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload, MediaIoBaseDownload

import io

credentials = service_account.Credentials.from_service_account_file('./data/elo-system-422211-922811cf5642.json',
                                                                    scopes=['https://www.googleapis.com/auth/drive'])
# Путь к вашему CSV-файлу
file_name = 'EloRatingDB'

def download_db():
    
    # Подключитесь к Google Drive API
    drive_service = build('drive', 'v3', credentials=credentials)

    # Найдите файл на Google Drive
    query = f"name='{file_name}' and mimeType='application/vnd.google-apps.spreadsheet'"
    results = drive_service.files().list(q=query, fields='files(id)').execute()
    items = results.get('files', [])
    # print(items)
    if items:
        file_id = items[0]['id']
        # print(file_id)
        # # URL для экспорта файла в CSV
        # url = f"https://www.googleapis.com/drive/v3/files/{file_id}/export?mimeType='text/csv'"


        request = drive_service.files().export_media(fileId=file_id,
                                                    mimeType='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        filename = './data/EloRatingDB.xlsx'
        fh = io.FileIO(filename, 'wb')
        downloader = MediaIoBaseDownload(fh, request)
        done = False
        while done is False:
            status, done = downloader.next_chunk()
    #     print ("Download %d%%." % int(status.progress() * 100))
    # else:
    #     print('File not found')
            

def upload_db():
    drive_service = build('drive', 'v3', credentials=credentials)

    file_path = './data/EloRatingDB.xlsx'  # Путь к локальному файлу
    file_name = 'EloRatingDB'  # Имя файла на Google Drive
    mime_type = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    
    # Поиск файла на Google Drive
    query = f"name='{file_name}' and mimeType='application/vnd.google-apps.spreadsheet'"
    results = drive_service.files().list(q=query, fields='files(id)').execute()
    items = results.get('files', [])
    
    if items:
        file_id = items[0]['id']
        # print(f'File ID: {file_id}')
        # Обновление существующего файла
        media = MediaFileUpload(file_path, mimetype=mime_type, resumable=True)
        file = drive_service.files().update(fileId=file_id, media_body=media).execute()
    #     print(f'File ID: {file_id} has been updated.')
    # else:
    #     print('File not found on Google Drive.')

# import pandas as pd
# download_db()  
# db = pd.read_excel('./data/EloRatingDB.xlsx')
# print(db.head())
# db.loc[db.shape[0]] = [1, 2, 3]
# print(db.head())
# db.to_csv('./data/EloRatingDB.xlsx', index=False)
# upload_db()


