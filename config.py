# config.py
import os
import json
from dotenv import load_dotenv
from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build

# Carrega as variáveis do .env
load_dotenv()

API_TOKEN = os.getenv("API_TOKEN")
SPREADSHEET_ID = os.getenv("SPREADSHEET_ID")
CREDENTIALS_FILE = os.getenv("CREDENTIALS_FILE", "credenciais_bot.json")
PASTA_COMPROVATIVOS_ID = os.getenv("PASTA_COMPROVATIVOS_ID")
SHEET_CLIENTES = os.getenv("SHEET_CLIENTES", "Tabela de Clientes 2")
SHEET_PEDIDOS = SHEET_CLIENTES

# Inicializar bot com parse_mode
bot = Bot(token=API_TOKEN, parse_mode=ParseMode.HTML)
dp = Dispatcher()
user_data = {}

# Autenticação Google via variável JSON ou ficheiro
json_credentials = os.getenv("GOOGLE_CREDENTIALS_JSON")
if json_credentials:
    creds_dict = json.loads(json_credentials)
    creds = Credentials.from_service_account_info(creds_dict, scopes=[
        'https://www.googleapis.com/auth/spreadsheets',
        'https://www.googleapis.com/auth/drive'
    ])
else:
    creds = Credentials.from_service_account_file(CREDENTIALS_FILE, scopes=[
        'https://www.googleapis.com/auth/spreadsheets',
        'https://www.googleapis.com/auth/drive'
    ])

sheet_service = build("sheets", "v4", credentials=creds)
drive_service = build("drive", "v3", credentials=creds)

mapa_colunas = {
    "username": "A",
    "password": "B",
    "email": "C",
    "ref_extra": "D",
    "vpn": "F",
    "conta_vpn": "G",
    "plano_novo": "K",
    "total": "L",
    "data_hora": "M",
    "estado_do_pedido": "N",
    "comprovativo": "O",
    "renovada_no_painel_e_tabela_de_clientes": "P",
    "telegram_id": "Q"
}