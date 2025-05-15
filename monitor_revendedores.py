import asyncio
import os
import json
import requests
from datetime import datetime
from dotenv import load_dotenv
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
from email_utils import enviar_email

load_dotenv()

SPREADSHEET_ID = os.getenv("SPREADSHEET_ID")
SHEET_NAME = "Revendedores"
CREDENTIALS_FILE = os.getenv("CREDENTIALS_FILE")
BOT_TOKEN = os.getenv("API_TOKEN")
json_credentials = os.getenv("GOOGLE_CREDENTIALS_JSON")

if json_credentials:
    creds_dict = json.loads(json_credentials)
    creds = Credentials.from_service_account_info(creds_dict)
else:
    creds = Credentials.from_service_account_file(CREDENTIALS_FILE)

sheet = build('sheets', 'v4', credentials=creds)

def idx(headers, nome):
    return headers.index(nome)

def enviar_telegram(chat_id, texto):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": texto,
        "parse_mode": "HTML"
    }
    try:
        r = requests.post(url, data=payload)
        if r.status_code == 200:
            print(f"📨 Telegram enviado para {chat_id}")
        else:
            print(f"⚠️ Falha Telegram: {r.status_code} - {r.text}")
    except Exception as e:
        print(f"❌ Erro ao enviar Telegram: {e}")

async def monitor_resposta_revendedores():
    print("📡 A iniciar monitor de revendedores...")

    while True:
        try:
            result = sheet.spreadsheets().values().get(
                spreadsheetId=SPREADSHEET_ID, range=SHEET_NAME).execute()
            valores = result.get('values', [])
            headers = valores[0]
            rows = valores[1:]

            for row_idx, row in enumerate(rows, start=2):
                row += [""] * (len(headers) - len(row))
                ativar = row[idx(headers, "Ativar saldo")].strip().lower()
                email = row[idx(headers, "Email")]
                nome = row[idx(headers, "Nome de utilizador")]
                telegram_id = row[idx(headers, "Telegram ID")]

                if ativar == "sim":
                    corpo = f"""
Olá {nome},

Confirmamos o teu carregamento. O saldo será atualizado manualmente nas próximas horas.

Obrigado por continuares connosco.

Com os melhores cumprimentos,  
A equipa 4US
"""
                    enviar_email(
                        destinatario=email,
                        assunto="✅ Confirmação de saldo – 4US",
                        corpo=corpo,
                        username=nome,
                        motivo="Resposta automática (Revendedor)"
                    )

                    if telegram_id.strip():
                        mensagem = (
                            f"✅ <b>Confirmação de saldo</b>\n\n"
                            f"Olá {nome}, confirmamos o teu carregamento.\n"
                            f"O saldo será atualizado manualmente nas próximas horas.\n\n"
                            f"Obrigado por continuares connosco. 💙"
                        )
                        enviar_telegram(telegram_id, mensagem)

                    # Marcar como "ENVIADO"
                    col_idx = idx(headers, "Ativar saldo")
                    sheet.spreadsheets().values().update(
                        spreadsheetId=SPREADSHEET_ID,
                        range=f"{SHEET_NAME}!{chr(65+col_idx)}{row_idx}",
                        valueInputOption="RAW",
                        body={"values": [["ENVIADO"]]}
                    ).execute()

                    print(f"✅ Mensagem enviada a {nome}")

            await asyncio.sleep(60)

        except Exception as e:
            print(f"❌ Erro no monitor de revendedores: {e}")
            await asyncio.sleep(60)
