import os
import json
import logging
import io
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload, MediaIoBaseDownload
import streamlit as st

logging.basicConfig(level=logging.INFO)

def create_credentials():
    """
    Создание учетных данных для доступа к Google API.
    """
    cred_path = './data/credentials.json'
    if os.path.exists(cred_path):
        logging.info("Файл учетных данных уже существует.")
        return
    
    cred = {
        'type': st.secrets["type"],
        'project_id': st.secrets["project_id"],
        'private_key_id': st.secrets["private_key_id"],
        'private_key': st.secrets["private_key"],
        'client_email': st.secrets["client_email"],
        'client_id': st.secrets["client_id"],
        'auth_uri': st.secrets["auth_uri"],
        'token_uri': st.secrets["token_uri"],
        'auth_provider_x509_cert_url': st.secrets["auth_provider_x509_cert_url"],
        'client_x509_cert_url': st.secrets["client_x509_cert_url"],
        'universe_domain': st.secrets["universe_domain"]
    }

    if not os.path.isdir('data'):
        os.mkdir('data')
    
    with open(cred_path, 'w') as file:
        json.dump(cred, file)
    
    logging.info("Файл учетных данных создан.")
    return

create_credentials()

credentials = service_account.Credentials.from_service_account_file(
    './data/credentials.json',
    scopes=['https://www.googleapis.com/auth/drive']
)

def download_db():
    """
    Скачивание базы данных из Google Drive.
    """
    drive_service = build('drive', 'v3', credentials=credentials)
    file_name = 'EloRatingDB'
    query = f"name='{file_name}' and mimeType='application/vnd.google-apps.spreadsheet'"
    results = drive_service.files().list(q=query, fields='files(id)').execute()
    items = results.get('files', [])

    if items:
        file_id = items[0]['id']
        request = drive_service.files().export_media(
            fileId=file_id,
            mimeType='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
        filename = './data/EloRatingDB.xlsx'
        fh = io.FileIO(filename, 'wb')
        downloader = MediaIoBaseDownload(fh, request)
        done = False
        while not done:
            status, done = downloader.next_chunk()
            logging.info(f"Download {int(status.progress() * 100)}%.")

def upload_db():
    """
    Загрузка базы данных на Google Drive.
    """
    drive_service = build('drive', 'v3', credentials=credentials)
    file_path = './data/EloRatingDB.xlsx'
    file_name = 'EloRatingDB'
    mime_type = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    
    query = f"name='{file_name}' and mimeType='application/vnd.google-apps.spreadsheet'"
    results = drive_service.files().list(q=query, fields='files(id)').execute()
    items = results.get('files', [])
    
    if items:
        file_id = items[0]['id']
        media = MediaFileUpload(file_path, mimetype=mime_type, resumable=True)
        file = drive_service.files().update(fileId=file_id, media_body=media).execute()
        logging.info("База данных успешно загружена на Google Drive.")
